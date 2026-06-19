from decimal import Decimal
from collections import defaultdict


def calculate_balances(expenses: list[dict]) -> dict[int, Decimal]:
    """Calculate net balance for each member across all expenses.

    Positive = others owe them. Negative = they owe others.
    All amounts converted to base currency using exchange_rate.
    """
    balances: dict[int, Decimal] = defaultdict(Decimal)

    for expense in expenses:
        paid_by = expense["paid_by_id"]
        rate = expense["exchange_rate"]
        total_in_base = expense["total_amount"] * rate

        # Payer gets credited for the full amount
        balances[paid_by] += total_in_base

        # Each share debits the member
        for share in expense["shares"]:
            member_id = share["member_id"]
            amount_in_base = share["amount"] * rate
            balances[member_id] -= amount_in_base

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
