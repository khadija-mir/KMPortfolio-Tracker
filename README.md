# KMPortfolio-Tracker
 
KMPortfolio-Tracker is a command-line portfolio tracker that lets users manage cash, portfolios, assets, and trades. It tracks holdings, average cost, realized gains, and unrealized gains. For Assignment 2, I updated the application to use a MySQL database so that information is saved between sessions. I also added automated tests using pytest and an isolated SQLite database.
 
## Setup and Running the App
 
### 1. Clone the repository
 
Open PowerShell and run:
 
```powershell
git clone https://github.com/khadija-mir/KMPortfolio-Tracker.git
cd KMPortfolio-Tracker
```
 
### 2. Set up the MySQL database
 
Install and start MySQL Community Server 9.7.
 
Open MySQL Workbench or the MySQL command line and create the database and user:
 
```sql
CREATE DATABASE portfolio_tracker;
 
CREATE USER 'tracker'@'localhost' IDENTIFIED BY 'your-password';
 
GRANT ALL PRIVILEGES ON portfolio_tracker.* TO 'tracker'@'localhost';
 
FLUSH PRIVILEGES;
```
 
You can replace `your-password` with a password of your choice.
 
### 3. Configure the environment variables
 
Copy the example environment file:
 
```powershell
Copy-Item .env.example .env
```
 
Open `.env` and update the values to match your MySQL setup. Make sure the password matches the one you used when creating the MySQL user.
 
The application uses these environment variables:
 
```text
DB_HOST=localhost
DB_PORT=3306
DB_NAME=portfolio_tracker
DB_USER=tracker
DB_PASSWORD=your-password
```
 
The `.env` file contains local database credentials and should not be committed to Git. The `.env.example` file is included so that someone setting up the project knows which variables are needed.
 
### 4. Create a virtual environment and install dependencies
 
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
 
### 5. Run the application
 
```powershell
python -m kmportfolio_tracker.main
```
 
The application creates the database tables automatically when it starts. Application logs are saved in `app.log`.
 
## Running the Tests
 
The tests use pytest and an in-memory SQLite database instead of the actual MySQL database.
 
Run the test suite with:
 
```powershell
python -m pytest
```
 
The tests create a fresh database for each test, so they do not use or modify my actual MySQL data.
 
To check code quality with Ruff, run:
 
```powershell
ruff check
```
 
## Package Layout
 
The project is organized into separate packages so that each part of the application has its own responsibility.
 
- `models/` – Defines the database tables and the Position class.
- `storage/` – Handles database operations, such as adding, retrieving, updating, and deleting records.
- `services/` – Contains the application's business logic and validation.
- `errors/` – Contains custom exceptions used by the application.
- `tests/` – Contains automated tests for the business rules and calculations.
- `cli.py` – Handles the command-line interface and user interaction.
- `database.py` – Sets up the database engine, sessions, and transactions.
- `main.py` – Starts the application and handles startup and shutdown.
## Design Decisions
 
### 1. Where do you store current prices and why?
 
I decided to store current asset prices in a separate `prices` table instead of keeping them in memory. Each asset has one current price record, and updating a price replaces the previous value.
 
This means prices are still available when the application is restarted. I also used a unique constraint on `asset_id` so that an asset cannot have multiple current price records.
 
### 2. How many decimal places do you use for cash, quantities, and prices? Where do you round, and why?
 
I use two decimal places for cash balances and four decimal places for quantities and prices.
 
I chose four decimal places for quantities and prices because the application supports fractional shares. Cash is stored to two decimal places because it represents money.
 
Purchase costs and sale proceeds are rounded to the nearest cent using `ROUND_HALF_UP` before checking available funds or updating the cash balance. I perform this rounding in Python rather than relying on the database so that the calculations behave consistently when using MySQL and SQLite.
 
For example, buying 3 shares at $33.3333 results in a total cost of $99.9999, which is rounded to $100.00 before the cash balance is checked and updated. Average cost is calculated from exact trade prices and not rounded.
 
### 3. Which of your business rules does the database itself enforce, in addition to the checks in your Python code, and why those?
 
I used database constraints as another layer of protection in case a bug skips a check in the Python code.
 
