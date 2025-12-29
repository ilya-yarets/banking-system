from banking.accounts.base import BankAccount
from decimal import Decimal

from banking.money import MONEY_QUANT
from banking.errors import InsufficientFundsError, InvalidOperationError


class PremiumAccount(BankAccount):
    def __init__(
        self,
        *,
        overdraft_limit: Decimal = Decimal("0.00"),
        withdraw_fee: Decimal = Decimal("0.00"),
        max_withdraw_per_txn: Decimal = Decimal("10000.00"),
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._overdraft_limit = self._validate_amount(overdraft_limit, allow_zero=True)
        self._withdraw_fee = self._validate_amount(withdraw_fee, allow_zero=True)
        self._max_withdraw_per_txn = self._validate_amount(
            max_withdraw_per_txn, allow_zero=False
        )

    @property
    def overdraft_limit(self) -> Decimal:
        return self._overdraft_limit

    @property
    def withdraw_fee(self) -> Decimal:
        return self._withdraw_fee

    @property
    def max_withdraw_per_txn(self) -> Decimal:
        return self._max_withdraw_per_txn

    def withdraw(self, amount: Decimal) -> None:
        self._check_can_operate()
        amount_val = self._validate_amount(amount)
        if amount_val > self._max_withdraw_per_txn:
            raise InvalidOperationError("Withdraw amount exceeds max_withdraw_per_txn.")
        total_debit = (amount_val + self._withdraw_fee).quantize(MONEY_QUANT)
        if self._balance - total_debit < -self._overdraft_limit:
            raise InsufficientFundsError("Overdraft limit exceeded.")
        self._balance = (self._balance - total_debit).quantize(MONEY_QUANT)

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
