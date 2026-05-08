import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Brent Crude Command Center",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium feel
st.markdown("""
<style>
    .kpi-box {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid #334155;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #F8FAFC;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .status-active {
        color: #10B981;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ───────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    def load_json(filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    events = load_json("data/processed/a1_events.json")
    macros = load_json("data/processed/a2_macro.json")
    signals = load_json("data/processed/a3_signals.json")
    risks = load_json("data/processed/a4_risk_decisions.json")
    trades = load_json("data/processed/a5_portfolio_trades.json")
    
    return events, macros, signals, risks, trades

events, macros, signals, risks, trades = load_data()

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
st.sidebar.title("🛢️ Brent Command Center")
st.sidebar.markdown(f"**Status:** <span class='status-active'>● PIPELINE ACTIVE</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", ["Dashboard", "Macro Debate", "Analysis Report"])

st.sidebar.markdown("---")
st.sidebar.info("FIN580 Quantamental Investment\nMulti-Agent Trading System")

# ─── HELPER FUNCTIONS ───────────────────────────────────────────────────────
def render_kpis():
    st.markdown("### System Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    num_events = len(events)
    num_signals = len(signals)
    num_approved = sum(1 for r in risks if r.get('approved', False))
    approval_rate = (num_approved / num_events * 100) if num_events > 0 else 0
    capital_deployed = sum(t.get('size_usd', 0) for t in trades)
    
    with col1:
        st.markdown(f"<div class='kpi-box'><div class='kpi-label'>Events Detected</div><div class='kpi-value' style='color:#3b82f6'>{num_events}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-box'><div class='kpi-label'>Signals Generated</div><div class='kpi-value' style='color:#8b5cf6'>{num_signals}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-box'><div class='kpi-label'>Approval Rate</div><div class='kpi-value' style='color:#10b981'>{approval_rate:.0f}%</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='kpi-box'><div class='kpi-label'>Capital Deployed</div><div class='kpi-value' style='color:#f59e0b'>${capital_deployed:,.0f}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ─── PAGE: DASHBOARD ────────────────────────────────────────────────────────
if page == "Dashboard":
    render_kpis()
    
    col_left, col_right = st.columns([1, 1])
    
    # Left Column: Events & Signals
    with col_left:
        st.markdown("### 📰 Latest Events")
        if events:
            df_events = pd.DataFrame(events)
            st.dataframe(df_events[['headline', 'directional_bias', 'confidence_score', 'source']], use_container_width=True, hide_index=True)
        else:
            st.info("No events loaded.")
            
        st.markdown("### 📊 Signal Breakdown")
        if signals:
            df_signals = pd.DataFrame(signals)
            sig_counts = df_signals['direction'].value_counts().reset_index()
            sig_counts.columns = ['Direction', 'Count']
            color_map = {'SHORT': '#ef4444', 'LONG': '#10b981', 'FLAT': '#64748b'}
            fig_sig = px.pie(sig_counts, values='Count', names='Direction', hole=0.7, color='Direction', color_discrete_map=color_map)
            fig_sig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=False)
            
            scol1, scol2 = st.columns([1, 1])
            with scol1:
                st.plotly_chart(fig_sig, use_container_width=True)
            with scol2:
                for idx, row in sig_counts.iterrows():
                    st.markdown(f"**{row['Direction']}**: {row['Count']} signals")
                avg_conv = df_signals['conviction'].mean()
                st.markdown(f"**Avg Conviction**: {avg_conv:.1f} / 5")
                avg_str = df_signals['signal_strength'].mean() * 100
                st.markdown(f"**Avg Strength**: {avg_str:.0f}%")
        else:
            st.info("No signals generated.")

    # Right Column: Risk & Portfolio
    with col_right:
        st.markdown("### 🛡️ Risk Gate Decisions")
        if risks:
            df_risks = pd.DataFrame(risks)
            df_risks['Status'] = df_risks['approved'].apply(lambda x: 'Approved' if x else 'Vetoed')
            risk_counts = df_risks['Status'].value_counts().reset_index()
            risk_counts.columns = ['Status', 'Count']
            fig_risk = px.bar(risk_counts, x='Count', y='Status', orientation='h', color='Status', 
                              color_discrete_map={'Approved': '#10b981', 'Vetoed': '#ef4444'})
            fig_risk.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, showlegend=False)
            st.plotly_chart(fig_risk, use_container_width=True)
            st.dataframe(df_risks[['direction', 'conviction', 'Status', 'veto_reason']], use_container_width=True, hide_index=True)
        else:
            st.info("No risk decisions available.")
            
        st.markdown("### 💼 Portfolio Allocation (Roth IRA)")
        deployed = sum(t.get('size_usd', 0) for t in trades)
        core_holdings = 800000
        tactical_cash = 200000 - deployed
        
        alloc_data = pd.DataFrame({
            'Category': ['Core Holdings (80%)', 'Deployed Trades', 'Tactical Cash'],
            'Amount': [core_holdings, deployed, tactical_cash]
        })
        fig_alloc = px.pie(alloc_data, values='Amount', names='Category', hole=0.7,
                           color='Category', color_discrete_map={
                               'Core Holdings (80%)': '#8b5cf6',
                               'Deployed Trades': '#3b82f6',
                               'Tactical Cash': '#334155'
                           })
        fig_alloc.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_alloc, use_container_width=True)

# ─── PAGE: MACRO DEBATE ─────────────────────────────────────────────────────
elif page == "Macro Debate":
    st.markdown("## Agent 2: Macro Debate Transcripts")
    st.markdown("3-round adversarial debate between Primary Analyst, Devil's Advocate, and Head of Strategy")
    
    if not macros:
        st.warning("No macro debate data available.")
    else:
        event_titles = [f"{m.get('event_id', 'Unknown')}: {m.get('market_regime', 'Regime')}" for m in macros]
        selected_event = st.selectbox("Select Event", options=range(len(macros)), format_func=lambda x: event_titles[x])
        
        m = macros[selected_event]
        st.markdown(f"**Final Thesis:** {m.get('macro_thesis')}")
        st.markdown(f"**Expected Impact:** `{m.get('expected_impact')}` | **Conviction:** `{m.get('conviction_score')}/5`")
        
        # Display rounds if available (we used mock data in HTML, let's see if the JSON actually has it)
        # If the JSON doesn't have transcript rounds, we will just show the thesis
        if 'transcript' in m or 'rounds' in m:
            st.markdown("### Debate Transcript")
            rounds = m.get('rounds', m.get('transcript', []))
            for r in rounds:
                role = r.get('role', 'Unknown').upper()
                text = r.get('text', '')
                st.info(f"**{role}**: {text}")
        else:
            st.info("Full transcript not available in the JSON output. (Only final thesis was saved).")

# ─── PAGE: ANALYSIS REPORT ──────────────────────────────────────────────────
elif page == "Analysis Report":
    st.markdown("## Brent Crude Oil — Analysis Report")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Events Analyzed", len(events))
    col2.metric("Signals Approved", sum(1 for r in risks if r.get('approved', False)))
    col3.metric("Capital Deployed", f"${sum(t.get('size_usd', 0) for t in trades):,.0f}")
    
    st.markdown("### Overall Market Verdict")
    st.warning("**Bearish with high volatility.** The multi-agent system identified a market dominated by demand destruction. Tight physical inventories prevent a freefall but cannot sustain rallies. The system recommends SHORT positions with reduced sizing due to elevated VIX.")
    
    st.markdown("### Portfolio Structure — Roth IRA (80/20)")
    st.info("80% of the $1M portfolio ($800,000) is locked in core buy-and-hold equity positions (FXAIX, FZROX, BRK-B, etc.). Only the remaining 20% tactical pool ($200,000) is available for Brent Crude trades, subject to a strict 15% minimum cash buffer.")
    
    st.markdown("### Executed Trades")
    if trades:
        df_trades = pd.DataFrame(trades)
        st.table(df_trades[['date', 'asset', 'direction', 'size_usd', 'reasoning_trace']])
    else:
        st.write("No trades executed.")
        
    st.markdown("---")
    st.caption("This report is generated by an AI-driven multi-agent system for academic purposes (FIN580 Quantamental Investment). It does not constitute financial advice.")

