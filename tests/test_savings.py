import unittest
from decimal import Decimal

from banking.accounts.savings import SavingsAccount
from banking.errors import InvalidOperationError
from banking.types import Owner, Currency


class TestSavingsAccount(unittest.TestCase):
    def test_savings_min_balance_blocks_withdraw(self):
        acc = SavingsAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            min_balance=Decimal("50.00"),
        )

        with self.assertRaises(InvalidOperationError):
            acc.withdraw(Decimal("60.00"))

    def test_apply_monthly_interest(self):
        acc = SavingsAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            monthly_interest_rate=Decimal("0.02"),
        )

        acc.apply_monthly_interest()

        self.assertEqual(acc.balance, Decimal("102.00"))
        info = acc.get_account_info()
        self.assertEqual(info["min_balance"], Decimal("0.00"))
        self.assertEqual(info["monthly_interest_rate"], Decimal("0.02"))
        self.assertIn("rate=", str(acc))

    def test_initial_balance_below_min_balance(self):
        with self.assertRaises(InvalidOperationError):
            SavingsAccount(
                owner=Owner("Ilya"),
                currency=Currency.USD,
                balance=Decimal("10.00"),
                min_balance=Decimal("50.00"),
            )

    def test_withdraw_within_min_balance(self):
        acc = SavingsAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            min_balance=Decimal("50.00"),
        )

        acc.withdraw(Decimal("40.00"))

        self.assertEqual(acc.balance, Decimal("60.00"))

    def test_negative_interest_rate_is_invalid(self):
        with self.assertRaises(InvalidOperationError):
            SavingsAccount(
                owner=Owner("Ilya"),
                currency=Currency.USD,
                balance=Decimal("100.00"),
                monthly_interest_rate=Decimal("-0.01"),
            )


if __name__ == "__main__":
    unittest.main()
