import unittest

from banking.accounts.premium import PremiumAccount
from banking.types import Owner, Currency


class TestPremiumAccount(unittest.TestCase):
    def test_premium_inherits_bank_account(self):
        acc = PremiumAccount(owner=Owner("Ilya"), currency=Currency.USD, balance=10)
        acc.deposit(5)
        self.assertEqual(acc.balance, 15)


if __name__ == "__main__":
    unittest.main()
