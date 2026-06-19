from decimal import Decimal

from app.services.settlement_calculator import calculate_balances, minimize_settlements


class TestCalculateBalances:
    def test_equal_split_two_people(self):
        expenses = [
            {
                "paid_by_id": 1,
                "total_amount": Decimal("1000"),
                "exchange_rate": Decimal("1"),
                "shares": [
                    {"member_id": 1, "amount": Decimal("500")},
                    {"member_id": 2, "amount": Decimal("500")},
                ],
            }
        ]
        balances = calculate_balances(expenses)
        assert balances[1] == Decimal("500")
        assert balances[2] == Decimal("-500")

    def test_multiple_expenses(self):
        expenses = [
            {
                "paid_by_id": 1,
                "total_amount": Decimal("3000"),
                "exchange_rate": Decimal("1"),
                "shares": [
                    {"member_id": 1, "amount": Decimal("1000")},
                    {"member_id": 2, "amount": Decimal("1000")},
                    {"member_id": 3, "amount": Decimal("1000")},
                ],
            },
            {
                "paid_by_id": 2,
                "total_amount": Decimal("1500"),
                "exchange_rate": Decimal("1"),
                "shares": [
                    {"member_id": 1, "amount": Decimal("750")},
                    {"member_id": 2, "amount": Decimal("750")},
                ],
            },
        ]
        balances = calculate_balances(expenses)
        assert balances[1] == Decimal("1250")
        assert balances[2] == Decimal("-250")
        assert balances[3] == Decimal("-1000")

    def test_with_exchange_rate(self):
        expenses = [
            {
                "paid_by_id": 1,
                "total_amount": Decimal("100"),
                "exchange_rate": Decimal("450"),
                "shares": [
                    {"member_id": 1, "amount": Decimal("50")},
                    {"member_id": 2, "amount": Decimal("50")},
                ],
            }
        ]
        balances = calculate_balances(expenses)
        assert balances[1] == Decimal("22500")
        assert balances[2] == Decimal("-22500")


class TestMinimizeSettlements:
    def test_simple_two_people(self):
        balances = {1: Decimal("500"), 2: Decimal("-500")}
        settlements = minimize_settlements(balances)
        assert len(settlements) == 1
        assert settlements[0] == (2, 1, Decimal("500"))

    def test_four_people_minimized(self):
        balances = {
            1: Decimal("8500"),
            2: Decimal("1200"),
            3: Decimal("-3700"),
            4: Decimal("-6000"),
        }
        settlements = minimize_settlements(balances)
        assert len(settlements) <= 3

        net = dict(balances)
        for from_id, to_id, amount in settlements:
            net[from_id] += amount
            net[to_id] -= amount
        for v in net.values():
            assert v == Decimal("0")

    def test_already_settled(self):
        balances = {1: Decimal("0"), 2: Decimal("0")}
        settlements = minimize_settlements(balances)
        assert len(settlements) == 0

    def test_three_way_circle(self):
        balances = {1: Decimal("0"), 2: Decimal("0"), 3: Decimal("0")}
        settlements = minimize_settlements(balances)
        assert len(settlements) == 0
