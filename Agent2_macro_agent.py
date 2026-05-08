"""
==============================================================================
  AGENT 2 -- MACRO INTERPRETATION (3-Round Debate Committee) (Student A)
  FIN580 Quantamental Investment Project -- Brent Crude Oil
==============================================================================
  This agent reads the structured events produced by Agent 1 and applies a
  multi-agent LLM debate to generate macro-economic theses.

  Pipeline:
    1. Load events from data/processed/a1_events.json  (Agent 1 output)
    2. For each event, run a 3-round debate:
         - Primary Analyst   -> initial thesis
         - Devil's Advocate  -> critique / challenge
         - Repeat for 3 rounds or until [CONSENSUS REACHED]
         - Head of Strategy  -> final JSON synthesis
    3. Save structured macro outputs + merged handshake file for Student B

  Usage:
    python macro_agent.py

  Output:
    data/processed/a2_macro.json       ->  full macro analysis audit trail
    data/processed/a1_a2_merged.json   ->  handshake file for Student B
==============================================================================
"""

import os
import json
import time
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Optional

# ── Import EventOutput from Agent 1 ────────────────────────────────────────
from Agent1_event_agent import EventOutput, GEMINI_API_KEY

# ── Config ──────────────────────────────────────────────────────────────────
GEMINI_MODEL   = "gemini-2.5-flash"
MOCK_MODE      = False           # Set True to skip all API calls
RATE_LIMIT_SEC = 2              # Seconds to sleep between articles (paid tier)
MAX_ROUNDS     = 3              # Maximum debate rounds

# ============================================================================
#   SCHEMA: MacroOutput  (inlined so no external schema dependency)
# ============================================================================
class MacroOutput(BaseModel):
    """Schema for Agent 2 output -- consumed by Agent 3 (Student B)"""
    event_id: str
    macro_thesis: str
    causal_chain: List[str]
    affected_factors: List[str]
    market_regime: str
    expected_impact: str
    conviction_score: int
    time_horizon: str
    reasoning_trace: Optional[str] = None
    processing_timestamp: Optional[str] = None


