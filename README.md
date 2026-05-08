# FIN580 — Multi-Agent Brent Crude Oil Trading System

> A 6-agent LLM-powered quantamental investment pipeline for Brent Crude Oil, built for **FIN580: Quantamental Investment**.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Overview

This project implements a **multi-agent sequential pipeline** that processes real-time news events to generate risk-managed portfolio trades for Brent Crude Oil (`BZ=F`). Each agent handles a distinct responsibility in the investment decision chain:

```
News Feed ──► A1 (Event) ──► A2 (Macro Debate) ──► A3 (Signal)
                                                        │
                A6 (Report) ◄── A5 (Portfolio) ◄── A4 (Risk) ◄──┘
```

### Agent Responsibilities

| Agent | Role | Student | Key Technology |
|-------|------|---------|----------------|
| **A1** — Event Detection | Classify news events (type, bias, confidence) | Student A | FinBERT + spaCy + Gemini |
| **A2** — Macro Interpretation | 3-round adversarial LLM debate to form macro theses | Student A | Gemini (multi-agent debate) |
| **A3** — Signal Generation | Convert macro theses → LONG / SHORT / FLAT signals | Student B | Rule-based + historical analogs |
| **A4** — Risk Management | VIX, drawdown, and conviction gating | Student C | Threshold-based risk filter |
| **A5** — Portfolio Construction | Size trades under capital constraints | Student C | Position sizing engine |
| **A6** — Report Generation | Synthesize all outputs into a professional report | Student A | Gemini |

---

## 🏗️ Project Structure

```
FIN580/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.yaml                        # Central configuration (all tunable params)
├── .env.example                       # Template for API keys
├── .gitignore                         # Git ignore rules
│
├── agents/                            # Core agent modules
│   ├── __init__.py                    # Config loader, prompt loader, path utils
│   ├── agent1_event.py                # A1: Event Detection (FinBERT + spaCy + Gemini)
│   ├── agent2_macro.py                # A2: 3-Round Adversarial Macro Debate
│   ├── agent3_signal.py               # A3: Signal Generation
│   ├── agent4_risk.py                 # A4: Risk Management
│   ├── agent5_portfolio.py            # A5: Portfolio Construction
│   └── agent6_result.py               # A6: Report Generator (Gemini + fallback)
│
├── prompts/                           # Externalized LLM prompt templates
│   ├── event_classification.txt       # A1: Event classification system prompt
│   ├── debate_primary_analyst.txt     # A2: Primary analyst initial thesis
│   ├── debate_devils_advocate.txt     # A2: Devil's advocate critique
│   ├── debate_head_of_strategy.txt    # A2: Head of strategy final synthesis
│   └── report_generation.txt          # A6: Report generation prompt
│
├── scripts/                           # Runnable scripts
│   ├── run_pipeline.py                # End-to-end pipeline (A1→A6)
│   ├── run_backtest.py                # Backtesting engine (PnL, Sharpe, drawdown)
│   └── run_evaluation.py              # Ablation study & evaluation metrics
│
├── data/
│   ├── sample/                        # Sample input data (committed)
│   │   └── mock_news.json             # 5 sample Brent Crude news articles
│   └── processed/                     # Pipeline outputs (gitignored)
│       └── .gitkeep
│
├── logs/                              # Trade & audit logs (gitignored)
│   └── .gitkeep
│
└── tests/
    └── test_pipeline_mock.py          # Integration test (mock mode)
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/FIN580.git
cd FIN580

# Create virtual environment
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (required for Agent 1 in live mode)
python -m spacy download en_core_web_sm
```

### 2. Configure API Keys (Optional — only for live mode)

```bash
cp .env.example .env
# Edit .env and add your keys:
#   GEMINI_API_KEY=your_key_here
#   NEWSAPI_KEY=your_key_here
```

> **Note**: The system runs in **mock mode by default** (`config.yaml` → `mock_mode: true`). No API keys are needed for demo/testing.

### 3. Run the Pipeline

```bash
# Full pipeline in mock mode (default — no API keys needed)
python scripts/run_pipeline.py --mock

# Full pipeline in live mode (requires API keys in .env)
python scripts/run_pipeline.py --live

# Skip report generation
python scripts/run_pipeline.py --mock --skip-report
```

### 4. Run Backtesting

```bash
# Default: 30 mock signals, $1M capital
python scripts/run_backtest.py

# Custom parameters
python scripts/run_backtest.py --signals 100 --capital 5000000
```

### 5. Run Evaluation / Ablation Study

```bash
python scripts/run_evaluation.py
```

