# Test Plan — Single Bet Placement

Manual test plan for the **Single Bet Placement** feature of the Sports Betting QA application. Scenarios are ordered by risk: the three highest-priority scenarios (TC-01 to TC-03) are the ones executed in `BUG_REPORTS.md`.

---

## 1. Document Information

| Field | Value |
|---|---|
| Feature | Single Bet Placement |
| Application | `https://qae-assignment-tau.vercel.app/?user-id=<your-user-id>` |
| Platform | Desktop web, latest Chrome |
| Sport / event type | Football, upcoming (pre-match) events only |
| Bet type | Single bet only |
| Author | `<your name>` |
| Date | 2026-10-09 |
| Version | v1.0 |

---

## 2. Scope

**In scope**

- Match list and odds selection (1 / X / 2)
- Bet slip: stake entry, potential payout, balance, Place Bet
- Stake validation in the UI and in the API
- Place bet flow: loading state, success receipt, error modal (Rebet / Close / X)
- Balance behaviour in the header and the bet slip
- Match rules: upcoming events only, one active bet at a time

**Out of scope**

- Live betting, multi-bets / accumulators, other sports
- Mobile-specific UX, currencies other than EUR

Date and odds filters, layout and copy are not scenarios in this plan; they are left to exploratory checks (findings go to section 7 of `BUG_REPORTS.md`).

---

## 3. Environment and Test Data

| Item | Value |
|---|---|
| Browser | Latest desktop Chrome, DevTools open on the Network tab |
| API tools | Swagger UI at `/api/docs`, browser DevTools |
| Required API header | `x-user-id: <your-user-id>` |
| Initial balance | €125.50 (restore with `POST /api/reset-balance` before every scenario) |
| Upcoming match | Any match whose kickoff date is in the future. The list also contains matches with a `PAST` badge: do not use them unless the scenario says so |
| Valid stakes | `1.00`, `10.00`, `100.00` |
| Invalid stakes | `0.99`, `100.01`, `10.123`, `abc`, empty |

---

## 4. How Scenarios Were Prioritised

Priority follows **business impact × likelihood**. The feature moves real money, so anything that charges, credits or displays money incorrectly outranks cosmetic and filter issues.

| Priority | Meaning |
|---|---|
| Critical | Money is charged, lost or misstated for many users, or the core flow is blocked |
| High | An important rule or validation is broken, or exposure exists only for deliberate abuse |
| Medium | The feature works but a secondary flow or edge case misbehaves |
| Low | Minor visual or copy issue |

---

## 5. Scenario Overview

| ID | Title | Priority | Layer | Executed |
|---|---|---|---|---|
| TC-01 | Place a valid bet and verify slip, receipt and balance | Critical | UI + API | Yes |
| TC-02 | Stake above the available balance is blocked | Critical | UI + API | Yes |
| TC-03 | Rapid repeated Place Bet creates only one bet | Critical | UI + API | Yes |
| TC-04 | Stake limits and input format | High | UI + API | No |
| TC-05 | Bets on past matches are blocked | High | UI + API | No |
| TC-06 | Error modal: Rebet, Close and X | Medium | UI | No |

---

## 6. Scenarios

### TC-01 — Place a valid bet and verify slip, receipt and balance

| Field | Value |
|---|---|
| Priority | Critical |
| Layer | UI, cross-checked against the API response |
| Risk rationale | This is the revenue flow and it runs for every bet. A wrong payout, a wrong or missing deduction, or a receipt that disagrees with the slip misstates the user's money and corrupts every record built on that bet. |

**Steps**

1. Reset the balance, open the app and note the header balance (B0).
2. Pick an upcoming match and click the Home (`1`) odds. Note the odds (O) and the team order.
3. Enter stake `10.00`. Note the Potential Payout shown in the bet slip.
4. Click **Place Bet** and watch the button state.
5. Compare every field of the receipt with the slip. Open the `place-bet` response in the Network tab.
6. Close the receipt. Without reloading, read the balance in the header and the bet slip, then call `GET /api/balance`.

**Expected result**

- Slip payout equals stake × odds (for example 10.00 × 2.45 = €24.50).
- The button shows `Placing...` and the flow ends in exactly one outcome.
- The receipt shows Bet ID, match with the home team first, selection, stake, odds, potential payout and timestamp. Values are identical to the slip.
- Header balance and slip balance both equal B0 − 10.00 immediately, and match `GET /api/balance` and the `balance` field of the response.
- Closing the receipt returns to an empty bet slip.

---

### TC-02 — Stake above the available balance is blocked

| Field | Value |
|---|---|
| Priority | Critical |
| Layer | UI and API |
| Risk rationale | A negative balance means the operator is lending money for free. The rule must hold in both layers (spec 4.1) and across sequential bets, where a stale balance check would allow unlimited overdraft. |

**Steps**

