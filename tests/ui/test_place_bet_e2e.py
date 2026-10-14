"""UI e2e: the core journey - pick odds, set a stake, place the bet, check the result.

Expected values come from the API (the source of truth), never from the UI under test.
Each stage compares everything in one assert, so a failure lists every wrong field at once.
"""

import re
from decimal import Decimal

import pytest
from core.constants import Selection
from core.ui.pages.betting_page import BettingPage, Slip

pytestmark = [pytest.mark.ui, pytest.mark.smoke]

STAKE = Decimal("10.00")
BET_ID_FORMAT = re.compile(r"#B-\d+")


@pytest.fixture
def page(driver) -> BettingPage:
    return BettingPage(driver).open()

@pytest.mark.usefixtures("clean_balance")
def test_user_places_a_single_bet_and_sees_consistent_slip_receipt_and_balance(
    page: BettingPage, api, upcoming_match, balance_before
):
    # Arrange
    match = f"{upcoming_match['homeTeam']} vs {upcoming_match['awayTeam']}"

    odds = Decimal(str(upcoming_match["odds"][Selection.HOME.lower()]))
    payout = (STAKE * odds).quantize(Decimal("0.01"))
    start_balance = Decimal(str(balance_before))
    assert page.header_balance() == start_balance, (
        "header balance must match the API before betting"
    )

    # Act: pick the outcome and enter the stake
    page.select_odds(upcoming_match["id"], Selection.HOME)
    page.enter_stake(STAKE)

    # Assert: the bet slip shows what the user picked
    assert page.read_slip() == Slip(teams=match, odds=odds, payout=payout)

    # Act: place the bet
    page.place_bet()
    receipt = page.wait_for_receipt()
    header_balance = page.wait_for_header_balance(start_balance - STAKE)

    # Assert: receipt, header balance and server balance all agree with the slip
    assert {
        "bet_id_format_ok": bool(BET_ID_FORMAT.fullmatch(receipt.bet_id)),
        "match": receipt.match,
        "stake": receipt.stake,
        "odds": receipt.odds,
        "payout": receipt.payout,
        "header_balance": header_balance,
        "api_balance": Decimal(str(api.balance_value())),
    } == {
        "bet_id_format_ok": True,
        "match": match,
        "stake": STAKE,
        "odds": odds,
        "payout": payout,
        "header_balance": start_balance - STAKE,
        "api_balance": start_balance - STAKE,
    }
