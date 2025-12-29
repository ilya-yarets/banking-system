from banking.accounts.base import BankAccount
from banking.errors import InsufficientFundsError, InvalidOperationError


class InvestmentAccount(BankAccount):
    def __init__(
        self,
        *,
        portfolios: dict | None = None,
        expected_yearly_growth: float = 0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if expected_yearly_growth < 0:
            raise InvalidOperationError("Expected yearly growth cannot be negative.")
        self._expected_yearly_growth = float(expected_yearly_growth)
        self._portfolios = {"stocks": 0.0, "bonds": 0.0, "etf": 0.0}
        if portfolios:
            for asset_type, value in portfolios.items():
                if asset_type not in self._portfolios:
                    raise InvalidOperationError(
                        "Portfolio asset must be one of: stocks, bonds, etf."
                    )
                self._validate_amount(value, allow_zero=True)
                self._portfolios[asset_type] = float(value)

    def project_yearly_growth(self, years: int = 1) -> float:
        if years < 0:
            raise InvalidOperationError("Years cannot be negative.")
        base = self._balance + self.portfolio_value
        return base * ((1 + self._expected_yearly_growth) ** years)

    def withdraw(self, amount: float) -> None:
        self._check_can_operate()
        self._validate_amount(amount)
        if float(amount) > self._balance:
            raise InsufficientFundsError("Not enough balance to withdraw this amount.")
        self._balance -= float(amount)

    def add_asset(self, asset_type: str, amount: float) -> None:
        self._check_can_operate()
        if asset_type not in self._portfolios:
            raise InvalidOperationError("Asset type must be one of: stocks, bonds, etf.")
        self._validate_amount(amount)
        self._portfolios[asset_type] += float(amount)

    @property
    def portfolio_value(self) -> float:
        return sum(self._portfolios.values())

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
