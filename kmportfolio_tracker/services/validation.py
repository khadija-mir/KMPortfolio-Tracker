from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from kmportfolio_tracker.errors import InvalidAmountError


# Convert an input into a Decimal + ensure valid finite number
def to_decimal(value, label):
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise InvalidAmountError(f"{label} must be a number.")
    # Reject values like NaN and Infinity because they aren't valid amounts
    if not amount.is_finite():
        raise InvalidAmountError(f"{label} must be a finite number.")
    return amount

# Round monetary amounts to cents using standard half-up rounding
def round_to_cents(amount):
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

# Round quantities and share prices to four decimal places
def round_to_four_places(value):
    return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)