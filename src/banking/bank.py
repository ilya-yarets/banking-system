from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, time
from decimal import Decimal
from typing import Iterable

from banking.account_options import (
    AccountOptions,
    BaseAccountOptions,
    InvestmentOptions,
    PremiumOptions,
    SavingsOptions,
)
from banking.accounts.base import BankAccount
from banking.accounts.investment import InvestmentAccount
from banking.accounts.premium import PremiumAccount
from banking.accounts.savings import SavingsAccount
from banking.client import Client
from banking.errors import InvalidOperationError
from banking.money import ZERO_MONEY
from banking.types import AccountStatus, AccountType, ClientStatus, Currency, Owner

MAX_FAILED_ATTEMPTS = 3
QUIET_HOURS_START = time(0, 0)
QUIET_HOURS_END = time(5, 0)
ACCOUNT_TYPE_MAP = {
    AccountType.BASE: (BankAccount, BaseAccountOptions),
    AccountType.BANK: (BankAccount, BaseAccountOptions),
    AccountType.SAVINGS: (SavingsAccount, SavingsOptions),
    AccountType.PREMIUM: (PremiumAccount, PremiumOptions),
    AccountType.INVESTMENT: (InvestmentAccount, InvestmentOptions),
}


@dataclass
class BankSecurityLog:
    client_id: str
    reason: str
    created_at: datetime


