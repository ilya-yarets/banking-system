import unittest
from decimal import Decimal

from banking.accounts.premium import PremiumAccount
from banking.errors import InsufficientFundsError, InvalidOperationError
from banking.types import Owner, Currency


class TestPremiumAccount(unittest.TestCase):
    def test_premium_overdraft_and_fee(self):
        acc = PremiumAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            overdraft_limit=Decimal("50.00"),
            withdraw_fee=Decimal("5.00"),
        )

        acc.withdraw(Decimal("140.00"))

        self.assertEqual(acc.balance, Decimal("-45.00"))
        info = acc.get_account_info()
        self.assertEqual(info["overdraft_limit"], Decimal("50.00"))
        self.assertEqual(info["withdraw_fee"], Decimal("5.00"))
        self.assertIn("overdraft=", str(acc))
        self.assertIn("max_withdraw_per_txn", info)

    def test_max_withdraw_per_txn_enforced(self):
        acc = PremiumAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            max_withdraw_per_txn=Decimal("30.00"),
        )

        with self.assertRaises(InvalidOperationError):
            acc.withdraw(Decimal("40.00"))

    def test_overdraft_limit_enforced(self):
        acc = PremiumAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            overdraft_limit=Decimal("10.00"),
            withdraw_fee=Decimal("0.00"),
        )

        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(Decimal("120.00"))

    def test_withdraw_fee_applied(self):
        acc = PremiumAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("50.00"),
            overdraft_limit=Decimal("0.00"),
            withdraw_fee=Decimal("2.00"),
            max_withdraw_per_txn=Decimal("100.00"),
        )

        acc.withdraw(Decimal("10.00"))

        self.assertEqual(acc.balance, Decimal("38.00"))


if __name__ == "__main__":
    unittest.main()
