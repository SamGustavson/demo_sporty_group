# Sporty QA Automation Framework

A small, risk-focused framework for the Sporty Group QA take-home assignment. It uses **Python + pytest + Selenium + requests + Poetry** and includes the required test plan, execution-record template, and strategy note.


# Project Structure

```text
sporty-qa-framework/
├── core/
│   ├── config.py
│   ├── api/
│   │   └── client.py
│   └── ui/
│       ├── driver_factory.py
│       └── pages/
│           └── betting_page.py
├── tests/
│   ├── conftest.py
│   ├── api/
│   │   └── test_bet_validation.py
│   └── ui/
│       └── test_single_bet_journey.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── TEST_PLAN_SINGLE_BET_PLACEMENT.md
├── TEST_RESULTS_BUG_REPORT.md
└── STRATEGY_AND_RECOMMENDATIONS.md
```

## Scope and deliverables

- `TEST_PLAN_SINGLE_BET_PLACEMENT.md` — six prioritized scenarios with rationale, steps and expected results.
- `TEST_RESULTS_BUG_REPORT.md` — top-three execution record, exploratory checklist and bug-report template.
- `STRATEGY_AND_RECOMMENDATIONS.md` — automation rationale, manual coverage and scale recommendations.
- `tests/ui/test_single_bet_journey.py` — critical single-bet UI journey.
- `tests/api/test_bet_validation.py` — API validation for a below-minimum stake.
- `core/` — configuration, API client, Chrome factory and Page Object.

## Prerequisites

- Python 3.12+
- Poetry
- Desktop Google Chrome
- Network access to the assignment application

The assignment requires Python 3, Selenium WebDriver, pytest, requests and current desktop Chrome. Poetry and Ruff are additional tooling.

## Setup

```bash
poetry install
cp .env.example .env
```

Set `SPORTY_USER_ID` in `.env` to the candidate ID provided for the assignment. The current example file uses the ID supplied in the task conversation. Do not commit `.env`.

```dotenv
QA_BASE_URL=https://qae-assignment-tau.vercel.app
QA_USER_ID=<user-id>
QA_HEADLESS=true
QA_TIMEOUT_SECONDS=10
```

## Run

Run API test:

```bash
poetry run pytest tests/api -m api
```

Run UI test (Chrome must be installed):

```bash
poetry run pytest tests/ui -m ui
```

Run smoke tests or all tests:

```bash
poetry run pytest -m smoke
poetry run pytest
```

Run lint/format checks:

```bash
poetry run ruff check core tests
poetry run ruff format core tests --check
```

## Important execution notes

- The UI test resets the assigned user's balance before running. The assignment's reset endpoint is state-changing; use only the test user assigned to you.
- The application has a shared user balance. Do not run multiple tests in parallel with the same user ID.
- The UI locators use accessible text and fallback selectors because the supplied specification does not define DOM selectors or `data-testid` attributes. If the live DOM differs, update `core/ui/pages/betting_page.py` after inspecting the page.
- The spec has a discrepancy: minimum stake is €1.00 in Business Rules and UI copy, but €1.01 in the Validation Rules table. The UI test uses €1.01; the API negative test uses €0.50 to avoid ambiguity.
- Tests have **not** been executed against the live app in this workspace. Do not report them as passing until run locally. Add observed outcomes and evidence to `TEST_RESULTS_BUG_REPORT.md`.

## API contract used

- `GET /api/matches`
- `GET /api/balance`
- `POST /api/place-bet`
- `POST /api/reset-balance`

All API requests include `x-user-id`, as required by the specification.

## Design

- **Page Object Model:** UI selectors and actions are kept out of the test body.
- **API client:** shared session and endpoint methods are isolated from assertions.
- **Fixtures:** browser lifecycle and balance reset are handled by pytest fixtures.
- **Configuration:** secrets/user context and execution options are environment-driven.


# Notes
## Tools and Technologies

* Requests — for sending HTTP requests and testing API endpoints.
* python-dotenv — python-dotenv** to load `QA_USER_ID` from `.env` instead of requiring it
  to be exported manually every session.
* jsonschema — for validating API response structures against JSON Schema.
* Ruff — for fast Python linting and maintaining consistent code quality.
* Poetry — for dependency management, virtual environments, and project configuration.

We use **Poetry** for dependency management and virtual environment handling. It provides several key benefits for our automation framework:

* **Predictable Runs (`poetry.lock`):** Guarantees that the exact same versions of all packages (Pytest, Selenium, etc.) are installed both locally and on CI/CD. This prevents test failures caused by accidental background dependency updates.
* **Automated Environment Management:** Poetry automatically creates and isolates the virtual environment, removing the need to manually create and activate `venv`.
* **Clean Dependency Removal:** When a package is removed, Poetry automatically cleans up its unused sub-dependencies, keeping the environment clean and lightweight.
* **Dependency Grouping:** Clear separation between core testing packages and development tools (like linters, formatters, or type checkers).
* **Single Configuration Hub (`pyproject.toml`):** Replaces multiple configuration files by keeping settings for Poetry, Pytest, and other tools in one organized place.


## CI/CD Direction

CI should use direct Poetry commands:

```yaml
- run: poetry install
- run: poetry run pytest tests/api -m api
- run: poetry run pytest tests/ui -m ui
- run: poetry run ruff check core tests
```

For UI tests, CI should provide Chrome and run in headless mode.