class AdvancedMacroAgent:
    """
    Agent 2: Macro Interpretation via Multi-Agent Debate
    ----------------------------------------------------
    Architecture:
      - Primary Analyst  -- proposes an initial macro thesis
      - Devil's Advocate  -- critiques & challenges the thesis
      - 3 rounds of iterative debate
      - Head of Strategy (Judge) -- synthesizes final consensus
    """

    def __init__(self):
        self.mock_mode = MOCK_MODE
        self.max_rounds = MAX_ROUNDS
        print("[Agent 2] Initializing Macro Debate Committee (Gemini)...")
        if not self.mock_mode:
            from google import genai
            from google.genai import types
            self.genai = genai
            self.types = types
            self.client = genai.Client(api_key=GEMINI_API_KEY)

    def _get_rag_context(self, event: EventOutput) -> str:
        """
        Retrieves macroeconomic context data for the debate.
        In production, this would pull live data from FRED API / Bloomberg.
        """
        context = """
        [MACROECONOMIC CONTEXT -- DEEP DIVE MATERIAL]
        - Current VIX: 22.5 (Elevated fear, risk-off sentiment)
        - US Fed Funds Rate: 5.25% - 5.50% (High, suppressing economic growth)
        - Global Oil Inventories: 4% below 5-year average (Tight physical supply)
        - China Manufacturing PMI: 49.2 (Contraction territory, weak demand)
        - US Dollar Index (DXY): 104.5 (Strong dollar, bearish for commodities)
        - Geopolitical Risk Index: High (Middle East tensions)
        """
        return context

    def process_event(self, event: EventOutput) -> MacroOutput:
        """Run a 3-round adversarial debate and return a MacroOutput."""
        processing_time = datetime.now(timezone.utc).isoformat()
        rag_context = self._get_rag_context(event)

        # ── Mock path ───────────────────────────────────────────────────────
        if self.mock_mode:
            mock_debate = (
                f"=== DEBATE TRANSCRIPT FOR EVENT: {event.headline} ===\n\n"
                "[ROUND 1 -- Primary Analyst (Initial Thesis)]:\n"
                "The event represents a severe supply shock. Given that global oil "
                "inventories are already 4% below the 5-year average, this event will "
                "immediately tighten physical markets. I expect strong bullish momentum.\n\n"
                "[ROUND 1 -- Devil's Advocate (Critique)]:\n"
                "Your analysis ignores the demand side entirely. China's PMI is at 49.2 "
                "(contraction) and the US Fed Funds Rate is at a restrictive 5.25%-5.50%. "
                "A strong dollar (DXY 104.5) also creates headwinds.\n\n"
                "[ROUND 2 -- Primary Analyst (Rebuttal)]:\n"
                "I acknowledge the demand headwinds. However, the Geopolitical Risk Index "
                "is currently High. Historically, when physical supply is tight AND "
                "geopolitical risk is high, risk-premiums override base-demand concerns.\n\n"
                "[ROUND 2 -- Devil's Advocate (Critique)]:\n"
                "Risk premiums are transient. Once the immediate fear subsides, the "
                "structural demand weakness from China and high rates will dominate.\n\n"
                "[ROUND 3 -- Primary Analyst (Concession)]:\n"
                "I concede. The bullish impact will be short-term and capped.\n\n"
                "[ROUND 3 -- Devil's Advocate (Consensus)]:\n"
                "[CONSENSUS REACHED] We agree on a short-term, capped bullish impact.\n\n"
                "=== END DEBATE ===\n\n"
                "[Head of Strategy (Final Synthesis)]:\n"
                "Consensus after 3 rounds. Short-term bullish spike driven by tight "
                "inventories and geopolitical risk. Structural demand weakness caps "
                "long-term upside. Conviction: 4."
            )
            return MacroOutput(
                event_id=event.event_id,
                macro_thesis="Short-term bullish spike driven by supply tightness, "
                             "but upside is capped by structural demand weakness "
                             "and high interest rates.",
                causal_chain=[
                    "Event tightens supply",
                    "Risk premium spikes short-term",
                    "High rates and weak China PMI suppress long-term demand",
                    "Net result: Capped short-term bullishness",
                ],
                affected_factors=["Inventories", "Geopolitical Risk", "Interest Rates", "PMI"],
                market_regime="Stagflationary",
                expected_impact="Bullish Brent",
                conviction_score=4,
                time_horizon="Short-term",
                reasoning_trace=mock_debate,
                processing_timestamp=processing_time,
            )

        # ── Live Gemini path -- 3-Round Debate ───────────────────────────────
        try:
            debate_transcript = f"=== DEBATE TRANSCRIPT FOR EVENT: {event.headline} ===\n\n"
            current_thesis = ""

            # ROUND 1: Initial Proposal
            prompt_initial = (
                f"Event: {event.headline}\n"
                f"Context Data: {rag_context}\n\n"
                "Based on the context, provide an initial macro thesis on how "
                "this impacts Brent Crude prices."
            )
            res_1 = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt_initial,
                config=self.types.GenerateContentConfig(
                    system_instruction="You are a Primary Macro Analyst."
                ),
            )
            current_thesis = res_1.text
            debate_transcript += f"[ROUND 1 -- Primary Analyst]:\n{current_thesis}\n\n"

            # Iterative Debate Loop
            consensus_reached = False
            for round_num in range(1, self.max_rounds + 1):
                # Devil's Advocate Turn
                prompt_devil = (
                    f"Context Data: {rag_context}\n\n"
                    f"Primary Analyst's Current Thesis:\n{current_thesis}\n\n"
                    "Critique this thesis. Find flaws, use the context data to "
                    "challenge it. If the thesis is flawless and incorporates "
                    "your past critiques, output exactly [CONSENSUS REACHED]."
                )
                res_devil = self.client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt_devil,
                    config=self.types.GenerateContentConfig(
                        system_instruction="You are a skeptical Devil's Advocate."
                    ),
                )
                critique = res_devil.text
                debate_transcript += f"[ROUND {round_num} -- Devil's Advocate]:\n{critique}\n\n"

                if "[CONSENSUS REACHED]" in critique:
                    consensus_reached = True
                    break

                # Primary Analyst Rebuttal (skip on final round)
                if round_num < self.max_rounds:
                    prompt_rebuttal = (
                        f"Context Data: {rag_context}\n\n"
                        f"Devil's Advocate Critique:\n{critique}\n\n"
                        "Your previous thesis was challenged. Deep-dive into the "
                        "Context Data to find new evidence to rebut, OR concede "
                        "and adjust your thesis to incorporate their valid points."
                    )
                    res_rebuttal = self.client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=prompt_rebuttal,
                        config=self.types.GenerateContentConfig(
                            system_instruction="You are the Primary Analyst."
                        ),
                    )
                    current_thesis = res_rebuttal.text
                    debate_transcript += (
                        f"[ROUND {round_num+1} -- Primary Analyst (Rebuttal)]:\n"
                        f"{current_thesis}\n\n"
                    )

            debate_transcript += "=== END DEBATE ===\n\n"

            # The Judge — Head of Strategy
            prompt_judge = f"""
            Review this {self.max_rounds}-round debate transcript regarding: {event.headline}

            {debate_transcript}

            Synthesize the final view. If consensus was reached early, Conviction
            is High (4-5). If 3 rounds passed with ongoing disagreement, Conviction
            is Low (1-2).

            Output MUST be valid JSON:
            {{
                "macro_thesis": "string (1-2 sentence final synthesis)",
                "causal_chain": ["string", "string"],
                "affected_factors": ["string", "string"],
                "market_regime": "string",
                "expected_impact": "string (Bullish Brent, Bearish Brent, Neutral)",
                "conviction_score": int (1 to 5),
                "time_horizon": "string"
            }}
            """
            res_judge = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt_judge,
                config=self.types.GenerateContentConfig(
                    system_instruction="You are the Head of Strategy (JSON Output).",
                    response_mime_type="application/json",
                ),
            )

            final_json = json.loads(res_judge.text)
            debate_transcript += (
                f"[Head of Strategy (Final Synthesis)]:\n"
                f"{final_json.get('macro_thesis')} "
                f"(Conviction: {final_json.get('conviction_score')})"
            )

            return MacroOutput(
                event_id=event.event_id,
                macro_thesis=final_json.get("macro_thesis", ""),
                causal_chain=final_json.get("causal_chain", []),
                affected_factors=final_json.get("affected_factors", []),
                market_regime=final_json.get("market_regime", "Neutral"),
                expected_impact=final_json.get("expected_impact", "Neutral"),
                conviction_score=final_json.get("conviction_score", 3),
                time_horizon=final_json.get("time_horizon", "Medium-term"),
                reasoning_trace=debate_transcript,
                processing_timestamp=processing_time,
            )

        except Exception as e:
            print(f"  [WARN] Debate Error: {e}")
            return MacroOutput(
                event_id=event.event_id,
                macro_thesis="Error occurred during debate.",
                causal_chain=[], affected_factors=[],
                market_regime="Unknown", expected_impact="Neutral",
                conviction_score=1, time_horizon="Unknown",
                reasoning_trace=str(e),
                processing_timestamp=processing_time,
            )


