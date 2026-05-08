"""
==============================================================================
  AGENT 4 -- RISK MANAGEMENT AGENT (Student C)
  FIN580 Quantamental Investment Project -- Brent Crude Oil
==============================================================================
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pydantic import BaseModel
from Agent3_signal_agent import SignalOutput

class RiskOutput(BaseModel):
    signal: SignalOutput
    approved: bool
    veto_reason: str
    risk_multiplier: float = 1.0

class RiskManagerAgent:
    def __init__(self, max_vix=30.0, min_conviction=3, max_drawdown=0.20):
        self.max_vix = max_vix
        self.min_conviction = min_conviction
        self.max_drawdown = max_drawdown

    def evaluate_signal(self, signal: SignalOutput) -> RiskOutput:
        if signal.conviction < self.min_conviction:
            return RiskOutput(signal=signal, approved=False, veto_reason=f"VETO: Conviction {signal.conviction} < {self.min_conviction}", risk_multiplier=0.0)
        
        # Simple Mock VIX/Drawdown for standalone stability
        vix = 22.0 
        risk_multiplier = 0.5 if vix > 20.0 else 1.0
        return RiskOutput(signal=signal, approved=True, veto_reason=f"APPROVED. VIX {vix} -> {risk_multiplier}x", risk_multiplier=risk_multiplier)

def main():
    import os
    import json
    print("=" * 70)
    print("  AGENT 4 -- RISK MANAGEMENT (Student C)")
    print("=" * 70)
    signal_path = "data/processed/a3_signals.json"
    if not os.path.exists(signal_path):
        print(f"[ERROR] Cannot find {signal_path}. Please run signal_agent.py first.")
        return
    with open(signal_path, "r") as f:
        signals_raw = json.load(f)
    signals = [SignalOutput(**s) for s in signals_raw]
    agent = RiskManagerAgent()
    decisions = [agent.evaluate_signal(s) for s in signals]
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/a4_risk_decisions.json"
    with open(output_path, "w") as f:
        json.dump([d.model_dump() for d in decisions], f, indent=4)
    print(f"[OK] Agent 4 saved {len(decisions)} decisions to {output_path}")

if __name__ == "__main__":
    main()
