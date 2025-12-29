import uuid
from abc import ABC, abstractmethod

from banking.errors import (
    InvalidOperationError,
    InsufficientFundsError,
    AccountFrozenError,
    AccountClosedError,
)
from banking.types import AccountStatus, Currency, Owner


class AbstractAccount(ABC):
    def __init__(
        self,
        owner: Owner,
        account_id: str,
        balance: float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
    ):
        self._id = account_id
        self._owner = owner
        self._balance = float(balance)
        self._status = status

    @property
    def id(self) -> str:
        return self._id

    @property
    def owner(self) -> Owner:
        return self._owner

    @property
    def status(self) -> AccountStatus:
        return self._status

    @property
    def balance(self) -> float:
        return self._balance

    @abstractmethod
    def deposit(self, amount: float) -> None: ...

    @abstractmethod
    def withdraw(self, amount: float) -> None: ...

    @abstractmethod
    def get_account_info(self) -> dict: ...


class BankAccount(AbstractAccount):
    def __init__(
        self,
        owner: Owner,
        account_id: str | None = None,
        balance: float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.USD,
    ):
        if account_id is None:
            account_id = uuid.uuid4().hex[:8]  # short uuid
        self._validate_owner(owner)
        self._validate_amount(balance, allow_zero=True)
        self._validate_currency(currency)

        super().__init__(owner=owner, account_id=account_id, balance=balance, status=status)
        self._currency = currency

    @property
    def currency(self) -> Currency:
        return self._currency

    def deposit(self, amount: float) -> None:
        self._check_can_operate()
        self._validate_amount(amount)
        self._balance += float(amount)

    def withdraw(self, amount: float) -> None:
        self._check_can_operate()
        self._validate_amount(amount)
        if float(amount) > self._balance:
            raise InsufficientFundsError("Not enough balance to withdraw this amount.")
        self._balance -= float(amount)

    def get_account_info(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "id": self._id,
            "owner_name": self._owner.name,
            "owner_doc_id": self._owner.doc_id,
            "status": self._status.value,
            "balance": self._balance,
            "currency": self._currency.value,
        }

    def _check_can_operate(self) -> None:
        if self._status == AccountStatus.FROZEN:
            raise AccountFrozenError("Account is frozen. Operations are not allowed.")
        if self._status == AccountStatus.CLOSED:
            raise AccountClosedError("Account is closed. Operations are not allowed.")
        if self._status != AccountStatus.ACTIVE:
            raise InvalidOperationError(f"Unknown account status: {self._status}")

    @staticmethod
    def _validate_owner(owner: Owner) -> None:
        if not isinstance(owner, Owner):
            raise InvalidOperationError("Owner must be an Owner object.")
        if not owner.name or not owner.name.strip():
            raise InvalidOperationError("Owner name is required.")

    @staticmethod
    def _validate_currency(currency: Currency) -> None:
        if not isinstance(currency, Currency):
            raise InvalidOperationError("Currency must be one of: RUB, USD, EUR, KZT, CNY.")

    @staticmethod
    def _validate_amount(amount: float, allow_zero: bool = False) -> None:
        try:
            val = float(amount)
        except (TypeError, ValueError):
            raise InvalidOperationError("Amount must be a number.")
        if val < 0:
            raise InvalidOperationError("Amount cannot be negative.")
        if not allow_zero and val == 0:
            raise InvalidOperationError("Amount must be greater than zero.")

    def __str__(self) -> str:
        last4 = self._id[-4:] if self._id else "????"
        return (
            f"{self.__class__.__name__}("
            f"client={self._owner.name}, "
            f"id=****{last4}, "
            f"status={self._status.value}, "
            f"balance={self._balance:.2f} {self._currency.value}"
            f")"
        )
