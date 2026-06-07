"""
CodeAlpha Internship — Task 2: Stock Portfolio Tracker
Author  : [Your Name]
Purpose : Track a personal stock portfolio — add holdings, view live
          valuation, gain/loss analysis, and export to CSV.
"""

import csv
import os
from datetime import datetime
from typing import Optional

# ─────────────────────────────────────────────
#  Hardcoded market prices  (USD)
# ─────────────────────────────────────────────
MARKET_PRICES: dict[str, float] = {
    "AAPL"  : 189.50,
    "TSLA"  : 248.75,
    "GOOGL" : 175.30,
    "AMZN"  : 192.40,
    "MSFT"  : 415.20,
    "META"  : 527.80,
    "NVDA"  : 875.60,
    "NFLX"  : 648.90,
    "AMD"   : 162.30,
    "INTC"  : 30.45,
}

EXPORT_FILE = "portfolio_report.csv"


# ─────────────────────────────────────────────
#  Helper utilities
# ─────────────────────────────────────────────
def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner(title: str) -> None:
    clear()
    width = 52
    print("=" * width)
    print(f"{'📈  STOCK PORTFOLIO TRACKER':^{width}}")
    print(f"{title:^{width}}")
    print("=" * width)


def fmt_usd(value: float) -> str:
    return f"${value:,.2f}"


def fmt_pct(value: float) -> str:
    arrow = "▲" if value >= 0 else "▼"
    return f"{arrow} {abs(value):.2f}%"