@dataclass
class Bank:
    _clients: dict[str, Client] = field(default_factory=dict)
    _accounts: dict[str, BankAccount] = field(default_factory=dict)
    _credentials: dict[str, str] = field(default_factory=dict)
    _failed_attempts: dict[str, int] = field(default_factory=dict)
    _security_log: list[BankSecurityLog] = field(default_factory=list)

    def add_client(self, client: Client, password: str) -> None:
        # Register a client with initial credentials and reset counters.
        if client.client_id in self._clients:
            raise InvalidOperationError("Client already exists.")
        if not password:
            raise InvalidOperationError("Password is required.")
        self._clients[client.client_id] = client
        self._credentials[client.client_id] = password
        self._failed_attempts[client.client_id] = 0

    def open_account(
        self,
        client_id: str,
        *,
        account_type: AccountType | str = AccountType.BASE,
        currency: Currency = Currency.USD,
        balance: Decimal = ZERO_MONEY,
        now: datetime | None = None,
        options: AccountOptions | None = None,
    ) -> BankAccount:
        # Create a new account for an active client during allowed hours.
        self._ensure_operating_hours(now=now, client_id=client_id)
        client = self._get_active_client(client_id)
        owner = Owner(name=client.full_name, doc_id=client.client_id)
        account_type_normalized = self._normalize_account_type(account_type)
        if account_type_normalized not in ACCOUNT_TYPE_MAP: raise InvalidOperationError("Unknown account type.")
        account_cls, options_cls = ACCOUNT_TYPE_MAP[account_type_normalized]
        opts = self._ensure_options(options, options_cls)
        account = account_cls(
            owner=owner,
            currency=currency,
            balance=balance,
            **asdict(opts),
        )
        self._accounts[account.id] = account
        client.add_account(account.id)
        return account

    def close_account(self, account_id: str, *, now: datetime | None = None) -> None:
        # Close account and disallow further operations.
        self._ensure_operating_hours(now=now, client_id=self._account_client_id(account_id))
        account = self._get_account(account_id)
        account._status = AccountStatus.CLOSED

    def freeze_account(self, account_id: str, *, now: datetime | None = None) -> None:
        # Freeze account unless already closed.
        self._ensure_operating_hours(now=now, client_id=self._account_client_id(account_id))
        account = self._get_account(account_id)
        if account.status != AccountStatus.CLOSED:
            account._status = AccountStatus.FROZEN

    def unfreeze_account(self, account_id: str, *, now: datetime | None = None) -> None:
        # Restore frozen account back to active status.
        self._ensure_operating_hours(now=now, client_id=self._account_client_id(account_id))
        account = self._get_account(account_id)
        if account.status == AccountStatus.FROZEN:
            account._status = AccountStatus.ACTIVE

    def authenticate_client(self, client_id: str, password: str) -> bool:
        # Track failed attempts and block after 3 incorrect passwords.
        client = self._clients.get(client_id)
        if client is None:
            return False
        if client.status == ClientStatus.BLOCKED:
            return False
        if self._credentials.get(client_id) == password:
            self._failed_attempts[client_id] = 0
            return True
        self._failed_attempts[client_id] = self._failed_attempts.get(client_id, 0) + 1
        if self._failed_attempts[client_id] >= MAX_FAILED_ATTEMPTS:
            client.status = ClientStatus.BLOCKED
            self._log_security_event(client_id, "account locked after failed logins")
        else:
            self._log_security_event(client_id, "failed login attempt")
        return False

    def search_accounts(
        self,
        *,
        client_id: str | None = None,
        status: AccountStatus | None = None,
        currency: Currency | None = None,
    ) -> list[BankAccount]:
        # Filter accounts by owner, status, and/or currency.
        results: Iterable[BankAccount] = self._accounts.values()
        if client_id is not None:
            results = [acc for acc in results if acc.owner.doc_id == client_id]
        if status is not None:
            results = [acc for acc in results if acc.status == status]
        if currency is not None:
            results = [acc for acc in results if acc.currency == currency]
        return list(results)

    def get_total_balance(self) -> Decimal:
        # Sum balances across all non-closed accounts.
        total = ZERO_MONEY
        for account in self._accounts.values():
            if account.status != AccountStatus.CLOSED:
                total += account.balance
        return total

    def get_clients_ranking(self) -> list[tuple[str, Decimal]]:
        # Rank clients by their total balance across accounts.
        totals: dict[str, Decimal] = {client_id: ZERO_MONEY for client_id in self._clients}
        for account in self._accounts.values():
            if account.status == AccountStatus.CLOSED:
                continue
            client_id = account.owner.doc_id
            if client_id in totals:
                totals[client_id] += account.balance
        return sorted(totals.items(), key=lambda item: item[1], reverse=True)

    @property
    def security_log(self) -> list[BankSecurityLog]:
        # Expose a copy so callers cannot mutate internal state.
        return list(self._security_log)

    def _ensure_operating_hours(self, *, now: datetime | None, client_id: str) -> None:
        # Block operations during quiet hours and log the event.
        current = now or datetime.now()
        if QUIET_HOURS_START <= current.time() < QUIET_HOURS_END:
            self._log_security_event(client_id, "operation blocked during quiet hours")
            raise InvalidOperationError("Operations are not allowed between 00:00 and 05:00.")

    def _get_account(self, account_id: str) -> BankAccount:
        # Centralized lookup with consistent error.
        account = self._accounts.get(account_id)
        if account is None:
            raise InvalidOperationError("Account not found.")
        return account

    def _get_active_client(self, client_id: str) -> Client:
        # Ensure the client exists and is active.
        client = self._clients.get(client_id)
        if client is None:
            raise InvalidOperationError("Client not found.")
        if client.status != ClientStatus.ACTIVE:
            raise InvalidOperationError("Client is not active.")
        return client

    def _account_client_id(self, account_id: str) -> str:
        # Resolve client id from account for security checks.
        account = self._get_account(account_id)
        return account.owner.doc_id or ""

    def _normalize_account_type(self, account_type: AccountType | str) -> AccountType:
        if isinstance(account_type, AccountType):
            return account_type
        try:
            return AccountType(account_type)
        except ValueError:
            raise InvalidOperationError("Unknown account type.")

    def _ensure_options(self, options: AccountOptions | None, expected_type: type[AccountOptions], ) -> AccountOptions:
        if options is None:
            return expected_type()
        if not isinstance(options, expected_type):
            raise InvalidOperationError("Options type does not match account type.")
        return options

    def _log_security_event(self, client_id: str, reason: str) -> None:
        # Append security events for auditing.
        self._security_log.append(BankSecurityLog(client_id=client_id, reason=reason, created_at=datetime.now()))
