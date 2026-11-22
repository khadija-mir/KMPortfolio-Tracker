# KMPortfolio-Tracker

This is a command-line app that intends to track investment portfolios. 
You can create portfolios for different strategies, add/buy/sell assets 
at the current price (set by you for now), and observe gains and losses. As we are not connected to a database for this assignment, memory does not persist when the app closes (0 or Ctrl+C)

*Setup and Running the App*
I use Windows; thus, these steps align with Windows PowerShell
1. Clone repo and go into project folder
   git clone https://github.com/khadija-mir/KMPortfolio-Tracker.git
   cd KMPortfolio-Tracker
2. Create + activate venv
   python -m venv .venv
   .venv\Scripts\Activate.ps1
3. Install requirements for libraries/packages with their versions  
    (specifically rich for console output)
    pip install -r requirements.txt
4. Run app from project folder: 
       python -m kmportfolio_tracker.main
App will write to log (app.log)

*Package Layout*
All code lives in kmportfolio_tracker package
**Entry Point and Interface**
-main.py: sets up logging and starts the app
-cli.py: shows the menu, asks for input, and displays results (no business rules)
**models/** ***objects needed***
-asset.py: an asset with a ticker and a name
-portfolio.py: a portfolio with its name, strategy, positions, trade history, and realized gain/loss
-position.py: shares of one asset in one portfolio, with average cost
**service/** ***business logic + calcs***
-asset_service.py: adding, finding, and listing assets
-pricing_service.py: current prices, kept separate from assets
-cash_service.py: the shared cash balance
-portfolio_service.py: creating, selecting, and deleting portfolios, plus the portfolio report
-trading_service.py: buying and selling in the selected portfolio
**errors/** ***errors***
-base_error.py: the base error all others build on
-asset_errors.py: duplicate asset, asset not found
-portfolio_errors.py: duplicate portfolio, not found, none selected, not empty
-trading_errors.py: invalid quantity, position not found, not enough shares
-cash_errors.py: not enough cash
-validation_errors.py: invalid amounts, missing required input

*Design Decisions*
1. Are fractional shares allowed? 
1a. Yes. Quantities are stored as Decimal, so a user can buy 0.5 shares. This matches brokers' current offers. 

2. Is aapl the same asset as AAPL? 
2a. Yes. Tickers are converted to uppercase when added or looked up. On exchanges, tickers are usually capitalized, so we will continue this convention and also mitigate duplication. Portfolio names follow the same idea: Tech and tech are the same portfolio, but the name is shown the way it was first typed. User would be informed that the name was already taken, and that they should select that folder instead (this does not apply to tickers though)

3. Do fully sold positions still appear in the portfolio view? 
3a. No, the holdings table only shows assets the portfolio currently owns. Gains from sold assets are still included in the realized gain total, so the totals remain accurate. However, the table no longer shows which sold asset each gain came from.

4. How does the portfolio view handle an asset with no current price?
4a. If an asset has no current price, its price shows as "Not set," and its market value and unrealized gain show as "Unavailable." The portfolio totals for market value and unrealized gain also show as "Unavailable," along with a message listing the tickers that need prices. Showing a total that excludes some assets could be misleading, so the app waits until all prices are set. Realized gains are still shown because they don't depend on current prices.

5. Which errors does the user see, and which are only written to the log?
- Business rule errors: If a rule is broken, such as adding a duplicate asset, having insufficient cash, or selling more than you own, the app displays a clear message and keeps running. These errors are logged as warnings.
- Invalid input: If the user enters letters instead of numbers or leaves a field empty, the app asks them to try again. These aren't logged because no operation was attempted.
- Unexpected errors: The app displays a short, friendly message to the user and saves the full error details in app.log.
- Successful operations: Actions such as creating, buying, selling, and depositing are logged at the info level.

## Future Considerations
- rename the 'models' folder to 'domain' as it holds domain objects
    - described on 10.21 class
- store trade date
- store trade id
- store everything mentioned on 10.21 if not already implemented
