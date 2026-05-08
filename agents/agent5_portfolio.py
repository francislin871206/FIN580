"""
==============================================================================
  AGENT 5 -- PORTFOLIO CONSTRUCTION AGENT (Student C)
  FIN580 Quantamental Investment Project -- Brent Crude Oil
==============================================================================
  Sizes approved trades from Agent 4 under capital and position constraints.
  Integrates IRL Roth-IRA core holdings with a defensive cash-buffer rule.

  Architecture:
    - 80% of capital is allocated to long-term core holdings (buy-and-hold)
    - 20% is the tactical trading pool for Brent Crude signals
    - A strict minimum cash buffer (15%) prevents over-deployment

  Usage: python -m agents.agent5_portfolio
  Output: data/processed/a5_portfolio_trades.json
==============================================================================
"""

import os, json
from pydantic import BaseModel
from typing import Optional
from agents import load_config, resolve_path
from agents.agent4_risk import RiskOutput

_CFG = load_config()
_AGENT_CFG = _CFG.get("agent5", {})

# ── Core Holdings (IRL Roth-IRA static portfolio) ────────────────────────────
CORE_HOLDINGS = {
    "FXAIX": "Fidelity 500 Index",
    "FZROX": "Fidelity Total Market",
    "BRK-B": "Berkshire Hathaway",
    "GOOG":  "Alphabet",
    "VRT":   "Vertiv Holdings",
    "GBX":   "Greenbrier Companies",
    "MAIN":  "Main Street Capital",
    "WSM":   "Williams-Sonoma",
    "BF-A":  "Brown-Forman",
}

class PortfolioOutput(BaseModel):
    date: str; asset: str; direction: str; size_usd: float
    entry_price_ref: float; reasoning_trace: str

