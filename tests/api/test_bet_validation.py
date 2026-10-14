import pytest
from jsonschema import validate

from core.api.client import ApiClient
from core.constants import ERROR_STAKE_MIN, ERROR_STAKE_TYPE, ERROR_STAKE_MAX, ERROR_STAKE_PRECISION, HttpStatus, \
    MIN_STAKE, MAX_STAKE, CURRENCY

pytestmark = pytest.mark.api


@pytest.mark.usefixtures("clean_balance")
@pytest.mark.parametrize(
    "stake, expected_error" ,
    [
        pytest.param(0, ERROR_STAKE_MIN, id="zero"),
        pytest.param(-1, ERROR_STAKE_TYPE, id="negative"),
        pytest.param(0.50, ERROR_STAKE_MIN, id="just-below-min"),
        pytest.param(100.01, ERROR_STAKE_MAX, id="just-above-max"),
        pytest.param(11.234, ERROR_STAKE_PRECISION, id="three-decimals"),
        pytest.param("ten",ERROR_STAKE_TYPE ,id="non-numeric-string"),
        pytest.param(None, ERROR_STAKE_TYPE, id="missing-stake"),
    ],
)
def test_invalid_stake_is_rejected_and_balance_is_untouched(api: ApiClient, stake, expected_error):
    match = api.first_match()
    balance_before = api.balance_value()

    response = api.place_bet(match["id"], "HOME", stake)

    assert expected_error in response.text
    assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY, f"expected 422, got {response.status_code}: {response.text}"
    assert api.balance_value() == balance_before, "a rejected bet must not change the balance"


@pytest.mark.usefixtures("clean_balance")
@pytest.mark.parametrize("stake", [MIN_STAKE, MAX_STAKE], ids=["exact-min", "exact-max"])
def test_boundary_stake_is_accepted_and_debited(
    api: ApiClient, upcoming_match, balance_before, place_bet_success_schema, stake
):
    odds = upcoming_match["odds"]["home"]
    expected_balance = round(balance_before - stake, 2)

    response = api.place_bet(upcoming_match["id"], "HOME", stake)

    assert response.status_code == HttpStatus.OK, response.text
    body = response.json()
    validate(instance=body, schema=place_bet_success_schema)

    expected = {
        "matchId": upcoming_match["id"],
        "selection": "HOME",
        "stake": stake,
        "odds": odds,
        "payout": round(stake * odds, 2),
        "balance": expected_balance,
        "currency": CURRENCY,
    }
    assert {key: body[key] for key in expected} == expected
    assert round(api.balance_value(), 2) == expected_balance, "GET /balance must match the debit"
