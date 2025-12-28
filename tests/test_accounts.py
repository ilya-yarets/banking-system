import unittest

from src.accounts import BankAccount, Owner, Currency, AccountStatus
from src.errors import (
    AccountFrozenError,
    AccountClosedError,
    InvalidOperationError,
    InsufficientFundsError,
)


class MyTestCase(unittest.TestCase):

    def test_deposit_active_account(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100
        )

        acc.deposit(50)

        self.assertEqual(acc.balance, 150)

    def test_withdraw_active_account(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100
        )

        acc.withdraw(40)

        self.assertEqual(acc.balance, 60)

    def test_frozen_account_cannot_deposit(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            status=AccountStatus.FROZEN,

        )

        with self.assertRaises(AccountFrozenError):
            acc.deposit(10)

    def test_closed_account_cannot_withdraw(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            status=AccountStatus.CLOSED
        )

        with self.assertRaises(AccountClosedError):
            acc.withdraw(10)

    def test_negative_amount_is_invalid(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100
        )

        with self.assertRaises(InvalidOperationError):
            acc.deposit(-5)

    def test_insufficient_funds(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=10
        )

        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(100)


if __name__ == '__main__':
    unittest.main()