1. Reset the balance (€125.50).
2. Place a valid bet with stake `100.00`. Remaining balance should be €25.50.
3. Select odds again and enter `25.51`: inside the €1–€100 limits, one cent above the balance. Note the warning and the Place Bet state.
4. If Place Bet is clickable, click it. Then send the same stake directly with `POST /api/place-bet` in Swagger.
5. Enter exactly `25.50` and place the bet.
6. Read the balance in the UI and from `GET /api/balance`.

**Expected result**

- `25.51`: the UI shows **Insufficient balance** and blocks placement; the API answers `422`.
- No receipt is shown for the rejected stake and the balance stays €25.50.
- `25.50` is accepted and the balance becomes €0.00.
- The balance never drops below zero.

---

### TC-03 — Rapid repeated Place Bet creates only one bet

| Field | Value |
|---|---|
| Priority | Critical |
| Layer | UI and API |
| Risk rationale | Double-clicks and impatient retries on a slow connection are common. Each extra accepted request charges the user for a bet they did not intend. The spec requires one active bet at a time and defines `409` for this case. |

**Steps**

1. Reset the balance, open the app and open DevTools → Network (filter `place-bet`).
2. Select odds and enter stake `2.00`.
3. Click **Place Bet** as fast as possible, 8–10 times.
4. Count the `place-bet` requests and note each status code and response body.
5. Count the receipts or modals shown. Read the header balance, the bet slip balance and `GET /api/balance`.
6. Repeat at API level: send two `POST /api/place-bet` requests at the same moment (two Swagger tabs or two parallel calls).

**Expected result**

- After the first click the button stays disabled (`Placing...`) and only one request is sent.
- Any further request that reaches the API is rejected with `409` and does not change the balance.
- One bet, one receipt: balance equals B0 − 2.00.
- The UI handles a `409` visibly and does not fail silently.

---

### TC-04 — Stake limits and input format

| Field | Value |
|---|---|
| Priority | High |
| Layer | UI and API |
| Risk rationale | The €1.00 / €100.00 limits, two-decimal precision and numeric-only rule control exposure per bet. Boundaries are where off-by-one defects live, and the spec contradicts itself on the minimum (see section 7). |

**Steps**

1. For each stake `0.99`, `1.00`, `100.00`, `100.01`, `10.123`, `abc` and empty: enter it in the bet slip and note the message and the Place Bet state.
2. Repeat the values the input accepts directly in the API with `POST /api/place-bet`.
3. After every rejected stake, check that the balance is unchanged.

**Expected result**

- `0.99` shows "Minimum stake is €1.00"; `100.01` shows "Maximum stake is €100.00".
- `1.00` and `100.00` are accepted, with the balance debited by exactly the stake.
- `10.123` is rejected or cannot be typed; non-numeric input is rejected; an empty stake blocks Place Bet.
- The API answers `422` with an error code matching the broken rule.

---

### TC-05 — Bets on past matches are blocked

| Field | Value |
|---|---|
| Priority | High |
| Layer | UI and API |
| Risk rationale | Betting on an event whose result is known is a guaranteed win and a direct fraud vector. The spec allows upcoming events only, yet the list shows matches with a `PAST` badge. |

**Steps**

1. Find a match card with a `PAST` badge (or any `kickoffDate` earlier than today in `GET /api/matches`).
2. Try to click its odds buttons.
3. If they can be selected, enter `10.00` and place the bet.
4. Send the same match id directly with `POST /api/place-bet`.

**Expected result**

- Past matches are not shown in the upcoming list, or their odds cannot be selected.
- The API rejects the request with `422` and the balance is unchanged.

---

### TC-06 — Error modal: Rebet, Close and X

| Field | Value |
|---|---|
| Priority | Medium |
| Layer | UI |
| Risk rationale | Retry flows are where double charges come from, but the modal only appears when placement already failed, so fewer users reach it. |

**Steps**

1. Select odds and enter a valid stake.
2. In DevTools set the network to **Offline** and click **Place Bet**.
3. Check the modal text, then restore the network and click **Rebet**.
4. Trigger the failure again and click **Close**, then once more and click the top-right **X**.

**Expected result**

- The modal title is "Something went wrong" and the body suggests trying again.
- **Rebet** closes the modal and retries once; the balance is debited only if the retry succeeds.
- **Close** and **X** close the modal and clear the selection and stake.
- The failed attempt itself does not change the balance.

---

## 7. Assumptions and Specification Ambiguities

| # | Topic | Assumption used in this plan |
|---|---|---|
| 1 | Minimum stake is €1.00 in Business Rules and UI copy, but €1.01 in validation rule 4.1 | €1.00 is valid. Needs confirmation from the product owner. |
| 2 | "Only one bet can be active at a time" can mean one selection in the slip or one request in flight | Both are tested (TC-03). |
| 3 | The spec defines `409` for the API but no UI behaviour for it | The UI must make the rejection visible and must not charge twice. |
| 4 | `kickoffDate` is date-only and the spec does not say whether today's matches count as upcoming | Only matches dated before today are treated as past. |
| 5 | The spec says the stake is deducted on success but not when the displayed balance refreshes | The displayed balance updates immediately, without a page reload. |
