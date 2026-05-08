"""
==============================================================================
  AGENT 2 -- MACRO INTERPRETATION (3-Round Debate Committee) (Student A)
  FIN580 Quantamental Investment Project -- Brent Crude Oil
==============================================================================
  Reads events from Agent 1 and runs a multi-agent LLM debate to generate
  macro-economic theses via Primary Analyst vs Devil's Advocate rounds.
  Usage: python -m agents.agent2_macro
  Output: data/processed/a2_macro.json, data/processed/a1_a2_merged.json
==============================================================================
"""

import os, json, time
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Optional
from agents import load_config, load_prompt, resolve_path
from agents.agent1_event import EventOutput

_CFG = load_config()
_PIPELINE  = _CFG.get("pipeline", {})
_AGENT_CFG = _CFG.get("agent2", {})
_GEMINI    = _CFG.get("gemini", {})

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = _GEMINI.get("model", "gemini-2.5-flash")
MOCK_MODE      = _PIPELINE.get("mock_mode", True)
RATE_LIMIT_SEC = _PIPELINE.get("rate_limit_sec", 2)
MAX_ROUNDS     = _AGENT_CFG.get("max_debate_rounds", 3)

class MacroOutput(BaseModel):
    """Schema for Agent 2 output -- consumed by Agent 3 (Student B)"""
    event_id: str; macro_thesis: str; causal_chain: List[str]
    affected_factors: List[str]; market_regime: str; expected_impact: str
    conviction_score: int; time_horizon: str
    reasoning_trace: Optional[str] = None
    processing_timestamp: Optional[str] = None

class AdvancedMacroAgent:
    """Agent 2: Macro Interpretation via 3-Round Adversarial Debate."""
    def __init__(self):
        self.mock_mode = MOCK_MODE; self.max_rounds = MAX_ROUNDS
        print("[Agent 2] Initializing Macro Debate Committee...")
        if not self.mock_mode:
            from google import genai; from google.genai import types
            self.genai, self.types = genai, types
            self.client = genai.Client(api_key=GEMINI_API_KEY)

    def _get_rag_context(self, event):
        return """
        [MACROECONOMIC CONTEXT]
        - Current VIX: 22.5 (Elevated fear, risk-off sentiment)
        - US Fed Funds Rate: 5.25%-5.50% (High, suppressing growth)
        - Global Oil Inventories: 4% below 5-year average (Tight supply)
        - China Manufacturing PMI: 49.2 (Contraction territory)
        - US Dollar Index (DXY): 104.5 (Strong dollar, bearish commodities)
        - Geopolitical Risk Index: High (Middle East tensions)
        """

    def process_event(self, event: EventOutput) -> MacroOutput:
        pt = datetime.now(timezone.utc).isoformat()
        rag = self._get_rag_context(event)
        if self.mock_mode:
            mock_debate = (
                f"=== DEBATE TRANSCRIPT FOR EVENT: {event.headline} ===\n\n"
                "[ROUND 1 -- Primary Analyst]:\nSupply shock tightens physical markets. "
                "Inventories 4% below average -> strong bullish momentum.\n\n"
                "[ROUND 1 -- Devil's Advocate]:\nDemand side ignored. China PMI 49.2 "
                "(contraction), Fed at 5.25%-5.50%, DXY 104.5 creates headwinds.\n\n"
                "[ROUND 2 -- Primary Analyst (Rebuttal)]:\nGeopolitical Risk Index High. "
                "Historically tight supply + geopolitical risk -> risk-premiums override demand.\n\n"
                "[ROUND 2 -- Devil's Advocate]:\nRisk premiums transient. Structural demand "
                "weakness from China and high rates will dominate.\n\n"
                "[ROUND 3 -- Primary Analyst]:\nConcede. Bullish impact short-term and capped.\n\n"
                "[ROUND 3 -- Devil's Advocate]:\n[CONSENSUS REACHED]\n\n"
                "=== END DEBATE ===\n\n"
                "[Head of Strategy]: Consensus after 3 rounds. Short-term bullish spike "
                "capped by structural demand weakness. Conviction: 4."
            )
            return MacroOutput(
                event_id=event.event_id,
                macro_thesis="Short-term bullish spike driven by supply tightness, but upside capped by structural demand weakness and high interest rates.",
                causal_chain=["Event tightens supply","Risk premium spikes short-term","High rates and weak PMI suppress demand","Net: Capped short-term bullishness"],
                affected_factors=["Inventories","Geopolitical Risk","Interest Rates","PMI"],
                market_regime="Stagflationary",expected_impact="Bullish Brent",
                conviction_score=4,time_horizon="Short-term",
                reasoning_trace=mock_debate,processing_timestamp=pt)

        # Live Gemini 3-Round Debate
        try:
            transcript = f"=== DEBATE FOR: {event.headline} ===\n\n"
            thesis = ""
            # Round 1: Initial
            p1 = load_prompt("debate_primary_analyst.txt",EVENT_HEADLINE=event.headline,RAG_CONTEXT=rag)
            r1 = self.client.models.generate_content(model=GEMINI_MODEL,contents=p1,config=self.types.GenerateContentConfig(system_instruction="You are a Primary Macro Analyst."))
            thesis = r1.text; transcript += f"[ROUND 1 -- Primary Analyst]:\n{thesis}\n\n"

            consensus = False
            for rnd in range(1, self.max_rounds+1):
                pd = load_prompt("debate_devils_advocate.txt",RAG_CONTEXT=rag,CURRENT_THESIS=thesis)
                rd = self.client.models.generate_content(model=GEMINI_MODEL,contents=pd,config=self.types.GenerateContentConfig(system_instruction="You are a skeptical Devil's Advocate."))
                critique = rd.text; transcript += f"[ROUND {rnd} -- Devil's Advocate]:\n{critique}\n\n"
                if "[CONSENSUS REACHED]" in critique: consensus = True; break
                if rnd < self.max_rounds:
                    pr = f"Context Data: {rag}\n\nDevil's Advocate Critique:\n{critique}\n\nRebut or concede and adjust your thesis."
                    rr = self.client.models.generate_content(model=GEMINI_MODEL,contents=pr,config=self.types.GenerateContentConfig(system_instruction="You are the Primary Analyst."))
                    thesis = rr.text; transcript += f"[ROUND {rnd+1} -- Primary Analyst (Rebuttal)]:\n{thesis}\n\n"

            transcript += "=== END DEBATE ===\n\n"
            pj = load_prompt("debate_head_of_strategy.txt",MAX_ROUNDS=str(self.max_rounds),EVENT_HEADLINE=event.headline,DEBATE_TRANSCRIPT=transcript)
            rj = self.client.models.generate_content(model=GEMINI_MODEL,contents=pj,config=self.types.GenerateContentConfig(system_instruction="You are the Head of Strategy (JSON Output).",response_mime_type="application/json"))
            fj = json.loads(rj.text)
            transcript += f"[Head of Strategy]: {fj.get('macro_thesis')} (Conviction: {fj.get('conviction_score')})"
            return MacroOutput(event_id=event.event_id,macro_thesis=fj.get("macro_thesis",""),causal_chain=fj.get("causal_chain",[]),affected_factors=fj.get("affected_factors",[]),market_regime=fj.get("market_regime","Neutral"),expected_impact=fj.get("expected_impact","Neutral"),conviction_score=fj.get("conviction_score",3),time_horizon=fj.get("time_horizon","Medium-term"),reasoning_trace=transcript,processing_timestamp=pt)
        except Exception as e:
            print(f"  [WARN] Debate Error: {e}")
            return MacroOutput(event_id=event.event_id,macro_thesis="Error during debate.",causal_chain=[],affected_factors=[],market_regime="Unknown",expected_impact="Neutral",conviction_score=1,time_horizon="Unknown",reasoning_trace=str(e),processing_timestamp=pt)

