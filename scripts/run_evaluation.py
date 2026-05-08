"""
==============================================================================
  EVALUATION & ABLATION SCRIPT
  FIN580 Multi-Agent Brent Crude Trading System
==============================================================================
  Runs the pipeline in mock mode with and without specific agents to measure
  each agent's marginal contribution. Outputs comparison metrics.

  Usage:
    python scripts/run_evaluation.py
==============================================================================
"""

import sys, os, json, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import load_config, resolve_path
from agents.agent1_event import AdvancedEventAgent, MockNewsScraper, EventOutput
from agents.agent2_macro import AdvancedMacroAgent, MacroOutput
from agents.agent3_signal import run_signal_agent, SignalOutput
from agents.agent4_risk import RiskManagerAgent
from agents.agent5_portfolio import PortfolioManagerAgent


def run_full_mock_pipeline():
    """Run full A1->A5 in mock mode, return metrics dict."""
    scraper = MockNewsScraper()
    news = scraper.fetch_news()
    agent1 = AdvancedEventAgent()
    events = [agent1.process_news(a["headline"], a["timestamp"], a["source"]) for a in news]

    agent2 = AdvancedMacroAgent()
    macros = [agent2.process_event(ev) for ev in events]

    signals = [run_signal_agent(m) for m in macros]

    agent4 = RiskManagerAgent()
    decisions = [agent4.evaluate_signal(s) for s in signals]

    agent5 = PortfolioManagerAgent()
    trades = [agent5.size_trade(d) for d in decisions if d.approved]
    trades = [t for t in trades if t]

    return {
        "events": len(events),
        "macros": len(macros),
        "signals_total": len(signals),
        "signals_long": sum(1 for s in signals if s.direction == "LONG"),
        "signals_short": sum(1 for s in signals if s.direction == "SHORT"),
        "signals_flat": sum(1 for s in signals if s.direction == "FLAT"),
        "approved": sum(1 for d in decisions if d.approved),
        "vetoed": sum(1 for d in decisions if not d.approved),
        "trades": len(trades),
        "capital_deployed": sum(t.size_usd for t in trades),
        "avg_conviction": sum(s.conviction for s in signals) / len(signals) if signals else 0,
    }


def run_ablation_no_risk():
    """Ablation: skip Agent 4 risk filter, pass all signals directly to A5."""
    scraper = MockNewsScraper()
    news = scraper.fetch_news()
    agent1 = AdvancedEventAgent()
    events = [agent1.process_news(a["headline"], a["timestamp"], a["source"]) for a in news]

    agent2 = AdvancedMacroAgent()
    macros = [agent2.process_event(ev) for ev in events]
    signals = [run_signal_agent(m) for m in macros]

    # Skip A4: approve everything
    from agents.agent4_risk import RiskOutput
    all_approved = [RiskOutput(signal=s, approved=True, veto_reason="No risk gate", risk_multiplier=1.0) for s in signals]

    agent5 = PortfolioManagerAgent()
    trades = [agent5.size_trade(d) for d in all_approved]
    trades = [t for t in trades if t]

    return {
        "label": "No Risk Gate (A4 removed)",
        "trades": len(trades),
        "capital_deployed": sum(t.size_usd for t in trades),
        "approved": len(signals),
        "vetoed": 0,
    }


def run_ablation_strict_risk():
    """Ablation: strict risk — min conviction = 4."""
    scraper = MockNewsScraper()
    news = scraper.fetch_news()
    agent1 = AdvancedEventAgent()
    events = [agent1.process_news(a["headline"], a["timestamp"], a["source"]) for a in news]

    agent2 = AdvancedMacroAgent()
    macros = [agent2.process_event(ev) for ev in events]
    signals = [run_signal_agent(m) for m in macros]

    agent4 = RiskManagerAgent(min_conviction=4)
    decisions = [agent4.evaluate_signal(s) for s in signals]

    agent5 = PortfolioManagerAgent()
    trades = [agent5.size_trade(d) for d in decisions if d.approved]
    trades = [t for t in trades if t]

    return {
        "label": "Strict Risk (min_conviction=4)",
        "trades": len(trades),
        "capital_deployed": sum(t.size_usd for t in trades),
        "approved": sum(1 for d in decisions if d.approved),
        "vetoed": sum(1 for d in decisions if not d.approved),
    }