- **Primary keys:** Give each record a unique identifier.
- **UNIQUE:** Prevents duplicate asset tickers, portfolio names, and multiple price records for the same asset.
- **NOT NULL:** Prevents required fields from being left empty. The selected portfolio reference is nullable because an account does not always have to have a portfolio selected.
- **Foreign keys:** Maintain relationships between accounts, portfolios, assets, transactions, and prices.
- **ENUM:** Restricts transaction sides to `buy` or `sell` in MySQL.
I chose these because they represent basic facts about the data that should always be true. Other rules, such as preventing negative cash balances or selling more shares than owned, depend on calculations across records, so those checks stay in the services.
 
One difference I had to account for in testing is that SQLite does not enforce the `ENUM` constraint the same way MySQL does. SQLAlchemy's default SQLite handling does not create a CHECK constraint for this ENUM unless it is specifically enabled.
 
### Other Design Choices
 
I also made a few decisions about how the application handles portfolios and transactions:
 
- The selected portfolio is stored in the `account` table so that the selection is preserved when the application is restarted.
- A portfolio can only be deleted if it has no shares remaining. When a portfolio is deleted, its transactions are deleted first. If it was selected, the selection is cleared as part of the same database transaction.
- Portfolio names are looked up without considering capitalization, so selecting a portfolio using `growth` or `GROWTH` finds the same portfolio.
## Design Decisions Carried Over from Assignment 1
 
I kept several of the original Assignment 1 business rules when updating the application.
 
1. **Fractional shares:** Users can buy and sell fractional shares, such as 0.5 shares.
2. **Ticker and portfolio name formatting:** Asset tickers are stored in uppercase. Portfolio names are looked up without considering capitalization, but their original capitalization is preserved.
3. **Fully sold positions:** Positions with zero shares are not shown in the current holdings, but their realized gains are still included in the portfolio's realized gain total.
4. **Missing prices:** If an asset does not have a current price, its price is shown as "Not set." Its market value and unrealized gain cannot be calculated, so the overall market value and unrealized gain totals are shown as "Unavailable." The missing ticker is listed, but realized gains are still calculated.
5. **Error handling:** Expected business errors are displayed to the user and logged as warnings. Invalid input is handled by prompting the user again. Unexpected errors are shown with a general message, while the details are saved in `app.log`. Successful operations are logged as informational messages.
## How the Tests Work
 
I used pytest to test the application's business rules without connecting to my actual MySQL database.
 
The `empty_db` fixture in `conftest.py` creates a fresh in-memory SQLite database for each test. It temporarily replaces the application's `get_engine()` function so that the services use the test database instead of MySQL. I also enabled SQLite foreign key enforcement so that foreign key relationships are checked during testing.
 
This makes the tests independent of one another and ensures that each test starts with a clean database. It also means I can run the tests without changing any of my actual portfolio data.
 
For portfolio report tests, I used a known current price as a stand-in instead of relying on an external price source. This makes the expected market values and gains predictable.
 
### A Bug I Introduced on Purpose
 
For one of my tests, I deliberately removed the rounding step from the purchase calculation in `trading_service.py`.
 
The test was:
 
`test_buy_is_allowed_when_rounded_cost_equals_cash`
 
It checks what happens when the purchase cost is slightly above the available cash before rounding, but exactly equal to the available cash after rounding.
 
For example, buying 3 shares at $33.3334 gives an unrounded cost of $100.0002. After rounding to cents, the actual amount charged is $100.00. If the application checks the unrounded amount against a $100.00 cash balance, it incorrectly raises an `InsufficientFundsError`.
 
When I removed the rounding step, this test failed while the other 47 tests passed:
 
```text
FAILED tests/test_trading_service.py::test_buy_is_allowed_when_rounded_cost_equals_cash
E InsufficientFundsError: Insufficient funds. Available cash: $100.00; amount needed: $100.00020000.
1 failed, 47 passed
```
 
The failure showed that the application was checking the unrounded purchase cost against the available cash. After restoring the rounding step, all 48 tests passed.
 
This also showed me why testing boundary cases matters. My original rounding test did not catch this issue, so I added a test that specifically checks the situation where rounding changes whether a purchase should be allowed.