# ============================================================================
#   Wrapper function for main.py pipeline integration
# ============================================================================
def run_macro_agent(event: EventOutput) -> MacroOutput:
    """Convenience wrapper: instantiate agent, process one event, return MacroOutput."""
    agent = AdvancedMacroAgent()
    return agent.process_event(event)


# ============================================================================
def main():
    print("=" * 70)
    print("  AGENT 2 -- MACRO INTERPRETATION (3-ROUND DEBATE)")
    print("=" * 70)

    # 1. Load Agent 1 output
    events_path = "data/processed/a1_events.json"
    if not os.path.exists(events_path):
        print(f"[ERROR] Cannot find {events_path}. Please run event_agent.py first.")
        return

    with open(events_path, "r") as f:
        events_raw = json.load(f)
    events = [EventOutput(**e) for e in events_raw]
    print(f"[Agent 2] Loaded {len(events)} events from {events_path}")

    # 2. Initialize agent
    agent = AdvancedMacroAgent()

    # 3. Process each event
    macros = []
    merged = []
    total = len(events)

    for i, event in enumerate(events):
        print(f"\n[{i+1}/{total}] Debating: {event.headline[:80]}...")
        macro = agent.process_event(event)
        macros.append(macro)
        print(f"  -> Thesis     : {macro.macro_thesis[:100]}...")
        print(f"  -> Impact     : {macro.expected_impact}")
        print(f"  -> Conviction : {macro.conviction_score}/5")
        print(f"  -> Regime     : {macro.market_regime}")

        # Build merged row for Student B handshake
        merged.append({
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "entities": event.entities,
            "macro_thesis": macro.macro_thesis,
            "confidence": macro.conviction_score,
            "sentiment_score": event.sentiment_score,
            "event_id": event.event_id,
            "reasoning_trace": macro.reasoning_trace,
        })

        # Rate limit (skip on last article)
        if not MOCK_MODE and i < total - 1:
            print(f"  -> Sleeping {RATE_LIMIT_SEC}s for API rate limits...")
            time.sleep(RATE_LIMIT_SEC)

    # 4. Save outputs
    os.makedirs("data/processed", exist_ok=True)

    macro_path = "data/processed/a2_macro.json"
    with open(macro_path, "w") as f:
        json.dump([m.model_dump() for m in macros], f, indent=4)

    merged_path = "data/processed/a1_a2_merged.json"
    with open(merged_path, "w") as f:
        json.dump(merged, f, indent=4)

    print(f"\n[OK] Agent 2 complete -- saved {len(macros)} macro analyses to {macro_path}")
    print(f"[OK] Handshake file for Student B: {merged_path}")

if __name__ == "__main__":
    main()