def run_macro_agent(event: EventOutput) -> MacroOutput:
    return AdvancedMacroAgent().process_event(event)

def main():
    print("="*70+"\n  AGENT 2 -- MACRO INTERPRETATION (3-ROUND DEBATE)\n"+"="*70)
    ep = str(resolve_path(_CFG["paths"]["a1_events"]))
    if not os.path.exists(ep): print(f"[ERROR] {ep} not found. Run agent1 first."); return
    with open(ep,"r",encoding="utf-8") as f: events = [EventOutput(**e) for e in json.load(f)]
    print(f"[Agent 2] Loaded {len(events)} events")
    agent = AdvancedMacroAgent(); macros, merged = [], []
    for i, ev in enumerate(events):
        print(f"\n[{i+1}/{len(events)}] Debating: {ev.headline[:80]}...")
        m = agent.process_event(ev); macros.append(m)
        print(f"  -> Thesis:{m.macro_thesis[:80]}... Impact:{m.expected_impact} Conv:{m.conviction_score}/5")
        merged.append({"timestamp":ev.timestamp,"event_type":ev.event_type,"entities":ev.entities,"macro_thesis":m.macro_thesis,"confidence":m.conviction_score,"sentiment_score":ev.sentiment_score,"event_id":ev.event_id,"reasoning_trace":m.reasoning_trace})
        if not MOCK_MODE and i < len(events)-1: time.sleep(RATE_LIMIT_SEC)
    os.makedirs(os.path.dirname(str(resolve_path(_CFG["paths"]["a2_macro"]))),exist_ok=True)
    with open(str(resolve_path(_CFG["paths"]["a2_macro"])),"w",encoding="utf-8") as f: json.dump([m.model_dump() for m in macros],f,indent=4)
    with open(str(resolve_path(_CFG["paths"]["a1_a2_merged"])),"w",encoding="utf-8") as f: json.dump(merged,f,indent=4)
    print(f"\n[OK] Agent 2 complete -- saved {len(macros)} macro analyses")

if __name__ == "__main__": main()
