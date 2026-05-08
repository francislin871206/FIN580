"""
==============================================================================
  BACKTESTING ENGINE
  FIN580 Multi-Agent Brent Crude Trading System
==============================================================================
  Generates mock signals over a date range and simulates A4 (Risk) -> A5
  (Portfolio) execution with random entry/exit prices.

  Computes: Total PnL, Sharpe Ratio, Win Rate, Max Drawdown

  Usage:
    python scripts/run_backtest.py
    python scripts/run_backtest.py --signals 50
    python scripts/run_backtest.py --capital 2000000
==============================================================================
"""

import sys, os, json, csv, random, math, argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import load_config, resolve_path
from agents.agent3_signal import SignalOutput
from agents.agent4_risk import RiskManagerAgent
from agents.agent5_portfolio import PortfolioManagerAgent


def generate_backtest_signals(num_signals=20, start_date=None):
    """Generate a series of mock A3 signals for backtesting."""
    if start_date is None:
        start_date = datetime(2022, 1, 1)

    reasons = [
        "OPEC+ production adjustment.", "Demand volatility in emerging markets.",
        "Inventory levels lower than expected.", "Geopolitical tensions in Middle East.",
        "Global recession fears impacting demand.", "SPR release rumors.",
        "Refinery maintenance season.", "Unexpected seasonal weather patterns.",
        "USD strength impacting commodity pricing.", "Technical breakout on daily chart."
    ]

    signals = []
    current_date = start_date
    for _ in range(num_signals):
        current_date += timedelta(days=random.randint(20, 40))
        direction = random.choice(["LONG", "SHORT", "FLAT"])
        conviction = random.randint(1, 5)
        if direction == "FLAT":
            conviction = random.randint(1, 2)

        signals.append(SignalOutput(
            event_id=f"BT_{current_date.strftime('%Y%m%d')}",
            asset="Brent Crude Oil", ticker="BZ=F",
            signal=direction, signal_strength=0.70,
            conviction_score=conviction, entry_timing="Next Market Open",
            holding_period_days=7,
            supporting_reason=random.choice(reasons),
            historical_avg_return=0.04, historical_win_rate=0.60,
            expected_alpha=0.025,
            historical_analog_event="Mock Analog",
            historical_analog_return=0.03, historical_similarity_score=0.75,
            date=current_date.strftime("%Y-%m-%d"),
            direction=direction, conviction=conviction,
        ))
    return signals


def run_backtest(num_signals=20, initial_capital=None):
    """Run a full backtest simulation."""
    cfg = load_config()
    if initial_capital is None:
        initial_capital = cfg.get("agent5", {}).get("initial_capital", 1000000.0)

    print("=" * 70)
    print("  BACKTESTING ENGINE")
    print(f"  Signals: {num_signals} | Capital: ${initial_capital:,.2f}")
    print("=" * 70)

    # 1. Generate signals
    signals = generate_backtest_signals(num_signals)
    print(f"\n[1] Generated {len(signals)} mock signals")

    # 2. Risk filter
    agent4 = RiskManagerAgent()
    agent5 = PortfolioManagerAgent(initial_capital=initial_capital)

    trades = []
    pnl_series = []
    cumulative_pnl = 0.0

    for sig in signals:
        risk = agent4.evaluate_signal(sig)
        if not risk.approved:
            continue

        trade = agent5.size_trade(risk)
        if trade is None:
            continue

        # Simulate entry/exit
        entry_price = 75.0 + random.uniform(-10, 15)  # ~$65-$90 range
        price_change_pct = random.gauss(0.001, 0.03)  # mean +0.1%, std 3%
        exit_price = entry_price * (1 + price_change_pct)

        if trade.direction == "LONG":
            pnl = trade.size_usd * price_change_pct
        else:  # SHORT
            pnl = trade.size_usd * (-price_change_pct)

        cumulative_pnl += pnl
        pnl_series.append(pnl)

        trades.append({
            "date": trade.date,
            "direction": trade.direction,
            "size_usd": trade.size_usd,
            "entry_price": round(entry_price, 2),
            "exit_price": round(exit_price, 2),
            "pnl": round(pnl, 2),
            "cumulative_pnl": round(cumulative_pnl, 2),
        })

    # 3. Compute metrics
    total_trades = len(trades)
    total_pnl = sum(t["pnl"] for t in trades)
    wins = sum(1 for t in trades if t["pnl"] > 0)
    win_rate = wins / total_trades if total_trades > 0 else 0

    # Sharpe ratio (annualized, assuming ~252 trading days)
    if len(pnl_series) > 1:
        mean_pnl = sum(pnl_series) / len(pnl_series)
        std_pnl = math.sqrt(sum((p - mean_pnl) ** 2 for p in pnl_series) / (len(pnl_series) - 1))
        sharpe = (mean_pnl / std_pnl) * math.sqrt(252) if std_pnl > 0 else 0
    else:
        sharpe = 0

    # Max drawdown
    cumulative = 0; peak = 0; max_dd = 0
    for t in trades:
        cumulative += t["pnl"]
        if cumulative > peak: peak = cumulative
        dd = (peak - cumulative) / initial_capital if peak > 0 else 0
        if dd > max_dd: max_dd = dd

    results = {
        "config": {"num_signals": num_signals, "initial_capital": initial_capital},
        "summary": {
            "total_signals": num_signals,
            "signals_approved": total_trades,
            "signals_vetoed": num_signals - total_trades,
            "total_pnl": round(total_pnl, 2),
            "win_rate": round(win_rate, 4),
            "sharpe_ratio": round(sharpe, 4),
            "max_drawdown_pct": round(max_dd * 100, 4),
        },
        "trades": trades,
    }

    # 4. Print summary
    print(f"\n{'=' * 50}")
    print(f"  BACKTEST RESULTS")
    print(f"{'=' * 50}")
    print(f"  Total Signals Generated : {num_signals}")
    print(f"  Signals Approved (Traded): {total_trades}")
    print(f"  Signals Vetoed           : {num_signals - total_trades}")
    print(f"  Total PnL               : ${total_pnl:,.2f}")
    print(f"  Win Rate                 : {win_rate:.1%}")
    print(f"  Sharpe Ratio (annualized): {sharpe:.4f}")
    print(f"  Max Drawdown             : {max_dd:.2%}")
    print(f"{'=' * 50}")

    # 5. Save results
    os.makedirs(str(resolve_path("logs")), exist_ok=True)
    out_path = str(resolve_path("logs/backtest_results.json"))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[OK] Results saved to {out_path}")

    # Also save trade log CSV
    csv_path = str(resolve_path("logs/backtest_trades.csv"))
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "direction", "size_usd", "entry_price", "exit_price", "pnl", "cumulative_pnl"])
        w.writeheader()
        w.writerows(trades)
    print(f"[OK] Trade log saved to {csv_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FIN580 Backtesting Engine")
    parser.add_argument("--signals", type=int, default=30, help="Number of mock signals to generate")
    parser.add_argument("--capital", type=float, default=None, help="Initial capital (default from config)")
    args = parser.parse_args()
    run_backtest(num_signals=args.signals, initial_capital=args.capital)
