from banking.accounts.base import BankAccount
from banking.errors import InsufficientFundsError, InvalidOperationError


class PremiumAccount(BankAccount):
    def __init__(
        self,
        *,
        overdraft_limit: float = 0.0,
        withdraw_fee: float = 0.0,
        max_withdraw_per_txn: float = 10_000.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._validate_amount(overdraft_limit, allow_zero=True)
        self._validate_amount(withdraw_fee, allow_zero=True)
        self._validate_amount(max_withdraw_per_txn, allow_zero=False)
        self._overdraft_limit = float(overdraft_limit)
        self._withdraw_fee = float(withdraw_fee)
        self._max_withdraw_per_txn = float(max_withdraw_per_txn)

    @property
    def overdraft_limit(self) -> float:
        return self._overdraft_limit

    @property
    def withdraw_fee(self) -> float:
        return self._withdraw_fee

    @property
    def max_withdraw_per_txn(self) -> float:
        return self._max_withdraw_per_txn

    def withdraw(self, amount: float) -> None:
        self._check_can_operate()
        self._validate_amount(amount)
        amount_val = float(amount)
        if amount_val > self._max_withdraw_per_txn:
            raise InvalidOperationError("Withdraw amount exceeds max_withdraw_per_txn.")
        total_debit = amount_val + self._withdraw_fee
        if self._balance - total_debit < -self._overdraft_limit:
            raise InsufficientFundsError("Overdraft limit exceeded.")
        self._balance -= total_debit

    def get_account_info(self) -> dict:
        info = super().get_account_info()
        info.update(
            {
                "overdraft_limit": self._overdraft_limit,
                "withdraw_fee": self._withdraw_fee,
                "max_withdraw_per_txn": self._max_withdraw_per_txn,
            }
        )
        return info

    def __str__(self) -> str:
        last4 = self._id[-4:] if self._id else "????"
        return (
            f"PremiumAccount("
            f"client={self._owner.name}, "
            f"id=****{last4}, "
            f"status={self._status.value}, "
            f"balance={self._balance:.2f} {self._currency.value}, "
            f"overdraft={self._overdraft_limit:.2f}, "
            f"fee={self._withdraw_fee:.2f}"
            f")"
        )
