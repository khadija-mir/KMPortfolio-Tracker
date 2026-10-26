import logging
from decimal import Decimal, InvalidOperation

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from kmportfolio_tracker.errors import PortfolioTrackerError
from kmportfolio_tracker.service import (
    asset_service,
    pricing_service,
    portfolio_service,
    cash_service,
    trading_service,
)

logger = logging.getLogger(__name__)
console = Console()

MAIN_MENU = """
================================
     PORTFOLIO TRACKER
================================
1.  Add asset
2.  View assets
3.  Set current asset price
4.  Create portfolio
5.  View portfolios
6.  Select portfolio
7.  Delete portfolio
8.  View selected portfolio
9.  Deposit funds
10. Buy asset
11. Sell asset
12. View cash balance
0.  Exit
"""


def ask_text(prompt):
    while True:
        value = Prompt.ask(prompt).strip()

        if value:
            return value

        console.print(
            "[yellow]Input cannot be empty. Please try again.[/yellow]"
        )


def ask_decimal(prompt):
    while True:
        text = Prompt.ask(prompt).strip()

        try:
            value = Decimal(text)

            if not value.is_finite():
                raise InvalidOperation

            return value

        except InvalidOperation:
            console.print(
                f"[yellow]{text!r} is not a valid number. Try again.[/yellow]"
            )

def show_assets():
    assets = asset_service.list_assets()

    if not assets:
        console.print(
            Panel("No assets have been added.", title="Assets")
        )
        return

    table = Table(title="Available Assets")
    table.add_column("Ticker", style="cyan")
    table.add_column("Name")
    table.add_column("Current Price", justify="right")

    for asset in assets:
        price = pricing_service.get_price(asset.ticker)
        price_text = "Not set" if price is None else f"${price:.2f}"

        table.add_row(asset.ticker, asset.name, price_text)

    console.print(table)

def add_asset():
    ticker = ask_text("Ticker: ")
    name = ask_text("Asset name: ")

    asset_service.add_asset(ticker, name)
    print("Asset added successfully.")


def set_asset_price():
    ticker = ask_text("Ticker: ")
    price = ask_decimal("Current price: ")

    pricing_service.set_price(ticker, price)
    print("Price updated successfully.")


def create_portfolio():
    name = ask_text("Portfolio name: ")
    description = ask_text("Investment strategy: ")

    portfolio_service.create_portfolio(name, description)
    print("Portfolio created successfully.")


def show_portfolios():
    portfolios = portfolio_service.list_portfolios()

    if not portfolios:
        console.print(
            Panel("No portfolios have been created.", title="Portfolios")
        )
        return

    table = Table(title="Investment Portfolios")
    table.add_column("Name", style="cyan")
    table.add_column("Strategy")
    table.add_column("Selection", justify="center")

    for portfolio, selected in portfolios:
        marker = "[green]Selected[/green]" if selected else ""

        table.add_row(
            portfolio.name,
            portfolio.description,
            marker,
        )

    console.print(table)

def select_portfolio():
    name = ask_text("Portfolio name to select: ")

    portfolio_service.select_portfolio(name)
    print(f"Selected portfolio: {name}")


def delete_portfolio():
    name = ask_text("Portfolio name to delete: ")

    portfolio_service.delete_portfolio(name)
    print("Portfolio deleted successfully.")


def deposit_funds():
    amount = ask_decimal("Amount to deposit: ")

    cash_service.deposit(amount)
    print(f"Deposit successful. Cash balance: ${cash_service.get_balance():.2f}")


def buy_asset():
    ticker = ask_text("Ticker to buy: ")
    quantity = ask_decimal("Quantity: ")
    price = ask_decimal("Price per share: ")

    trading_service.buy_asset(ticker, quantity, price)
    print("Purchase completed successfully.")
    print(f"Cash balance: ${cash_service.get_balance():.2f}")


def sell_asset():
    ticker = ask_text("Ticker to sell: ")
    quantity = ask_decimal("Quantity: ")
    price = ask_decimal("Sale price per share: ")

    trading_service.sell_asset(ticker, quantity, price)
    print("Sale completed successfully.")
    print(f"Cash balance: ${cash_service.get_balance():.2f}")


def show_cash_balance():
    print(f"Cash balance: ${cash_service.get_balance():.2f}")


def show_selected_portfolio():
    report = portfolio_service.get_selected_portfolio_report()

    console.print(
        Panel(
            f"[bold]{report['name']}[/bold]\n"
            f"Strategy: {report['description']}",
            title="Portfolio Overview",
            border_style="blue",
        )
    )

    table = Table(title="Current Holdings")
    table.add_column("Ticker", style="cyan")
    table.add_column("Name")
    table.add_column("Quantity", justify="right")
    table.add_column("Average Cost", justify="right")
    table.add_column("Current Price", justify="right")
    table.add_column("Market Value", justify="right")
    table.add_column("Unrealized Gain/Loss", justify="right")

    for position in report["positions"]:
        current_price = position["current_price"]
        market_value = position["market_value"]
        unrealized = position["unrealized_gain"]

        table.add_row(
            position["ticker"],
            position["name"],
            str(position["quantity"]),
            f"${position['average_cost']:.2f}",
            "Not set" if current_price is None else f"${current_price:.2f}",
            "Unavailable" if market_value is None else f"${market_value:.2f}",
            "Unavailable" if unrealized is None else f"${unrealized:.2f}",
        )

    if not report["positions"]:
        console.print("[dim]No shares currently held.[/dim]")
    else:
        console.print(table)

    totals = Table(title="Portfolio Totals")
    totals.add_column("Metric")
    totals.add_column("Value", justify="right")

    market_value = report["market_value_total"]
    unrealized = report["unrealized_gain_total"]

    totals.add_row(
        "Market Value",
        "Unavailable" if market_value is None else f"${market_value:.2f}",
    )
    totals.add_row(
        "Unrealized Gain/Loss",
        "Unavailable" if unrealized is None else f"${unrealized:.2f}",
    )
    totals.add_row(
        "Realized Gain/Loss",
        f"${report['realized_gain_total']:.2f}",
    )

    console.print(totals)

    if report["missing_prices"]:
        console.print(
            "[yellow]Prices are missing for: "
            + ", ".join(report["missing_prices"])
            + ". Set those prices to calculate complete totals.[/yellow]"
        )

def handle_choice(choice):
    actions = {
        "1": add_asset,
        "2": show_assets,
        "3": set_asset_price,
        "4": create_portfolio,
        "5": show_portfolios,
        "6": select_portfolio,
        "7": delete_portfolio,
        "8": show_selected_portfolio,
        "9": deposit_funds,
        "10": buy_asset,
        "11": sell_asset,
        "12": show_cash_balance,
    }

    if choice == "0":
        return False

    action = actions.get(choice)

    if action is None:
        print("Invalid menu choice. Enter a number from 0 to 12.")
        return True

    try:
        action()
    except PortfolioTrackerError as error:
        logger.warning("Operation rejected: %s", error)
        print(f"Error: {error}")

    return True


def run():
    print("Welcome to Portfolio Tracker!")

    while True:
        print(MAIN_MENU)
        choice = input("Choose an option: ").strip()

        if not handle_choice(choice):
            print("Goodbye!")
            break