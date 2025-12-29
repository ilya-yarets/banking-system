import unittest

from banking.accounts.savings import SavingsAccount
from banking.errors import InvalidOperationError
from banking.types import Owner, Currency


class TestSavingsAccount(unittest.TestCase):
    def test_savings_min_balance_blocks_withdraw(self):
        acc = SavingsAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            min_balance=50,
        )

        with self.assertRaises(InvalidOperationError):
            acc.withdraw(60)

    def test_apply_monthly_interest(self):
        acc = SavingsAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            monthly_interest_rate=0.02,
        )

        acc.apply_monthly_interest()

        self.assertAlmostEqual(acc.balance, 102.0, places=2)
        info = acc.get_account_info()
        self.assertEqual(info["min_balance"], 0.0)
        self.assertEqual(info["monthly_interest_rate"], 0.02)
        self.assertIn("rate=", str(acc))

    def test_initial_balance_below_min_balance(self):
        with self.assertRaises(InvalidOperationError):
            SavingsAccount(
                owner=Owner("Ilya"),
                currency=Currency.USD,
                balance=10,
                min_balance=50,
            )

    def test_withdraw_within_min_balance(self):
        acc = SavingsAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            min_balance=50,
        )

        acc.withdraw(40)

        self.assertEqual(acc.balance, 60)

    def test_negative_interest_rate_is_invalid(self):
        with self.assertRaises(InvalidOperationError):
            SavingsAccount(
                owner=Owner("Ilya"),
                currency=Currency.USD,
                balance=100,
                monthly_interest_rate=-0.01,
            )


if __name__ == "__main__":
    unittest.main()
