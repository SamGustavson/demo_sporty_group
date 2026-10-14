import re
from decimal import Decimal

_AMOUNT = re.compile(r"-?\d+(?:\.\d+)?")


def parse_amount(text: str) -> Decimal:
    """'€19.50' -> Decimal('19.50'), 'Odds: 1.95' -> Decimal('1.95')."""
    found = _AMOUNT.search(text.replace(",", ""))
    if found is None:
        raise ValueError(f"No number found in {text!r}")
    return Decimal(found.group())


