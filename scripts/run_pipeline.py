"""
==============================================================================
  END-TO-END PIPELINE RUNNER
  FIN580 Multi-Agent Brent Crude Trading System
==============================================================================
  Runs the complete 6-agent pipeline sequentially:
    A1 (Event) -> A2 (Macro) -> A3 (Signal) -> A4 (Risk) -> A5 (Portfolio) -> A6 (Report)

  Usage:
    python scripts/run_pipeline.py           # full pipeline (uses config.yaml mock_mode)
    python scripts/run_pipeline.py --mock    # force mock mode
    python scripts/run_pipeline.py --live    # force live API mode
    python scripts/run_pipeline.py --skip-report   # stop after A5
==============================================================================
"""

import sys, os, argparse

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import load_config, resolve_path
from agents.agent1_event import AdvancedEventAgent, MockNewsScraper, NewsAPIScraper
from agents.agent2_macro import AdvancedMacroAgent
from agents.agent3_signal import run_signal_agent
from agents.agent4_risk import RiskManagerAgent
from agents.agent5_portfolio import PortfolioManagerAgent

import json, time

def run_pipeline(mock_override=None, skip_report=False):
    cfg = load_config()
    mock = mock_override if mock_override is not None else cfg["pipeline"]["mock_mode"]
    rate = cfg["pipeline"]["rate_limit_sec"]

    print("=" * 70)
    print("  FIN580 MULTI-AGENT PIPELINE")
    print(f"  Mode: {'MOCK (no API calls)' if mock else 'LIVE (API calls enabled)'}")
    print("  A1 -> A2 -> A3 -> A4 -> A5" + (" -> A6" if not skip_report else ""))
    print("=" * 70)

    # ── AGENT 1: Event Detection ────────────────────────────────────────────
    print("\n" + "-" * 50 + "\n  STAGE 1: Event Detection\n" + "-" * 50)
    if mock:
        scraper = MockNewsScraper()
    else:
        from agents.agent1_event import NEWSAPI_KEY
        scraper = NewsAPIScraper(api_key=NEWSAPI_KEY)
    news = scraper.fetch_news()
    if not news and not mock:
        print("[WARN] Live fetch empty. Falling back to mock.")
        scraper = MockNewsScraper(); news = scraper.fetch_news()

    agent1 = AdvancedEventAgent()
    events = []
    for i, art in enumerate(news):
        print(f"  [{i+1}/{len(news)}] {art['headline'][:70]}...")
        ev = agent1.process_news(art["headline"], art["timestamp"], art["source"])
        events.append(ev)
        if not mock and i < len(news)-1: time.sleep(rate)

    out1 = str(resolve_path(cfg["paths"]["a1_events"]))
    os.makedirs(os.path.dirname(out1), exist_ok=True)
    with open(out1, "w", encoding="utf-8") as f:
        json.dump([e.model_dump() for e in events], f, indent=4)
    print(f"  [OK] {len(events)} events -> {out1}")

    # ── AGENT 2: Macro Debate ───────────────────────────────────────────────
    print("\n" + "-" * 50 + "\n  STAGE 2: Macro Debate\n" + "-" * 50)
    agent2 = AdvancedMacroAgent()
    macros, merged = [], []
    for i, ev in enumerate(events):
        print(f"  [{i+1}/{len(events)}] Debating: {ev.headline[:60]}...")
        m = agent2.process_event(ev); macros.append(m)
        merged.append({"timestamp":ev.timestamp,"event_type":ev.event_type,"entities":ev.entities,
                        "macro_thesis":m.macro_thesis,"confidence":m.conviction_score,
                        "sentiment_score":ev.sentiment_score,"event_id":ev.event_id,
                        "reasoning_trace":m.reasoning_trace})
        if not mock and i < len(events)-1: time.sleep(rate)

    out2 = str(resolve_path(cfg["paths"]["a2_macro"]))
    with open(out2, "w", encoding="utf-8") as f:
        json.dump([m.model_dump() for m in macros], f, indent=4)
    out_m = str(resolve_path(cfg["paths"]["a1_a2_merged"]))
    with open(out_m, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4)
    print(f"  [OK] {len(macros)} macro analyses -> {out2}")

    # ── AGENT 3: Signal Generation ──────────────────────────────────────────
    print("\n" + "-" * 50 + "\n  STAGE 3: Signal Generation\n" + "-" * 50)
    signals = [run_signal_agent(m) for m in macros]
    out3 = str(resolve_path(cfg["paths"]["a3_signals"]))
    with open(out3, "w", encoding="utf-8") as f:
        json.dump([s.model_dump() for s in signals], f, indent=4)
    long_n = sum(1 for s in signals if s.direction == "LONG")
    short_n = sum(1 for s in signals if s.direction == "SHORT")
    flat_n = sum(1 for s in signals if s.direction == "FLAT")
    print(f"  [OK] {len(signals)} signals (LONG:{long_n} SHORT:{short_n} FLAT:{flat_n}) -> {out3}")

    # ── AGENT 4: Risk Management ────────────────────────────────────────────
    print("\n" + "-" * 50 + "\n  STAGE 4: Risk Management\n" + "-" * 50)
    agent4 = RiskManagerAgent()
    decisions = [agent4.evaluate_signal(s) for s in signals]
    out4 = str(resolve_path(cfg["paths"]["a4_risk"]))
    with open(out4, "w", encoding="utf-8") as f:
        json.dump([d.model_dump() for d in decisions], f, indent=4)
    approved = sum(1 for d in decisions if d.approved)
    print(f"  [OK] {len(decisions)} decisions (Approved:{approved} Vetoed:{len(decisions)-approved}) -> {out4}")

    # ── AGENT 5: Portfolio Construction ──────────────────────────────────────
    print("\n" + "-" * 50 + "\n  STAGE 5: Portfolio Construction\n" + "-" * 50)
    agent5 = PortfolioManagerAgent()
    trades = [agent5.size_trade(d) for d in decisions if d.approved]
    trades = [t for t in trades if t]
    out5 = str(resolve_path(cfg["paths"]["a5_trades"]))
    with open(out5, "w", encoding="utf-8") as f:
        json.dump([t.model_dump() for t in trades], f, indent=4)
    total_usd = sum(t.size_usd for t in trades)
    print(f"  [OK] {len(trades)} trades (${total_usd:,.2f} deployed) -> {out5}")

    # ── AGENT 6: Report Generation ──────────────────────────────────────────
    if not skip_report:
        print("\n" + "-" * 50 + "\n  STAGE 6: Report Generation\n" + "-" * 50)
        from agents.agent6_result import load_agent_outputs, build_summaries
        from agents.agent6_result import generate_report_with_gemini, generate_fallback_report, save_report_to_docx
        data = load_agent_outputs()
        a1s, a2s, a3s, a4s, a5s = build_summaries(data)
        try:
            report = generate_report_with_gemini(a1s, a2s, a3s, a4s, a5s)
        except Exception:
            report = generate_fallback_report(a1s, a2s, a3s, a4s, a5s)
        rp = str(resolve_path(cfg["paths"]["report_md"]))
        with open(rp, "w", encoding="utf-8") as f: f.write(report)
        print(f"  [OK] Report -> {rp}")
        try: save_report_to_docx(report, str(resolve_path(cfg["paths"]["report_docx"])))
        except Exception: pass

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FIN580 Multi-Agent Pipeline Runner")
    parser.add_argument("--mock", action="store_true", help="Force mock mode (no API calls)")
    parser.add_argument("--live", action="store_true", help="Force live API mode")
    parser.add_argument("--skip-report", action="store_true", help="Skip Agent 6 report generation")
    args = parser.parse_args()
    mock_override = None
    if args.mock: mock_override = True
    elif args.live: mock_override = False
    run_pipeline(mock_override=mock_override, skip_report=args.skip_report)
