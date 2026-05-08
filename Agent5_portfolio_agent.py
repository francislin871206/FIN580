import os
import json
import yfinance as yf
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Optional

# ── Import RiskOutput from Agent 4 ──────────────────────────────────────────
from Agent4_risk_agent import RiskOutput

class PortfolioOutput(BaseModel):
    date: str
    asset: str
    direction: str
    size_usd: float
    entry_price_ref: float
    reasoning_trace: str
    core_allocation_pct: float
    tactical_allocation_pct: float
    cash_buffer_pct: float

class PortfolioManagerAgent:
    def __init__(self, initial_capital=1000000.0, core_allocation_pct=0.80, min_cash_buffer_pct=0.15):
        self.total_portfolio_value = initial_capital
        self.core_allocation_pct = core_allocation_pct
        self.min_cash_buffer_pct = min_cash_buffer_pct
        
        # Integration of IRL Portfolio Holdings (Roth-IRA)
        self.core_holdings = {
            "FXAIX": "Fidelity 500 Index",
            "FZROX": "Fidelity Total Market",
            "BRK-B": "Berkshire Hathaway",
            "GOOG": "Alphabet",
            "VRT": "Vertiv Holdings",
            "GBX": "Greenbrier Companies",
            "MAIN": "Main Street Capital",
            "WSM": "Williams-Sonoma",
            "BF-A": "Brown-Forman"
        }

    def size_trade(self, risk_decision: RiskOutput) -> Optional[PortfolioOutput]:
        if not risk_decision.approved:
            return None
        
        # Calculation Logic:
        # 1. Reserve 80% for Core Holdings
        # 2. Reserve 15% for Cash Buffer
        # 3. Use remaining 5% as Max Tactical Pool for Brent Crude
        
        core_value = self.total_portfolio_value * self.core_allocation_pct
        cash_buffer = self.total_portfolio_value * self.min_cash_buffer_pct
        tactical_pool = self.total_portfolio_value - core_value - cash_buffer
        
        # Sizing based on risk multiplier
        trade_size = tactical_pool * risk_decision.risk_multiplier
        
        return PortfolioOutput(
            date=risk_decision.signal.date or datetime.now().strftime("%Y-%m-%d"),
            asset=risk_decision.signal.asset,
            direction=risk_decision.signal.direction,
            size_usd=trade_size,
            entry_price_ref=80.0, # Placeholder for live price
            reasoning_trace=(
                f"Roth-IRA Logic: 80% Core (${core_value:,.0f}), "
                f"15% Cash Buffer (${cash_buffer:,.0f}). "
                f"Sizing tactical trade from pool (${tactical_pool:,.0f}) "
                f"using {risk_decision.risk_multiplier}x multiplier."
            ),
            core_allocation_pct=self.core_allocation_pct,
            tactical_allocation_pct=(1 - self.core_allocation_pct - self.min_cash_buffer_pct),
            cash_buffer_pct=self.min_cash_buffer_pct
        )

def main():
    print("=" * 70)
    print("  AGENT 5 -- PORTFOLIO CONSTRUCTION (Roth-IRA Strategy)")
    print("=" * 70)
    
    risk_path = "data/processed/a4_risk_decisions.json"
    if not os.path.exists(risk_path):
        print(f"[ERROR] Cannot find {risk_path}. Please run Agent 4 first.")
        return

    with open(risk_path, "r") as f:
        risks_raw = json.load(f)
    
    risks = [RiskOutput(**r) for r in risks_raw]
    agent = PortfolioManagerAgent()
    
    trades = []
    for r in risks:
        trade = agent.size_trade(r)
        if trade:
            trades.append(trade)
            print(f"[Agent 5] Planned Trade: {trade.direction} {trade.asset} - ${trade.size_usd:,.2f}")
    
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/a5_portfolio_trades.json"
    with open(output_path, "w") as f:
        json.dump([t.model_dump() for t in trades], f, indent=4)
        
    print(f"\n[OK] Agent 5 complete -- saved {len(trades)} trades to {output_path}")

if __name__ == "__main__":
    main()
