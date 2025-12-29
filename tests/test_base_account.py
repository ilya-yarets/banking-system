import unittest
from decimal import Decimal

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
            balance=Decimal("100.00"),
        )

        acc.deposit(Decimal("50.00"))

        self.assertEqual(acc.balance, Decimal("150.00"))

    def test_withdraw_active_account(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
        )

        acc.withdraw(Decimal("40.00"))

        self.assertEqual(acc.balance, Decimal("60.00"))

    def test_frozen_account_cannot_deposit(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            status=AccountStatus.FROZEN,
        )

        with self.assertRaises(AccountFrozenError):
            acc.deposit(Decimal("10.00"))

    def test_closed_account_cannot_withdraw(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            status=AccountStatus.CLOSED,
        )

        with self.assertRaises(AccountClosedError):
            acc.withdraw(Decimal("10.00"))

    def test_negative_amount_is_invalid(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
        )

        with self.assertRaises(InvalidOperationError):
            acc.deposit(Decimal("-5.00"))

    def test_insufficient_funds(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("10.00"),
        )

        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(Decimal("100.00"))

    def test_get_account_info(self):
        acc = BankAccount(
            owner=Owner("Ilya", doc_id="AB123"),
            currency=Currency.EUR,
            balance=Decimal("25.00"),
        )

        info = acc.get_account_info()

        self.assertEqual(info["type"], "BankAccount")
        self.assertEqual(info["owner_name"], "Ilya")
        self.assertEqual(info["owner_doc_id"], "AB123")
        self.assertEqual(info["currency"], "EUR")
        self.assertEqual(info["balance"], Decimal("25.00"))

    def test_str_contains_masked_id(self):
        acc = BankAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("10.00"),
        )

        text = str(acc)

        self.assertIn("BankAccount(", text)
        self.assertIn("id=****", text)

    def test_invalid_owner(self):
        with self.assertRaises(InvalidOperationError):
            BankAccount(
                owner="Ilya",  # type: ignore[arg-type]
                currency=Currency.USD,
                balance=Decimal("10.00"),
            )

    def test_invalid_currency(self):
        with self.assertRaises(InvalidOperationError):
            BankAccount(
                owner=Owner("Ilya"),
                currency="USD",  # type: ignore[arg-type]
                balance=Decimal("10.00"),
            )


if __name__ == "__main__":
    unittest.main()