def main():
    print("=" * 70)
    print("  EVALUATION & ABLATION STUDY")
    print("  FIN580 Multi-Agent Trading System")
    print("=" * 70)

    # 1. Baseline (full pipeline)
    print("\n[1/3] Running BASELINE (full pipeline, mock mode)...")
    baseline = run_full_mock_pipeline()

    # 2. Ablation: no risk gate
    print("[2/3] Running ABLATION: No Risk Gate...")
    no_risk = run_ablation_no_risk()

    # 3. Ablation: strict risk
    print("[3/3] Running ABLATION: Strict Risk (min_conviction=4)...")
    strict = run_ablation_strict_risk()

    # Print comparison table
    print("\n" + "=" * 70)
    print("  EVALUATION RESULTS")
    print("=" * 70)
    print(f"\n{'Metric':<30} {'Baseline':<15} {'No Risk Gate':<15} {'Strict Risk':<15}")
    print("-" * 75)
    print(f"{'Events Detected':<30} {baseline['events']:<15}")
    print(f"{'Macro Analyses':<30} {baseline['macros']:<15}")
    print(f"{'Signals (LONG)':<30} {baseline['signals_long']:<15}")
    print(f"{'Signals (SHORT)':<30} {baseline['signals_short']:<15}")
    print(f"{'Signals (FLAT)':<30} {baseline['signals_flat']:<15}")
    print(f"{'Avg Conviction':<30} {baseline['avg_conviction']:<15.1f}")
    print(f"{'Approved':<30} {baseline['approved']:<15} {no_risk['approved']:<15} {strict['approved']:<15}")
    print(f"{'Vetoed':<30} {baseline['vetoed']:<15} {no_risk['vetoed']:<15} {strict['vetoed']:<15}")
    print(f"{'Trades Executed':<30} {baseline['trades']:<15} {no_risk['trades']:<15} {strict['trades']:<15}")
    print(f"{'Capital Deployed ($)':<30} {baseline['capital_deployed']:<15,.2f} {no_risk['capital_deployed']:<15,.2f} {strict['capital_deployed']:<15,.2f}")

    # Save evaluation report
    report_lines = [
        "# Evaluation & Ablation Report",
        f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Baseline (Full Pipeline)",
        f"- Events: {baseline['events']}",
        f"- Signals: {baseline['signals_total']} (LONG:{baseline['signals_long']} SHORT:{baseline['signals_short']} FLAT:{baseline['signals_flat']})",
        f"- Approved: {baseline['approved']} | Vetoed: {baseline['vetoed']}",
        f"- Trades: {baseline['trades']} | Capital: ${baseline['capital_deployed']:,.2f}",
        "",
        "## Ablation: No Risk Gate (A4 Removed)",
        f"- Trades: {no_risk['trades']} | Capital: ${no_risk['capital_deployed']:,.2f}",
        f"- All {no_risk['approved']} signals approved (no filtering)",
        "",
        "## Ablation: Strict Risk (min_conviction=4)",
        f"- Approved: {strict['approved']} | Vetoed: {strict['vetoed']}",
        f"- Trades: {strict['trades']} | Capital: ${strict['capital_deployed']:,.2f}",
        "",
        "## Key Findings",
        f"- Risk gate (A4) vetoed {baseline['vetoed']} of {baseline['signals_total']} signals ({baseline['vetoed']/baseline['signals_total']*100:.0f}%)" if baseline['signals_total'] > 0 else "- No signals to evaluate",
        f"- Removing risk gate increases capital deployment by ${no_risk['capital_deployed']-baseline['capital_deployed']:,.2f}",
        f"- Strict conviction threshold reduces trades from {baseline['trades']} to {strict['trades']}",
    ]

    os.makedirs(str(resolve_path("logs")), exist_ok=True)
    eval_path = str(resolve_path("logs/evaluation_report.md"))
    with open(eval_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\n[OK] Evaluation report saved to {eval_path}")

    # Also save JSON
    eval_json = str(resolve_path("logs/evaluation_results.json"))
    with open(eval_json, "w", encoding="utf-8") as f:
        json.dump({"baseline": baseline, "no_risk_gate": no_risk, "strict_risk": strict}, f, indent=2)
    print(f"[OK] JSON results saved to {eval_json}")


if __name__ == "__main__":
    main()
