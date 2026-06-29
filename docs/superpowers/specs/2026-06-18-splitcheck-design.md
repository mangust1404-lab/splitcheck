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
| Database | PostgreSQL (asyncpg) — Render managed instance |
| Receipt OCR | Claude Vision API |
| File Storage | Cloudflare R2 (receipt images) — not yet configured |
| Deploy | Render (free tier), multi-stage Dockerfile, auto-deploy from `master` |

## Core Features (MVP)

### 0. Internationalization (i18n)

- Two languages: **Russian** and **English**
- Auto-detected from Telegram user's `language_code` (falls back to English)
- Lightweight composable (`useI18n`) with reactive locale and `{param}` interpolation
- All UI strings translated; code comments and API remain in English

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
- **Default (tap-to-select + assign):** Tap items to multi-select them (highlighted), then tap a participant avatar in the floating bottom bar to assign all selected items at once. Intuitive for batch assignment.
- **Brush mode:** Tap participant avatar in the ParticipantBar → enter brush mode → tap items to toggle exclusive assignment. Fast for "each person marks their own items".

> **Note:** The original "popup with checkboxes" mode was simplified to tap-to-assign with multi-select for the MVP. Brush mode works via single tap on avatar (not long-press).

**Additional receipt features:**
- Discount line item support — discounts are proportionally distributed across assigned item shares
- Receipt total vs items total comparison shown when discount is present
- Detected currency displayed as a badge (auto-detected from receipt by LLM)

### 4. Multi-Currency

- Each group has a `base_currency` (home currency for final settlements)
- Each expense stores its `currency` and `exchange_rate` to base currency
- Exchange rate is fixed at the moment of expense creation
- Currency rates fetched from open.er-api.com (free, no API key required), cached for 1 hour on backend

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

**Backend logic:** Already-settled amounts are subtracted from balances before running `minimize_settlements`, preventing duplicate settlements when some transfers are already marked as paid.

**3-state visual system for settlement cards:**

| State | Card Style | Actions |
|-------|-----------|---------|
| Not paid | White card, gray border | "Mark Paid" button + "Remind" button |
| Paid (not confirmed) | Light green card, amount crossed out, checkmark | "Paid" label + "Undo" button |
| Paid + confirmed | Green card | "Paid and confirmed" text (no actions) |

- "Remind" button sends a Telegram notification to the debtor
- If the debtor is a virtual member (no Telegram linked), "Remind" shows an alert explaining they need to join via invite link
- "Undo" resets the settlement back to unpaid state

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
├── group_id (FK → groups, CASCADE)
├── from_member_id (FK → group_members)
├── to_member_id (FK → group_members)
├── amount (decimal 12,2)
├── currency (char 3)
├── is_settled (boolean, default false)
├── settled_at (nullable, timezone-aware)
└── confirmed_by_to (boolean, default false)
```

## API Endpoints

```
# Auth
POST   /api/auth/telegram            — validate initData, issue JWT
GET    /api/auth/me                   — get current user info

# Groups
GET    /api/groups                    — user's groups (active + archived)
POST   /api/groups                    — create group
GET    /api/groups/invite/:code       — preview group before joining (no membership required)
GET    /api/groups/:id                — group details
PATCH  /api/groups/:id                — edit (name, currency, archive/unarchive)
DELETE /api/groups/:id                — delete group (owner only)
POST   /api/groups/:id/join           — join by invite_code (link to virtual member or create new)
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
PATCH  /api/settlements/:id           — mark paid / confirm / undo
POST   /api/settlements/:id/remind    — send Telegram reminder to debtor

# Currency
GET    /api/currencies/rates          — current exchange rates (cached, 1h TTL)
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
3. **Add Expense** — manual entry form (title, amount, payer, split mode); also used for editing existing expenses
4. **Scan Receipt** — camera/gallery → all-in-one item assignment with multi-select
5. **Expense Detail** — shows expense info, items, distribution; edit and delete actions
6. **Join Group** — invite preview (group name, members list), link to existing virtual member or join as new participant
7. **Group Settings** — members, invite link, currency, archive/reactivate, delete group
8. **Settlement Cards** (inline in Trip Detail) — 3-state transfer cards with pay/confirm/remind/undo actions

## Deployment

| Parameter | Value |
|-----------|-------|
| Хостинг | [Render](https://render.com) (free tier) |
| URL приложения | https://splitcheck-miym.onrender.com |
| Telegram бот | https://t.me/SplitCheckanalog_bot/app |
| GitHub репозиторий | https://github.com/mangust1404-lab/splitcheck (public) |
| База данных | PostgreSQL — `splitcheck-db` на Render (free tier) |
| Dockerfile | Multi-stage: Node.js (сборка frontend) + Python (backend + static serving) |
| IaC | `render.yaml` blueprint в корне репозитория |
| Auto-deploy | Включен, из ветки `master` |
| Cold start | ~50 секунд (free tier засыпает при неактивности) |

**Telegram Mini App URL — два независимых места настройки:**

При смене домена/хостинга необходимо обновить URL в **двух** местах:

1. **`setChatMenuButton` (Bot API)** — кнопка меню в чате с ботом. Влияет только на кнопку внизу чата, **не** на deep link `/app`.
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/setChatMenuButton" \
     -H "Content-Type: application/json" \
     -d '{"menu_button":{"type":"web_app","text":"SplitCheck","web_app":{"url":"https://splitcheck-miym.onrender.com"}}}'
   ```

2. **Main Mini App URL (BotFather)** — URL для deep link `t.me/SplitCheckanalog_bot/app`. Настраивается через BotFather: `/myapps` → выбрать бота → Edit Web App URL. Без этого ссылка для шеринга `https://t.me/SplitCheckanalog_bot/app` будет вести на старый домен.

> **Важно:** `setChatMenuButton` и Main Mini App URL — это разные настройки. Обновление одного не обновляет другое.

**Ограничения текущего деплоя:**
- Cloudflare R2 переменные (`R2_ENDPOINT`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`) не настроены — сканирование чеков загружает изображение только для распознавания, не сохраняет в storage
- Free tier Render: 750 часов/месяц, автоматическое засыпание после 15 минут неактивности, cold start ~50 секунд

## Out of Scope (v2+)

- Deep links to banking apps (Kaspi, etc.) for direct payment
- AI auto-assignment of items to participants based on history
- Recurring expenses for roommates/flatmates scenario
- PWA fallback for non-Telegram users
- Expense categories and analytics
- Receipt history and search