This runs three scenarios and compares:
- **Baseline**: Full pipeline with default risk parameters
- **No Risk Gate**: Agent 4 removed (all signals approved)
- **Strict Risk**: Minimum conviction raised to 4

### 6. Run Tests

```bash
python -m tests.test_pipeline_mock
```

---

## ⚙️ Configuration

All tunable parameters are in [`config.yaml`](config.yaml):

| Section | Parameter | Default | Description |
|---------|-----------|---------|-------------|
| `pipeline.mock_mode` | `true` | Skip API calls, use deterministic mock data |
| `pipeline.rate_limit_sec` | `2` | Seconds between API calls |
| `gemini.model` | `gemini-2.5-flash` | Gemini model identifier |
| `agent1.finbert_model` | `ProsusAI/finbert` | FinBERT model for sentiment |
| `agent1.spacy_model` | `en_core_web_sm` | spaCy NER model |
| `agent2.max_debate_rounds` | `3` | Rounds of adversarial debate |
| `agent4.min_conviction` | `3` | Minimum conviction to approve |
| `agent4.max_vix` | `30.0` | VIX threshold for risk scaling |
| `agent5.initial_capital` | `1000000` | Starting capital ($) |
| `agent5.max_position_pct` | `0.10` | Max 10% of capital per trade |

---

## 📊 Sample Output

After running `python scripts/run_pipeline.py --mock`, you'll find in `data/processed/`:

| File | Description |
|------|-------------|
| `a1_events.json` | Structured events with sentiment scores and entity tags |
| `a2_macro.json` | Macro theses with full debate transcripts |
| `a1_a2_merged.json` | Handshake file merging A1 + A2 outputs |
| `a3_signals.json` | LONG / SHORT / FLAT trading signals |
| `a4_risk_decisions.json` | Risk gate approval/veto decisions |
| `a5_portfolio_trades.json` | Final sized trade orders |
| `analysis_report.md` | Professional Markdown analysis report |

---

## 🧪 Agent 2: Adversarial Debate Architecture

Agent 2 uses a unique **3-round adversarial debate** to stress-test macro theses:

```
┌─────────────────┐     ┌────────────────────┐     ┌─────────────────┐
│ Primary Analyst  │────►│  Devil's Advocate   │────►│ Head of Strategy│
│ (Initial Thesis) │◄────│  (Critique/Rebut)   │     │ (Final Judge)   │
└─────────────────┘     └────────────────────┘     └─────────────────┘
       Round 1 ──────────► Round 2 ──────────► Round 3 ──► Synthesis
```

- **Primary Analyst**: Proposes an initial macro thesis using RAG context
- **Devil's Advocate**: Critiques the thesis, finds flaws, challenges assumptions
- **Head of Strategy**: Synthesizes the debate into a final JSON output with conviction score

Early consensus (`[CONSENSUS REACHED]`) → High conviction (4-5).  
Full 3 rounds with disagreement → Low conviction (1-2).

---

## 📈 Backtesting Metrics

The backtesting engine (`scripts/run_backtest.py`) computes:

- **Total PnL** — Net profit/loss across all simulated trades
- **Win Rate** — Percentage of profitable trades
- **Sharpe Ratio** — Risk-adjusted return (annualized)
- **Max Drawdown** — Largest peak-to-trough loss as % of capital

Results are saved to `logs/backtest_results.json` and `logs/backtest_trades.csv`.

---

## 🔬 Ablation Studies

The evaluation script (`scripts/run_evaluation.py`) tests the marginal contribution of each agent by removing or modifying components:

| Scenario | Description | Purpose |
|----------|-------------|---------|
| Baseline | Full pipeline | Reference point |
| No Risk Gate | Remove Agent 4 | Measure risk filter's impact |
| Strict Risk | min_conviction = 4 | Test tighter filtering |

---

## 🛠️ Technology Stack

| Category | Tools |
|----------|-------|
| **LLM** | Google Gemini 2.5 Flash |
| **NLP** | FinBERT (sentiment), spaCy (NER) |
| **Data Validation** | Pydantic v2 |
| **Finance Data** | yfinance, FRED API |
| **News** | NewsAPI.org |
| **Report Export** | python-docx (Word), Markdown |
| **Config** | YAML + python-dotenv |

---

## 👥 Team

| Role | Responsibility |
|------|---------------|
| **Student A** | Data pipeline, Agent 1 (Event), Agent 2 (Macro Debate), Agent 6 (Report) |
| **Student B** | Agent 3 (Signal Generation) |
| **Student C** | Agent 4 (Risk Management), Agent 5 (Portfolio Construction) |

---

## 📝 License

This project is for academic purposes as part of **FIN580: Quantamental Investment**.

MIT License — see [LICENSE](LICENSE) for details.
