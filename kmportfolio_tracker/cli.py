import logging
from decimal import Decimal, InvalidOperation

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
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
        value = input(prompt).strip()
        if value:
            return value
        console.print(
            "[yellow]Input cannot be empty. Please try again.[/yellow]"
        )

def ask_decimal(prompt):
    while True:
        text = input(prompt).strip()
        try:
            value = Decimal(text)
            #decimal might take "nan" or "infinity" - must be careful so below
            if not value.is_finite():
                raise InvalidOperation
            return value
        except InvalidOperation:
            console.print(
                f"[yellow]'{escape(text)}' is not a valid number. Try again.[/yellow]"
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
        #asked AI as guide about how the SQL injection issue could apply to my file
        #flagged here as user input should be treated as plain text
        table.add_row(escape(asset.ticker), escape(asset.name), price_text)
    console.print(table)

def add_asset():
    ticker = ask_text("Ticker: ")
    name = ask_text("Asset name: ")
    asset_service.add_asset(ticker, name)
    console.print("[green]Asset added successfully.[/green]")

def set_asset_price():
    ticker = ask_text("Ticker: ")
    price = ask_decimal("Current price: ")
    pricing_service.set_price(ticker, price)
    console.print("[green]Price updated successfully.[/green]")

def create_portfolio():
    name = ask_text("Portfolio name: ")
    description = ask_text("Investment strategy: ")
    portfolio_service.create_portfolio(name, description)
    console.print("[green]Portfolio created successfully.[/green]")

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
            escape(portfolio.name),
            escape(portfolio.description),
            marker,
        )
    console.print(table)

def select_portfolio():
    name = ask_text("Portfolio name to select: ")
    portfolio_service.select_portfolio(name)
    console.print(f"[green]Selected portfolio: {escape(name)}[/green]")

def delete_portfolio():
    name = ask_text("Portfolio name to delete: ")
    portfolio_service.delete_portfolio(name)
    console.print("[green]Portfolio deleted successfully.[/green]")

def deposit_funds():
    amount = ask_decimal("Amount to deposit: ")
    cash_service.deposit(amount)
    console.print(
        f"[green]Deposit successful.[/green] "
        f"Cash balance: ${cash_service.get_balance():.2f}"
    )

def buy_asset():
    ticker = ask_text("Ticker to buy: ")
    quantity = ask_decimal("Quantity: ")
    price = ask_decimal("Price per share: ")
    trading_service.buy_asset(ticker, quantity, price)
    console.print("[green]Purchase completed successfully.[/green]")
    console.print(f"Cash balance: ${cash_service.get_balance():.2f}")

def sell_asset():
    ticker = ask_text("Ticker to sell: ")
    quantity = ask_decimal("Quantity: ")
    price = ask_decimal("Sale price per share: ")
    trading_service.sell_asset(ticker, quantity, price)
    console.print("[green]Sale completed successfully.[/green]")
    console.print(f"Cash balance: ${cash_service.get_balance():.2f}")

def show_cash_balance():
    console.print(f"Cash balance: ${cash_service.get_balance():.2f}")

def show_selected_portfolio():
    report = portfolio_service.get_selected_portfolio_report()

    console.print(
        Panel(
            f"[bold]{escape(report['name'])}[/bold]\n"
            f"Strategy: {escape(report['description'])}",
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
            escape(position["ticker"]),
            escape(position["name"]),
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
        missing = escape(", ".join(report["missing_prices"]))
        console.print(
            f"[yellow]Prices are missing for: {missing}. "
            "Set those prices to calculate complete totals.[/yellow]"
        )

def handle_choice(choice):
    if choice == "0":
        return False

    try:
        if choice == "1":
            add_asset()
        elif choice == "2":
            show_assets()
        elif choice == "3":
            set_asset_price()
        elif choice == "4":
            create_portfolio()
        elif choice == "5":
            show_portfolios()
        elif choice == "6":
            select_portfolio()
        elif choice == "7":
            delete_portfolio()
        elif choice == "8":
            show_selected_portfolio()
        elif choice == "9":
            deposit_funds()
        elif choice == "10":
            buy_asset()
        elif choice == "11":
            sell_asset()
        elif choice == "12":
            show_cash_balance()
        else:
            console.print(
                "[yellow]Invalid menu choice. Enter a number from 0 to 12.[/yellow]"
            )
    except PortfolioTrackerError as error:
        logger.warning("Operation rejected: %s", error)
        console.print(f"[red]Error: {escape(str(error))}[/red]")
    return True

def run():
    console.print("[bold]Welcome to Portfolio Tracker![/bold]")
    while True:
        console.print(MAIN_MENU)
        choice = input("Choose an option: ").strip()
        if not handle_choice(choice):
            console.print("Goodbye!")
            break