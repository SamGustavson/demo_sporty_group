from selenium.webdriver.common.by import By


class BetLocators:
    ANY_MATCH_CARD = (By.CSS_SELECTOR, "[id^='match-card-']")
    HEADER_BALANCE = (By.ID, "header-balance")
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")
    SLIP_TEAMS = (By.CLASS_NAME, "betSelectionTeams")
    SLIP_ODDS = (By.CLASS_NAME, "betSelectionOdds")
    SLIP_PAYOUT = (By.ID, "bet-slip-potential-payout")
    RECEIPT_BET_ID = (By.ID, "modal-success-bet-id")
    RECEIPT_MATCH = (By.ID, "modal-success-match")
    RECEIPT_STAKE = (By.ID, "modal-success-stake")
    RECEIPT_ODDS = (By.ID, "modal-success-odds")
    RECEIPT_PAYOUT = (By.ID, "modal-success-payout")
    ERROR_MODAL = (By.XPATH, "//*[normalize-space(text())='Something went wrong']")