from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from banking.errors import InvalidOperationError

MONEY_QUANT = Decimal("0.01")


def to_money(amount: Decimal) -> Decimal:
    try:
        value = Decimal(str(amount))
    except (TypeError, ValueError, InvalidOperation):
        raise InvalidOperationError("Amount must be a number.")
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def validate_amount(amount: Decimal, allow_zero: bool = False) -> Decimal:
    value = to_money(amount)
    if value < 0:
        raise InvalidOperationError("Amount cannot be negative.")
    if not allow_zero and value == 0:
        raise InvalidOperationError("Amount must be greater than zero.")
    return value
