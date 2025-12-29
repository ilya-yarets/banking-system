import unittest

from banking.accounts.investment import InvestmentAccount
from banking.types import Owner, Currency


class TestInvestmentAccount(unittest.TestCase):
    def test_investment_inherits_bank_account(self):
        acc = InvestmentAccount(owner=Owner("Ilya"), currency=Currency.USD, balance=10)
        acc.deposit(5)
        self.assertEqual(acc.balance, 15)


if __name__ == "__main__":
    unittest.main()