# ─────────────────────────────────────────────
#  Portfolio class
# ─────────────────────────────────────────────
class Portfolio:
    """Holds all user stock positions and exposes analytics."""

    def __init__(self) -> None:
        # { ticker: {"qty": int, "buy_price": float} }
        self._holdings: dict[str, dict] = {}

    # ── Mutations ─────────────────────────────
    def add_position(self, ticker: str, qty: int,
                     buy_price: Optional[float] = None) -> str:
        ticker = ticker.upper()
        if ticker not in MARKET_PRICES:
            return f"  ❌  '{ticker}' not found. Available: {', '.join(MARKET_PRICES)}"

        price = buy_price if buy_price is not None else MARKET_PRICES[ticker]

        if ticker in self._holdings:
            # Average down / up  (weighted average cost basis)
            old     = self._holdings[ticker]
            total_q = old["qty"] + qty
            avg     = (old["qty"] * old["buy_price"] + qty * price) / total_q
            self._holdings[ticker] = {"qty": total_q, "buy_price": round(avg, 4)}
            return f"  ✅  Updated {ticker}: {total_q} shares @ avg {fmt_usd(avg)}"
        else:
            self._holdings[ticker] = {"qty": qty, "buy_price": price}
            return f"  ✅  Added {ticker}: {qty} shares @ {fmt_usd(price)}"

    def remove_position(self, ticker: str) -> str:
        ticker = ticker.upper()
        if ticker not in self._holdings:
            return f"  ⚠  {ticker} not in portfolio."
        del self._holdings[ticker]
        return f"  🗑  Removed {ticker} from portfolio."

    # ── Analytics ─────────────────────────────
    def summary(self) -> list[dict]:
        rows = []
        for ticker, data in self._holdings.items():
            mkt      = MARKET_PRICES[ticker]
            qty      = data["qty"]
            buy_p    = data["buy_price"]
            cost     = qty * buy_p
            value    = qty * mkt
            gain     = value - cost
            gain_pct = (gain / cost * 100) if cost else 0.0
            rows.append({
                "ticker"   : ticker,
                "qty"      : qty,
                "buy_price": buy_p,
                "mkt_price": mkt,
                "cost"     : cost,
                "value"    : value,
                "gain"     : gain,
                "gain_pct" : gain_pct,
            })
        return sorted(rows, key=lambda r: r["value"], reverse=True)

    @property
    def total_cost(self) -> float:
        return sum(r["cost"] for r in self.summary())

    @property
    def total_value(self) -> float:
        return sum(r["value"] for r in self.summary())

    @property
    def total_gain(self) -> float:
        return self.total_value - self.total_cost

    @property
    def total_gain_pct(self) -> float:
        return (self.total_gain / self.total_cost * 100) if self.total_cost else 0.0

    def is_empty(self) -> bool:
        return not self._holdings

    # ── Export ────────────────────────────────
    def export_csv(self) -> str:
        if self.is_empty():
            return "  ⚠  Portfolio is empty — nothing to export."

        rows = self.summary()
        fields = ["Ticker", "Qty", "Buy Price", "Market Price",
                  "Cost Basis", "Current Value", "Gain/Loss", "Gain %",
                  "Exported At"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(EXPORT_FILE, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow({
                    "Ticker"       : r["ticker"],
                    "Qty"          : r["qty"],
                    "Buy Price"    : f"{r['buy_price']:.2f}",
                    "Market Price" : f"{r['mkt_price']:.2f}",
                    "Cost Basis"   : f"{r['cost']:.2f}",
                    "Current Value": f"{r['value']:.2f}",
                    "Gain/Loss"    : f"{r['gain']:.2f}",
                    "Gain %"       : f"{r['gain_pct']:.2f}",
                    "Exported At"  : timestamp,
                })
            # Totals row
            w.writerow({
                "Ticker"       : "TOTAL",
                "Qty"          : "",
                "Buy Price"    : "",
                "Market Price" : "",
                "Cost Basis"   : f"{self.total_cost:.2f}",
                "Current Value": f"{self.total_value:.2f}",
                "Gain/Loss"    : f"{self.total_gain:.2f}",
                "Gain %"       : f"{self.total_gain_pct:.2f}",
                "Exported At"  : timestamp,
            })
        return f"  ✅  Report saved to '{EXPORT_FILE}'"


# ─────────────────────────────────────────────
#  Display helpers
# ─────────────────────────────────────────────
def show_prices() -> None:
    banner("── Market Prices ──")
    print(f"\n  {'Ticker':<8} {'Price':>10}")
    print("  " + "-" * 20)
    for ticker, price in sorted(MARKET_PRICES.items()):
        print(f"  {ticker:<8} {fmt_usd(price):>10}")
    print()


def show_portfolio(portfolio: Portfolio) -> None:
    banner("── Your Portfolio ──")
    if portfolio.is_empty():
        print("\n  Portfolio is empty. Add some stocks first.\n")
        return

    rows = portfolio.summary()
    hdr  = f"  {'Ticker':<7} {'Qty':>5} {'Buy$':>9} {'Mkt$':>9} {'Value':>12} {'G/L':>12} {'G/L%':>9}"
    print(f"\n{hdr}")
    print("  " + "-" * 68)
    for r in rows:
        color = "+" if r["gain"] >= 0 else "-"
        print(
            f"  {r['ticker']:<7}"
            f" {r['qty']:>5}"
            f" {fmt_usd(r['buy_price']):>9}"
            f" {fmt_usd(r['mkt_price']):>9}"
            f" {fmt_usd(r['value']):>12}"
            f" {color}{fmt_usd(abs(r['gain'])):>11}"
            f" {fmt_pct(r['gain_pct']):>9}"
        )
    print("  " + "-" * 68)
    g_sign = "+" if portfolio.total_gain >= 0 else "-"
    print(
        f"  {'TOTAL':<7}"
        f" {'':>5}"
        f" {'':>9}"
        f" {'':>9}"
        f" {fmt_usd(portfolio.total_value):>12}"
        f" {g_sign}{fmt_usd(abs(portfolio.total_gain)):>11}"
        f" {fmt_pct(portfolio.total_gain_pct):>9}"
    )
    print()


# ─────────────────────────────────────────────
#  Main menu
# ─────────────────────────────────────────────
def main() -> None:
    portfolio = Portfolio()

    menu = {
        "1": "View Portfolio",
        "2": "Add / Update Stock",
        "3": "Remove Stock",
        "4": "View Market Prices",
        "5": "Export to CSV",
        "0": "Exit",
    }

    while True:
        banner("── Main Menu ──")
        for key, label in menu.items():
            print(f"  [{key}]  {label}")
        print()
        choice = input("  Select option: ").strip()

        if choice == "1":
            show_portfolio(portfolio)
            input("  Press Enter to continue…")

        elif choice == "2":
            banner("── Add Stock ──")
            show_prices()
            ticker = input("  Enter ticker symbol: ").strip().upper()
            try:
                qty = int(input("  Quantity of shares : "))
                if qty <= 0:
                    raise ValueError
            except ValueError:
                input("  ⚠  Invalid quantity. Press Enter…")
                continue

            raw_price = input("  Buy price (leave blank to use market price): ").strip()
            buy_price: Optional[float] = None
            if raw_price:
                try:
                    buy_price = float(raw_price)
                    if buy_price <= 0:
                        raise ValueError
                except ValueError:
                    input("  ⚠  Invalid price. Press Enter…")
                    continue

            msg = portfolio.add_position(ticker, qty, buy_price)
            input(f"{msg}\n  Press Enter to continue…")

        elif choice == "3":
            banner("── Remove Stock ──")
            show_portfolio(portfolio)
            if not portfolio.is_empty():
                ticker = input("  Enter ticker to remove: ").strip()
                msg = portfolio.remove_position(ticker)
                input(f"{msg}\n  Press Enter to continue…")

        elif choice == "4":
            show_prices()
            input("  Press Enter to continue…")

        elif choice == "5":
            msg = portfolio.export_csv()
            input(f"\n{msg}\n  Press Enter to continue…")

        elif choice == "0":
            clear()
            print("\n  👋  Goodbye! Happy investing.\n")
            break

        else:
            input("  ⚠  Invalid option. Press Enter…")


if __name__ == "__main__":
    main()
