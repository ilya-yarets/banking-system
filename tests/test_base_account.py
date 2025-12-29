import unittest

from banking.accounts.base import BankAccount
from banking.errors import (
    AccountFrozenError,
    AccountClosedError,
    InvalidOperationError,
    InsufficientFundsError,
)
from banking.types import Owner, Currency, AccountStatus


class TestBaseAccount(unittest.TestCase):
    def test_deposit_active_account(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
        )

        acc.deposit(50)

        self.assertEqual(acc.balance, 150)

    def test_withdraw_active_account(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
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
            status=AccountStatus.CLOSED,
        )

        with self.assertRaises(AccountClosedError):
            acc.withdraw(10)

    def test_negative_amount_is_invalid(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
        )

        with self.assertRaises(InvalidOperationError):
            acc.deposit(-5)

    def test_insufficient_funds(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=10,
        )

        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(100)

    def test_get_account_info(self):
        acc = BankAccount(
            owner=Owner("Ilya", doc_id="AB123"),
            currency=Currency.EUR,
            balance=25,
        )

        info = acc.get_account_info()

        self.assertEqual(info["type"], "BankAccount")
        self.assertEqual(info["owner_name"], "Ilya")
        self.assertEqual(info["owner_doc_id"], "AB123")
        self.assertEqual(info["currency"], "EUR")

    def test_str_contains_masked_id(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=10,
        )

        text = str(acc)

        self.assertIn("BankAccount(", text)
        self.assertIn("id=****", text)

    def test_invalid_owner(self):
        with self.assertRaises(InvalidOperationError):
            BankAccount(
                owner="Ilya",  # type: ignore[arg-type]
                currency=Currency.USD,
                balance=10,
            )

    def test_invalid_currency(self):
        with self.assertRaises(InvalidOperationError):
            BankAccount(
                owner=Owner("Ilya"),
                currency="USD",  # type: ignore[arg-type]
                balance=10,
            )


if __name__ == "__main__":
    unittest.main()
