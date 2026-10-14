"""Page Object for the betting UI: match list, bet slip and bet receipt modal.

Locators are the app's own element ids (e.g. ``odds-<matchId>-home``, ``bet-slip-stake-input``).
If the app changes its markup, this is the only file that needs to change.
"""

import platform
from dataclasses import dataclass
from decimal import Decimal

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import settings
from core.ui.pages.base_page import BasePage
from core.ui.pages.locators import BetLocators
from core.ui.util import parse_amount


@dataclass(frozen=True)
class Slip:
    teams: str
    odds: Decimal
    payout: Decimal


@dataclass(frozen=True)
class Receipt:
    bet_id: str
    match: str
    stake: Decimal
    odds: Decimal
    payout: Decimal


class BettingPage(BasePage):


    def open(self) -> "BettingPage":
        self.driver.get(settings.ui_url)
        self.find_all(*BetLocators.ANY_MATCH_CARD)

        return self

    def header_balance(self) -> Decimal:
        return parse_amount(self._text(BetLocators.HEADER_BALANCE))

    def wait_for_header_balance(self, expected: Decimal) -> Decimal:
        """Give the header a moment to refresh; return what it shows, right or wrong."""
        try:
            self.wait.until(lambda _: self.header_balance() == expected)
        except TimeoutException:
            pass
        return self.header_balance()

    def select_odds(self, match_id: str, selection: str) -> None:
        """selection is the API value: HOME, DRAW or AWAY."""
        button = self.wait.until(
            EC.presence_of_element_located((By.ID, f"odds-{match_id}-{selection.lower()}"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        self.wait.until(EC.element_to_be_clickable(button)).click()

    def enter_stake(self, stake: Decimal) -> None:
        field = self.find(*BetLocators.STAKE_INPUT)
        select_all = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        # clear() is unreliable on controlled React inputs, so select all + delete instead
        field.send_keys(select_all + "a", Keys.BACKSPACE)
        field.send_keys(f"{stake:f}")

    def read_slip(self) -> Slip:
        return Slip(
            teams=self._text(BetLocators.SLIP_TEAMS),
            odds=parse_amount(self._text(BetLocators.SLIP_ODDS)),
            payout=parse_amount(self._text(BetLocators.SLIP_PAYOUT)),
        )

    def place_bet(self) -> None:
        self.find_clickable(*BetLocators.PLACE_BET_BUTTON).click()

    def wait_for_receipt(self) -> Receipt:
        """Wait for the single final outcome; an error modal fails with a clear message."""

        def outcome_shown(driver: WebDriver) -> bool:
            return bool(
                driver.find_elements(*BetLocators.RECEIPT_BET_ID)
                or driver.find_elements(*BetLocators.ERROR_MODAL)
            )

        try:
            WebDriverWait(self.driver, settings.timeout * 2).until(outcome_shown)
        except TimeoutException:
            raise AssertionError(
                "Neither a receipt nor an error modal appeared after Place Bet"
            ) from None

        if not self.driver.find_elements(*BetLocators.RECEIPT_BET_ID):
            raise AssertionError(
                "Error modal ('Something went wrong') shown instead of a receipt"
            )

        return Receipt(
            bet_id=self._text(BetLocators.RECEIPT_BET_ID),
            match=self._text(BetLocators.RECEIPT_MATCH),
            stake=parse_amount(self._text(BetLocators.RECEIPT_STAKE)),
            odds=parse_amount(self._text(BetLocators.RECEIPT_ODDS)),
            payout=parse_amount(self._text(BetLocators.RECEIPT_PAYOUT)),
        )

