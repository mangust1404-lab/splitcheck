# SplitCheck — Design Spec

Telegram Mini App for splitting group expenses with receipt scanning.

## Problem Statement

Tricount pain points this app solves:
- **Installation friction** — requires download and install; SplitCheck opens via link in Telegram
- **Sync issues** — Tricount often fails to sync; SplitCheck uses a single backend as source of truth
- **Manual entry** — tedious to type in expenses; SplitCheck scans receipts via LLM Vision and assigns line items to participants

## Primary Use Case

Friends on a trip (3-8 people, multiple days, many small expenses). At the end of the trip, the app calculates optimized settlements — who owes whom and how much.

## Platform & Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue.js 3 + Vite + Tailwind CSS + Telegram Web App SDK |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Receipt OCR | Claude Vision API |
| File Storage | Cloudflare R2 (receipt images) |
| Deploy | Docker (Railway or VPS) |

## Core Features (MVP)

### 1. Groups (Trips)

- Create a group with name and base currency
- Add participants by name (virtual members, no Telegram account required)
- Share invite link — Telegram users who open it auto-join and link to their virtual member or create a new one
- `group_members.user_id` is nullable — virtual participants exist without Telegram binding
- Group statuses: `active` / `archived`
- Archive view for past trips (read-only), reactivation supported

### 2. Expenses

Three split modes:
- **Equal** — total divided equally among selected participants
- **By items** — receipt line items assigned to specific participants
- **Custom amounts** — manually enter each participant's share

#### Custom Amounts — Smart Validation

No hard blocks on save. Instead:
- Live indicator: "Assigned 4,200 of 7,400₸, remaining: 3,200₸"
- Button: "Split remainder equally" — distributes unassigned amount among participants without a share
- If amounts don't add up to total: offer "Adjust proportionally" or "Add difference to last participant"
- Save always allowed; show warning (not block) if discrepancy exists

### 3. Receipt Scanning

**Flow:**
1. User taps "Scan receipt" — camera opens
2. Photo uploaded to backend as `multipart/form-data`
3. Backend saves image to Cloudflare R2
4. Image sent to Claude Vision API with structured prompt
5. Returns JSON: `{items: [{name, price, quantity}], total, tax, tips}`
6. Frontend displays items on all-in-one screen for participant assignment

**All-in-one screen:**
- List of recognized items with prices
- Green background = assigned, yellow = unassigned (shows "?")
- Progress bar: "Assigned X of Y₸"
- Participant avatars bar at bottom

**Two assignment modes:**
- **Default (tap → popup):** Tap item → popup with participant checkboxes. Intuitive for "this pizza was shared by 3 people"
- **Brush mode (power user):** Long-press participant avatar → enter brush mode → tap items to assign. Fast for "each person marks their own items"

### 4. Multi-Currency

- Each group has a `base_currency` (home currency for final settlements)
- Each expense stores its `currency` and `exchange_rate` to base currency
- Exchange rate is fixed at the moment of expense creation
- Currency rates fetched from a public API, cached on backend

### 5. Balances & Settlements

**Balances tab:**
- Net balance per participant (spent minus owed)
- Visual bars: green = others owe them, red = they owe others
- Total group spending displayed

**Settlements tab (transaction minimization):**

Algorithm:
1. Calculate net balance for each participant
2. Sort into creditors (positive) and debtors (negative)
3. Greedy: largest debtor pays largest creditor `min(|debt|, |credit|)`
4. Repeat until all balances are zero

Result displayed as transfer cards: `[Debtor] → amount → [Creditor]`

Each settlement has:
- "Mark as paid" button (debtor marks)
- "Confirm" from creditor side (two-party confirmation)
- "Remind" button — sends Telegram notification (if participant is linked)
- Settled transfers shown with green background and confirmation text

### 6. Telegram Notifications

- Reminder to settle debts (triggered by creditor)
- New expense added notification (for group members)
- Settlement confirmation requests

## Data Model

```
users
├── id (PK)
├── telegram_id (unique)
├── display_name
├── avatar_url
└── created_at

groups
├── id (PK)
├── name
├── base_currency
├── invite_code (unique)
├── status (active/archived)
├── created_by (FK → users)
├── archived_at (nullable)
└── created_at

group_members
├── id (PK)
├── group_id (FK → groups)
├── user_id (FK → users, nullable)  -- null for virtual members
├── display_name
├── role (admin/member)
└── UNIQUE(group_id, user_id) WHERE user_id IS NOT NULL

expenses
├── id (PK)
├── group_id (FK → groups)
├── paid_by (FK → group_members)
├── title
├── total_amount (decimal)
├── currency (char 3)
├── exchange_rate (decimal)
├── receipt_image_url (nullable)
├── split_type (equal/by_items/custom)
└── created_at

expense_items
├── id (PK)
├── expense_id (FK → expenses)
├── name
├── price (decimal)
└── quantity (int)

expense_shares
├── id (PK)
├── expense_id (FK → expenses)
├── member_id (FK → group_members)
├── amount (decimal)
└── item_id (FK → expense_items, nullable)

settlements
├── id (PK)
├── group_id (FK → groups)
├── from_member (FK → group_members)
├── to_member (FK → group_members)
├── amount (decimal)
├── currency (char 3)
├── is_settled (boolean)
├── settled_at (nullable)
└── confirmed_by_to (boolean)
```

## API Endpoints

```
# Auth
POST   /api/auth/telegram            — validate initData, issue JWT

# Groups
GET    /api/groups                    — user's groups (active + archived)
POST   /api/groups                    — create group
GET    /api/groups/:id                — group details
PATCH  /api/groups/:id                — edit (name, currency, archive/unarchive)
POST   /api/groups/:id/join           — join by invite_code
POST   /api/groups/:id/members        — add virtual member

# Expenses
GET    /api/groups/:id/expenses       — list group expenses
POST   /api/groups/:id/expenses       — create expense
GET    /api/expenses/:id              — expense details with items and shares
PATCH  /api/expenses/:id              — edit expense
DELETE /api/expenses/:id              — delete expense

# Receipt OCR
POST   /api/receipts/scan             — upload photo → LLM Vision → JSON

# Balances & Settlements
GET    /api/groups/:id/balances       — current participant balances
GET    /api/groups/:id/settlements    — optimized transfers
PATCH  /api/settlements/:id           — mark paid / confirm

# Currency
GET    /api/currencies/rates          — current exchange rates (cached)
```

## Auth Flow

1. User opens Mini App from Telegram
2. Frontend reads `Telegram.WebApp.initData`
3. Sends to `POST /api/auth/telegram`
4. Backend validates signature using bot token (HMAC-SHA256)
5. Creates or finds user by `telegram_id`
6. Returns JWT for subsequent API calls

## Screen Map

1. **My Trips** — list of active groups, archive tab, "New trip" button
2. **Trip Detail** — expense list, tabs: Expenses / Balances / Settlements
3. **Add Expense** — manual entry form (title, amount, payer, split mode)
4. **Scan Receipt** — camera → all-in-one item assignment screen
5. **Settlement Detail** — transfer card with pay/confirm/remind actions
6. **Group Settings** — members, invite link, currency, archive/delete

## Out of Scope (v2+)

- Deep links to banking apps (Kaspi, etc.) for direct payment
- AI auto-assignment of items to participants based on history
- Recurring expenses for roommates/flatmates scenario
- PWA fallback for non-Telegram users
- Expense categories and analytics
- Receipt history and search
