"""Business rules of the application under test."""
from enum import StrEnum, IntEnum

# Spec conflict: Business Rules say the minimum stake is EUR 1.00, the validation table says 1.01.
# 1.00 is used until the product owner clarifies.
MIN_STAKE = 1.00   #TODO
MAX_STAKE = 100.00
STARTING_BALANCE = 125.50
CURRENCY = "EUR"

# Error codes returned by POST /api/place-bet (HTTP 422 unless noted)
ERROR_STAKE_MIN = "invalid_stake_min"
ERROR_STAKE_MAX = "invalid_stake_max"
ERROR_STAKE_PRECISION = "invalid_stake_precision"
ERROR_STAKE_TYPE = "invalid_stake_type"
ERROR_SELECTION = "invalid_selection"

class Selection(StrEnum):
    HOME = "HOME"
    DRAW = "DRAW"
    AWAY = "AWAY"

class HttpStatus(IntEnum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
