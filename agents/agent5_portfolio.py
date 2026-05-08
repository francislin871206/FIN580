"""
==============================================================================
  AGENT 5 -- PORTFOLIO CONSTRUCTION AGENT (Student C)
  FIN580 Quantamental Investment Project -- Brent Crude Oil
==============================================================================
  Sizes approved trades from Agent 4 under capital and position constraints.
  Usage: python -m agents.agent5_portfolio
  Output: data/processed/a5_portfolio_trades.json
==============================================================================
"""

import os, json
from pydantic import BaseModel
from agents import load_config, resolve_path
from agents.agent4_risk import RiskOutput

_CFG = load_config()
_AGENT_CFG = _CFG.get("agent5", {})

class PortfolioOutput(BaseModel):
    date: str; asset: str; direction: str; size_usd: float
    entry_price_ref: float; reasoning_trace: str

class PortfolioManagerAgent:
    def __init__(self, initial_capital=None, max_position_pct=None):
        self.capital = initial_capital or _AGENT_CFG.get("initial_capital", 1000000.0)
        self.max_pos = max_position_pct or _AGENT_CFG.get("max_position_pct", 0.10)

    def size_trade(self, risk_decision: RiskOutput) -> PortfolioOutput:
        if not risk_decision.approved: return None
        size = self.capital * self.max_pos * risk_decision.risk_multiplier
        return PortfolioOutput(
            date=risk_decision.signal.date or "2024-05-01",
            asset=risk_decision.signal.asset, direction=risk_decision.signal.direction,
            size_usd=size, entry_price_ref=80.0,
            reasoning_trace=f"Sized at ${size:,.2f} with risk multiplier {risk_decision.risk_multiplier}")

def main():
    print("="*70+"\n  AGENT 5 -- PORTFOLIO CONSTRUCTION (Student C)\n"+"="*70)
    rp = str(resolve_path(_CFG["paths"]["a4_risk"]))
    if not os.path.exists(rp): print(f"[ERROR] {rp} not found. Run agent4 first."); return
    with open(rp,"r",encoding="utf-8") as f: risks = [RiskOutput(**r) for r in json.load(f)]
    agent = PortfolioManagerAgent()
    trades = [agent.size_trade(r) for r in risks if r.approved]
    out = str(resolve_path(_CFG["paths"]["a5_trades"]))
    os.makedirs(os.path.dirname(out),exist_ok=True)
    with open(out,"w",encoding="utf-8") as f: json.dump([t.model_dump() for t in trades if t],f,indent=4)
    print(f"[OK] Agent 5 saved {len(trades)} trades to {out}")
    print("\n"+"="*70+"\n  ALL AGENTS FINISHED. CHECK data/processed/ FOR RESULTS.\n"+"="*70)

if __name__ == "__main__": main()
