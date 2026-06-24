from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

TWO_PLACES = Decimal("0.01")


def calculate_balances(expenses: list[dict]) -> dict[int, Decimal]:
    """Calculate net balance for each member across all expenses.

    Positive = others owe them. Negative = they owe others.
    All amounts converted to base currency using exchange_rate.
    Shares are normalized so total debits = total credits per expense.
    """
    balances: dict[int, Decimal] = defaultdict(Decimal)

    for expense in expenses:
        paid_by = expense["paid_by_id"]
        rate = expense["exchange_rate"]
        total_in_base = (expense["total_amount"] * rate).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

        # Payer gets credited for the full amount
        balances[paid_by] += total_in_base

        shares = expense["shares"]
        if not shares:
            continue

        # Normalize shares so debits sum exactly to total_in_base
        shares_sum = sum(s["amount"] for s in shares)
        if shares_sum == 0:
            continue

        debited = Decimal(0)
        for i, share in enumerate(shares):
            member_id = share["member_id"]
            if i == len(shares) - 1:
                # Last share gets the remainder to avoid rounding drift
                amount_in_base = total_in_base - debited
            else:
                amount_in_base = (
                    total_in_base * share["amount"] / shares_sum
                ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            balances[member_id] -= amount_in_base
            debited += amount_in_base

    return dict(balances)


def minimize_settlements(balances: dict[int, Decimal]) -> list[tuple[int, int, Decimal]]:
    """Minimize the number of transfers to settle all debts.

    Returns list of (from_member_id, to_member_id, amount) tuples.
    Uses greedy algorithm: match largest debtor with largest creditor.
    """
    debtors = []
    creditors = []

    for member_id, balance in balances.items():
        if balance < 0:
            debtors.append([member_id, -balance])
        elif balance > 0:
            creditors.append([member_id, balance])

    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    settlements = []
    i, j = 0, 0

    while i < len(debtors) and j < len(creditors):
        debtor_id, debt = debtors[i]
        creditor_id, credit = creditors[j]

        transfer = min(debt, credit)
        if transfer > 0:
            settlements.append((debtor_id, creditor_id, transfer))

        debtors[i][1] -= transfer
        creditors[j][1] -= transfer

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return settlements
