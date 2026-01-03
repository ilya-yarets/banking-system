from dataclasses import dataclass
from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class Currency(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    KZT = "KZT"
    CNY = "CNY"


class AccountType(str, Enum):
    BASE = "base"
    BANK = "bank"
    SAVINGS = "savings"
    PREMIUM = "premium"
    INVESTMENT = "investment"


class ClientStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Owner:
    name: str
    doc_id: str | None = None
