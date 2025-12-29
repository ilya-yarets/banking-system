from banking.accounts.base import BankAccount
from banking.errors import InsufficientFundsError, InvalidOperationError


class SavingsAccount(BankAccount):

    def __init__(
        self,
        *,
        min_balance: float = 0.0,
        monthly_interest_rate: float = 0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._validate_amount(min_balance, allow_zero=True)
        self._validate_interest_rate(monthly_interest_rate)
        self._min_balance = float(min_balance)
        self._monthly_interest_rate = float(monthly_interest_rate)
        if self._balance < self._min_balance:
            raise InvalidOperationError("Initial balance cannot be below min_balance.")

    @property
    def min_balance(self) -> float:
        return self._min_balance

    @property
    def monthly_interest_rate(self) -> float:
        return self._monthly_interest_rate

    def apply_monthly_interest(self) -> None:
        self._check_can_operate()
        if self._monthly_interest_rate == 0:
            return
        self._balance += self._balance * self._monthly_interest_rate

    def withdraw(self, amount: float) -> None:
        self._check_can_operate()
        self._validate_amount(amount)
        if float(amount) > self._balance:
            raise InsufficientFundsError("Not enough balance to withdraw this amount.")
        if self._balance - float(amount) < self._min_balance:
            raise InvalidOperationError("Cannot withdraw: min_balance would be violated.")
        self._balance -= float(amount)

    def get_account_info(self) -> dict:
        info = super().get_account_info()
        info.update(
            {
                "min_balance": self._min_balance,
                "monthly_interest_rate": self._monthly_interest_rate,
            }
        )
        return info

    def __str__(self) -> str:
        last4 = self._id[-4:] if self._id else "????"
        return (
            f"SavingsAccount("
            f"client={self._owner.name}, "
            f"id=****{last4}, "
            f"status={self._status.value}, "
            f"balance={self._balance:.2f} {self._currency.value}, "
            f"min_balance={self._min_balance:.2f}, "
            f"rate={self._monthly_interest_rate:.4f}"
            f")"
        )

    @staticmethod
    def _validate_interest_rate(rate: float) -> None:
        try:
            val = float(rate)
        except (TypeError, ValueError):
            raise InvalidOperationError("Interest rate must be a number.")
        if val < 0:
            raise InvalidOperationError("Interest rate cannot be negative.")
