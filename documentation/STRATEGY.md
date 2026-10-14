# Strategy and Recommendations

## 1. Why These Two Tests Were Automated

| Test | Layer | Why it was chosen |
|---|---|---|
| `test_user_places_a_single_bet_and_sees_consistent_slip_receipt_and_balance` | UI e2e | The place-bet journey is the revenue flow and runs for every bet. One test crosses the match list, bet slip, placement, receipt and both balances, and compares them with values taken from the API. It checks three of the defects found manually: the wrong receipt payout, the balance not refreshing and the reversed team order. |
| `tests/api/test_bet_validation.py` (stake-limit checks) | API | Stake rules are enforced in the API, so a UI-only check can be bypassed by any client. The test is fast, needs no browser, runs on a table of boundary values (€1.00, €100.00 and the values around them) and checks the side effect that matters: a rejected stake leaves the balance untouched and an accepted one debits it exactly once. Responses are also validated against JSON schemas. |

**Considered and not automated first**

- **Overdraft check (TC-02):** the strongest next candidate. It is deterministic at API level, but the assignment caps automation at two tests, so it heads the backlog.
- **Concurrent submit (TC-03):** valuable, but it needs controlled timing and is better written as a dedicated API concurrency test once the backend guard is fixed.
- **Filters and layout:** low money risk, so manual checks are enough for now.

## 2. What Was Left Manual and Why

| Area | Reason |
|---|---|
| Rapid repeated Place Bet (TC-03) | Depends on timing and on what the Network tab shows; a human finds and explains it faster. Automate at API level later. |
| Error modal, Rebet / Close / X (TC-06) | The failure cannot be triggered from the product itself; it needs network blocking or a test hook. |
| Date and odds filters | Low financial risk and the markup changes often, so UI tests would be fragile for little value. |
| Layout, copy, modal behaviour | Quick exploratory checks give more value than scripted ones at this size. |
| Spec contradictions | A decision for the product owner, not a test (see recommendation 3). |

## 3. Top Recommendations if the Project Scales

### 3.1 CI/CD and test data

- Run the API tests on every pull request and the UI smoke test on every merge to the test environment. Run the full suite before a release.
- The balance is shared per user, so every run needs its own user id and a `reset-balance` step in a fixture. Parallel runs on one user would corrupt each other.
- Ask for test-only support: a way to seed matches with past and future kickoff times, and a way to inject failures. That makes TC-05 and TC-06 automatable.

### 3.2 More test layers

- **Contract tests** generated from the OpenAPI JSON at `/api/docs?format=json`, so schema drift fails the build. The two JSON schemas already used in the API test are the first step.
- **Concurrency and idempotency tests** for `place-bet`, including parallel requests, double submit and Rebet. This is the area where the most serious bugs were found (BUG-01, BUG-02).
- Stable `data-testid` attributes on the match list, bet slip and modals, to make UI tests resilient.

### 3.3 Specification and backend clarifications

- Settle the minimum stake: €1.00 in Business Rules and UI copy against €1.01 in validation rule 4.1.
- Define the UI behaviour for a `409` response and what "one bet at a time" means (one selection or one request in flight).
- Define when the displayed balance refreshes and what counts as an upcoming match (date-only `kickoffDate`, no time or time zone).
- Backend: make the balance check and debit one atomic step, add an idempotency key to `place-bet`, return `EUR` as the currency, and reject past matches.
