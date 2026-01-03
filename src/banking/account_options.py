from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from banking.money import DEFAULT_MAX_WITHDRAW, ZERO_MONEY


@dataclass(frozen=True)
class AccountOptions:
    pass


@dataclass(frozen=True)
class BaseAccountOptions(AccountOptions):
    pass


@dataclass(frozen=True)
class SavingsOptions(AccountOptions):
    min_balance: Decimal = ZERO_MONEY
    monthly_interest_rate: Decimal = ZERO_MONEY


@dataclass(frozen=True)
class PremiumOptions(AccountOptions):
    overdraft_limit: Decimal = ZERO_MONEY
    withdraw_fee: Decimal = ZERO_MONEY
    max_withdraw_per_txn: Decimal = DEFAULT_MAX_WITHDRAW


@dataclass(frozen=True)
class InvestmentOptions(AccountOptions):
    portfolios: dict | None = None
    expected_yearly_growth: Decimal = ZERO_MONEY
