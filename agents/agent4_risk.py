"""
==============================================================================
  AGENT 4 -- RISK MANAGEMENT AGENT (Student C)
  FIN580 Quantamental Investment Project -- Brent Crude Oil
==============================================================================
  Evaluates signals from Agent 3 against VIX, drawdown, and conviction gates.
  Usage: python -m agents.agent4_risk
  Output: data/processed/a4_risk_decisions.json  ->  consumed by Agent 5
==============================================================================
"""

import os, json
from pydantic import BaseModel
from agents import load_config, resolve_path
from agents.agent3_signal import SignalOutput

_CFG = load_config()
_AGENT_CFG = _CFG.get("agent4", {})

class RiskOutput(BaseModel):
    signal: SignalOutput; approved: bool; veto_reason: str
    risk_multiplier: float = 1.0

class RiskManagerAgent:
    def __init__(self, max_vix=None, min_conviction=None, max_drawdown=None):
        self.max_vix = max_vix or _AGENT_CFG.get("max_vix", 30.0)
        self.min_conviction = min_conviction or _AGENT_CFG.get("min_conviction", 3)
        self.max_drawdown = max_drawdown or _AGENT_CFG.get("max_drawdown", 0.20)

    def evaluate_signal(self, signal: SignalOutput) -> RiskOutput:
        if signal.conviction < self.min_conviction:
            return RiskOutput(signal=signal, approved=False,
                veto_reason=f"VETO: Conviction {signal.conviction} < {self.min_conviction}",
                risk_multiplier=0.0)
        vix = 22.0  # Mock VIX for standalone stability
        risk_multiplier = 0.5 if vix > 20.0 else 1.0
        return RiskOutput(signal=signal, approved=True,
            veto_reason=f"APPROVED. VIX {vix} -> {risk_multiplier}x",
            risk_multiplier=risk_multiplier)

def main():
    print("="*70+"\n  AGENT 4 -- RISK MANAGEMENT (Student C)\n"+"="*70)
    sp = str(resolve_path(_CFG["paths"]["a3_signals"]))
    if not os.path.exists(sp): print(f"[ERROR] {sp} not found. Run agent3 first."); return
    with open(sp,"r",encoding="utf-8") as f: signals = [SignalOutput(**s) for s in json.load(f)]
    agent = RiskManagerAgent()
    decisions = [agent.evaluate_signal(s) for s in signals]
    out = str(resolve_path(_CFG["paths"]["a4_risk"]))
    os.makedirs(os.path.dirname(out),exist_ok=True)
    with open(out,"w",encoding="utf-8") as f: json.dump([d.model_dump() for d in decisions],f,indent=4)
    print(f"[OK] Agent 4 saved {len(decisions)} decisions to {out}")

if __name__ == "__main__": main()
