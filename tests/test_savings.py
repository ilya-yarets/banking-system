import unittest

from banking.accounts.savings import SavingsAccount
from banking.types import Owner, Currency


class TestSavingsAccount(unittest.TestCase):
    def test_savings_inherits_bank_account(self):
        acc = SavingsAccount(owner=Owner("Ilya"), currency=Currency.USD, balance=10)
        acc.deposit(5)
        self.assertEqual(acc.balance, 15)


if __name__ == "__main__":
    unittest.main()
