import unittest
from datetime import datetime
from decimal import Decimal

from banking.bank import Bank
from banking.client import Client
from banking.errors import InvalidOperationError
from banking.types import AccountStatus, AccountType, ClientStatus, Currency


class TestBank(unittest.TestCase):
    def setUp(self):
        self.bank = Bank()
        self.client = Client(
            full_name="Ilya Yarets",
            client_id="C-001",
            age=30,
            contacts={"phone": "+10000000000"},
        )
        self.bank.add_client(self.client, password="secret")

    def test_client_age_validation(self):
        with self.assertRaises(InvalidOperationError):
            Client(full_name="Young Client", client_id="C-002", age=17)

    def test_authentication_blocks_after_three_attempts(self):
        self.assertFalse(self.bank.authenticate_client("C-001", "wrong1"))
        self.assertFalse(self.bank.authenticate_client("C-001", "wrong2"))
        self.assertFalse(self.bank.authenticate_client("C-001", "wrong3"))
        self.assertEqual(self.client.status, ClientStatus.BLOCKED)
        self.assertFalse(self.bank.authenticate_client("C-001", "secret"))

    def test_open_freeze_unfreeze_close(self):
        account = self.bank.open_account(
            "C-001",
            account_type=AccountType.BASE,
            currency=Currency.USD,
            balance=Decimal("100.00"),
        )
        self.assertIn(account.id, self.client.accounts)
        self.bank.freeze_account(account.id)
        self.assertEqual(account.status, AccountStatus.FROZEN)
        self.bank.unfreeze_account(account.id)
        self.assertEqual(account.status, AccountStatus.ACTIVE)
        self.bank.close_account(account.id)
        self.assertEqual(account.status, AccountStatus.CLOSED)

    def test_restricted_hours_blocks_operation(self):
        with self.assertRaises(InvalidOperationError):
            self.bank.open_account(
                "C-001",
                account_type=AccountType.BASE,
                currency=Currency.USD,
                balance=Decimal("10.00"),
                now=datetime(2024, 1, 1, 1, 30),
            )
        self.assertTrue(self.bank.security_log)

    def test_totals_and_ranking(self):
        client_two = Client(
            full_name="Anna Petrova",
            client_id="C-002",
            age=40,
            contacts={"email": "anna@example.com"},
        )
        self.bank.add_client(client_two, password="pass")
        self.bank.open_account(
            "C-001",
            account_type=AccountType.BASE,
            currency=Currency.USD,
            balance=Decimal("200.00"),
        )
        self.bank.open_account(
            "C-002",
            account_type=AccountType.BASE,
            currency=Currency.USD,
            balance=Decimal("50.00"),
        )
        total = self.bank.get_total_balance()
        self.assertEqual(total, Decimal("250.00"))
        ranking = self.bank.get_clients_ranking()
        self.assertEqual(ranking[0][0], "C-001")


if __name__ == "__main__":
    unittest.main()