class PortfolioManagerAgent:
    """
    Portfolio construction with Roth-IRA constraints:
      - 80% locked in core equity holdings (FXAIX, FZROX, BRK-B, etc.)
      - 20% available for tactical Brent Crude trades
      - Minimum 15% cash buffer enforced at all times
    """
    def __init__(self, initial_capital=None, max_position_pct=None,
                 core_allocation_pct=None, min_cash_buffer_pct=None):
        self.total_portfolio_value = initial_capital or _AGENT_CFG.get("initial_capital", 1000000.0)
        self.max_position_pct = max_position_pct or _AGENT_CFG.get("max_position_pct", 0.10)
        self.core_allocation_pct = core_allocation_pct or _AGENT_CFG.get("core_allocation_pct", 0.80)
        self.min_cash_buffer_pct = min_cash_buffer_pct or _AGENT_CFG.get("min_cash_buffer_pct", 0.15)

        # 80% locked in core holdings, 20% is tactical pool
        self.allocated_in_core = self.total_portfolio_value * self.core_allocation_pct
        self.available_cash = self.total_portfolio_value - self.allocated_in_core
        self.core_holdings = CORE_HOLDINGS
        self.portfolio_log = []

    def get_entry_price(self, date_str: str) -> float:
        """Fetch real entry price for BZ=F. Falls back to $80 in mock mode."""
        if _CFG.get("pipeline", {}).get("mock_mode", True):
            return 80.0
        try:
            import yfinance as yf
            from datetime import datetime, timedelta
            import pandas as pd
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            data = yf.download(
                "BZ=F",
                start=(target_date - timedelta(days=7)).strftime("%Y-%m-%d"),
                end=(target_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                progress=False
            )
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    return float(data['Close']['BZ=F'].iloc[-1])
                return float(data['Close'].iloc[-1])
        except Exception:
            pass
        return 80.0

    def size_trade(self, risk_decision: RiskOutput) -> Optional[PortfolioOutput]:
        """
        Size a trade with Roth-IRA defensive constraints:
          1. Base allocation = (conviction / 5) * max_position_pct
          2. Apply Agent 4's risk multiplier
          3. Enforce minimum cash buffer (never dip below 15% reserve)
        """
        if not risk_decision.approved:
            return None

        signal = risk_decision.signal

        # 1. Base allocation based on conviction (5/5 = 100% of max allowed position)
        base_allocation_pct = (signal.conviction / 5.0) * self.max_position_pct

        # 2. Apply dynamic risk multiplier from Agent 4
        final_allocation_pct = base_allocation_pct * risk_decision.risk_multiplier
        intended_trade_size = self.total_portfolio_value * final_allocation_pct

        # 3. Roth IRA Cash Buffer Constraint
        min_required_cash = self.total_portfolio_value * self.min_cash_buffer_pct
        max_deployable_cash = self.available_cash - min_required_cash

        if max_deployable_cash <= 0:
            print(f"   [PORTFOLIO VETO] Trade rejected. Available cash "
                  f"(${self.available_cash:,.2f}) hit minimum buffer reserve.")
            return None

        # Cap trade to deployable cash
        actual_trade_size = min(intended_trade_size, max_deployable_cash)

        # 4. Deduct from available cash
        self.available_cash -= actual_trade_size

        entry_price = self.get_entry_price(signal.date or "2024-05-01")

        # Reasoning trace with full math
        cash_note = ""
        if actual_trade_size < intended_trade_size:
            cash_note = (f" (NOTE: Capped by Cash Buffer - Reduced from "
                        f"${intended_trade_size:,.0f} to ${actual_trade_size:,.0f})")

        trace = (f"A4 Risk Multiplier: {risk_decision.risk_multiplier}x. "
                f"A5 Sizing: Allocated {final_allocation_pct*100:.1f}% "
                f"= ${actual_trade_size:,.0f}{cash_note}. "
                f"Cash remaining: ${self.available_cash:,.0f} "
                f"(Core holdings: ${self.allocated_in_core:,.0f}).")

        trade = PortfolioOutput(
            date=signal.date or "2024-05-01",
            asset=signal.asset, direction=signal.direction,
            size_usd=actual_trade_size, entry_price_ref=entry_price,
            reasoning_trace=trace
        )
        self.portfolio_log.append(trade)
        return trade

def main():
    print("="*70+"\n  AGENT 5 -- PORTFOLIO CONSTRUCTION (Student C)\n"+"="*70)
    rp = str(resolve_path(_CFG["paths"]["a4_risk"]))
    if not os.path.exists(rp): print(f"[ERROR] {rp} not found. Run agent4 first."); return
    with open(rp,"r",encoding="utf-8") as f: risks = [RiskOutput(**r) for r in json.load(f)]

    agent = PortfolioManagerAgent()

    # Display portfolio structure
    print(f"\n  Total Portfolio:       ${agent.total_portfolio_value:>14,.2f}")
    print(f"  Core Holdings (80%):  ${agent.allocated_in_core:>14,.2f}")
    print(f"  Tactical Pool (20%):  ${agent.available_cash:>14,.2f}")
    print(f"  Min Cash Buffer:      {agent.min_cash_buffer_pct*100:.0f}%")
    print(f"\n  Core Holdings:")
    for ticker, name in agent.core_holdings.items():
        print(f"    {ticker:<8s} {name}")
    print()

    trades = []
    for r in risks:
        t = agent.size_trade(r)
        if t:
            trades.append(t)
            print(f"  [TRADE] {t.direction} {t.asset} | ${t.size_usd:,.0f} | {t.reasoning_trace}")
        elif r.approved:
            print(f"  [PORTFOLIO VETO] Cash buffer prevents trade for {r.signal.event_id}")

    out = str(resolve_path(_CFG["paths"]["a5_trades"]))
    os.makedirs(os.path.dirname(out),exist_ok=True)
    with open(out,"w",encoding="utf-8") as f: json.dump([t.model_dump() for t in trades],f,indent=4)
    print(f"\n[OK] Agent 5 saved {len(trades)} trades to {out}")
    print(f"     Cash remaining: ${agent.available_cash:,.2f}")
    print("\n"+"="*70+"\n  ALL AGENTS FINISHED. CHECK data/processed/ FOR RESULTS.\n"+"="*70)

if __name__ == "__main__": main()
