from decimal import Decimal, InvalidOperation

from banking.accounts.base import BankAccount
from banking.money import MONEY_QUANT, ZERO_MONEY
from banking.errors import InsufficientFundsError, InvalidOperationError


class InvestmentAccount(BankAccount):
    def __init__(
        self,
        *,
        portfolios: dict | None = None,
        expected_yearly_growth: Decimal = ZERO_MONEY,
        **kwargs,
    ):
        super().__init__(**kwargs)
        growth_val = self._validate_growth_rate(expected_yearly_growth)
        if growth_val < 0:
            raise InvalidOperationError("Expected yearly growth cannot be negative.")
        self._expected_yearly_growth = growth_val
        self._portfolios = {
            "stocks": ZERO_MONEY,
            "bonds": ZERO_MONEY,
            "etf": ZERO_MONEY,
        }
        if portfolios:
            for asset_type, value in portfolios.items():
                if asset_type not in self._portfolios:
                    raise InvalidOperationError(
                        "Portfolio asset must be one of: stocks, bonds, etf."
                    )
                self._portfolios[asset_type] = self._validate_amount(
                    value, allow_zero=True
                )

    def project_yearly_growth(self, years: int = 1) -> Decimal:
        if years < 0:
            raise InvalidOperationError("Years cannot be negative.")
        base = self._balance + self.portfolio_value
        projected = base * ((Decimal("1") + self._expected_yearly_growth) ** years)
        return projected.quantize(MONEY_QUANT)

    def withdraw(self, amount: Decimal) -> None:
        self._check_can_operate()
        value = self._validate_amount(amount)
        if value > self._balance:
            raise InsufficientFundsError("Not enough balance to withdraw this amount.")
        self._balance -= value

    def add_asset(self, asset_type: str, amount: Decimal) -> None:
        self._check_can_operate()
        if asset_type not in self._portfolios:
            raise InvalidOperationError("Asset type must be one of: stocks, bonds, etf.")
        value = self._validate_amount(amount)
        self._portfolios[asset_type] = (self._portfolios[asset_type] + value).quantize(
            MONEY_QUANT
        )

    @property
    def portfolio_value(self) -> Decimal:
        return sum(self._portfolios.values(), ZERO_MONEY)

    def get_account_info(self) -> dict:
        info = super().get_account_info()
        info.update(
            {
                "portfolios": dict(self._portfolios),
                "portfolio_value": self.portfolio_value,
                "expected_yearly_growth": self._expected_yearly_growth,
            }
        )
        return info

    def __str__(self) -> str:
        last4 = self._id[-4:] if self._id else "????"
        return (
            f"InvestmentAccount("
            f"client={self._owner.name}, "
            f"id=****{last4}, "
            f"status={self._status.value}, "
            f"balance={self._balance:.2f} {self._currency.value}, "
            f"portfolio={self.portfolio_value:.2f}, "
            f"growth={self._expected_yearly_growth:.2f}"
            f")"
        )

    @staticmethod
    def _validate_growth_rate(rate: Decimal) -> Decimal:
        try:
            val = Decimal(str(rate))
        except (TypeError, ValueError, InvalidOperation):
            raise InvalidOperationError("Expected yearly growth must be a number.")
        return val
