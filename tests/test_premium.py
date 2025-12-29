import unittest

from banking.accounts.premium import PremiumAccount
from banking.errors import InsufficientFundsError, InvalidOperationError
from banking.types import Owner, Currency


class TestPremiumAccount(unittest.TestCase):
    def test_premium_overdraft_and_fee(self):
        acc = PremiumAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            overdraft_limit=50,
            withdraw_fee=5,
        )

        acc.withdraw(140)

        self.assertEqual(acc.balance, -45)
        info = acc.get_account_info()
        self.assertEqual(info["overdraft_limit"], 50.0)
        self.assertEqual(info["withdraw_fee"], 5.0)
        self.assertIn("overdraft=", str(acc))
        self.assertIn("max_withdraw_per_txn", info)

    def test_max_withdraw_per_txn_enforced(self):
        acc = PremiumAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            max_withdraw_per_txn=30,
        )

        with self.assertRaises(InvalidOperationError):
            acc.withdraw(40)

    def test_overdraft_limit_enforced(self):
        acc = PremiumAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            overdraft_limit=10,
            withdraw_fee=0,
        )

        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(120)

    def test_withdraw_fee_applied(self):
        acc = PremiumAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=50,
            overdraft_limit=0,
            withdraw_fee=2,
            max_withdraw_per_txn=100,
        )

        acc.withdraw(10)

        self.assertEqual(acc.balance, 38)


if __name__ == "__main__":
    unittest.main()
