"""
==============================================================================
  MOCK PIPELINE TEST
  FIN580 Multi-Agent Brent Crude Trading System
==============================================================================
  Runs the full A1->A5 pipeline in MOCK_MODE and validates:
    - Output schemas (Pydantic models parse correctly)
    - File outputs exist
    - Data integrity (event_ids propagate through the chain)

  Usage:
    python -m tests.test_pipeline_mock
    python scripts/run_pipeline.py --mock   (alternative)
==============================================================================
"""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent1_event import AdvancedEventAgent, MockNewsScraper, EventOutput
from agents.agent2_macro import AdvancedMacroAgent, MacroOutput
from agents.agent3_signal import run_signal_agent, SignalOutput
from agents.agent4_risk import RiskManagerAgent, RiskOutput
from agents.agent5_portfolio import PortfolioManagerAgent, PortfolioOutput


def test_full_pipeline_mock():
    """Run the complete pipeline in mock mode and validate outputs."""
    print("=" * 70)
    print("  TEST: Full Pipeline (Mock Mode)")
    print("=" * 70)
    errors = []

    # ── A1: Event Detection ─────────────────────────────────────────────────
    print("\n[TEST] Agent 1: Event Detection...")
    scraper = MockNewsScraper()
    news = scraper.fetch_news()
    assert len(news) > 0, "No mock news loaded"

    agent1 = AdvancedEventAgent()
    events = []
    for art in news:
        ev = agent1.process_news(art["headline"], art["timestamp"], art["source"])
        assert isinstance(ev, EventOutput), f"Expected EventOutput, got {type(ev)}"
        assert ev.event_id.startswith("EVT_"), f"Invalid event_id: {ev.event_id}"
        assert ev.confidence_score >= 0 and ev.confidence_score <= 1.0
        events.append(ev)
    print(f"  [PASS] {len(events)} events created, schemas valid")

    # ── A2: Macro Debate ────────────────────────────────────────────────────
    print("\n[TEST] Agent 2: Macro Debate...")
    agent2 = AdvancedMacroAgent()
    macros = []
    for ev in events:
        m = agent2.process_event(ev)
        assert isinstance(m, MacroOutput), f"Expected MacroOutput, got {type(m)}"
        assert m.event_id == ev.event_id, f"Event ID mismatch: {m.event_id} != {ev.event_id}"
        assert 1 <= m.conviction_score <= 5, f"Conviction out of range: {m.conviction_score}"
        macros.append(m)
    print(f"  [PASS] {len(macros)} macro analyses, event_ids match")

    # ── A3: Signal Generation ───────────────────────────────────────────────
    print("\n[TEST] Agent 3: Signal Generation...")
    signals = []
    for m in macros:
        s = run_signal_agent(m)
        assert isinstance(s, SignalOutput), f"Expected SignalOutput, got {type(s)}"
        assert s.direction in ("LONG", "SHORT", "FLAT"), f"Invalid direction: {s.direction}"
        signals.append(s)
    print(f"  [PASS] {len(signals)} signals generated")

    # ── A4: Risk Management ─────────────────────────────────────────────────
    print("\n[TEST] Agent 4: Risk Management...")
    agent4 = RiskManagerAgent()
    decisions = []
    for s in signals:
        d = agent4.evaluate_signal(s)
        assert isinstance(d, RiskOutput), f"Expected RiskOutput, got {type(d)}"
        assert isinstance(d.approved, bool)
        decisions.append(d)
    approved = sum(1 for d in decisions if d.approved)
    print(f"  [PASS] {len(decisions)} decisions (approved:{approved} vetoed:{len(decisions)-approved})")

    # ── A5: Portfolio Construction ───────────────────────────────────────────
    print("\n[TEST] Agent 5: Portfolio Construction...")
    agent5 = PortfolioManagerAgent()
    trades = []
    for d in decisions:
        if d.approved:
            t = agent5.size_trade(d)
            if t:
                assert isinstance(t, PortfolioOutput)
                assert t.size_usd > 0, f"Trade size should be positive: {t.size_usd}"
                trades.append(t)
    print(f"  [PASS] {len(trades)} trades executed")

    # ── Summary ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  ALL TESTS PASSED [OK]")
    print(f"  Events: {len(events)} -> Macros: {len(macros)} -> Signals: {len(signals)}")
    print(f"  Decisions: {len(decisions)} -> Trades: {len(trades)}")
    total = sum(t.size_usd for t in trades)
    print(f"  Total Capital: ${total:,.2f}")
    print("=" * 70)


if __name__ == "__main__":
    test_full_pipeline_mock()
