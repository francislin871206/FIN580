// ================================================================
// BRENT CRUDE COMMAND CENTER — Dashboard Logic
// ================================================================

// ── EMBEDDED DATA (from pipeline outputs) ───────────────────────
const EVENTS = [
  {event_id:"EVT_9F7B9357",headline:"Stock Market Live Updates: Sensex up over 100 points, crosses 78,000 mark; Nifty50 opens above 24,350",event_type:"Macroeconomic Indicator",category:"Macroeconomics",directional_bias:"Bullish Brent",confidence_score:0.7,source:"The Times of India",sentiment_score:0.918,timestamp:"2026-05-07T02:18:45Z"},
  {event_id:"EVT_2F9EA5C2",headline:"Oil Prices Edge Higher as Iran Deal Doubts Resurface",event_type:"Geopolitical Tension",category:"Energy Policy",directional_bias:"Bullish Brent",confidence_score:0.95,source:"OilPrice.com",sentiment_score:0.580,timestamp:"2026-05-07T02:07:40Z"},
  {event_id:"EVT_1AF6CC79",headline:"Oil prices rise about $1 as investors weigh Middle East peace prospects",event_type:"Geopolitical Stability",category:"Geopolitics",directional_bias:"Bullish Brent",confidence_score:0.9,source:"The Times of India",sentiment_score:0.455,timestamp:"2026-05-07T01:49:19Z"},
  {event_id:"EVT_3D83EBB6",headline:"U.S. Stock Market on Thursday: S&P 500, Nasdaq, Dow Jones, Russell 2000 investors eye five factors",event_type:"Market Outlook/Sentiment",category:"Macroeconomics",directional_bias:"Neutral",confidence_score:0.85,source:"The Times of India",sentiment_score:0.0,timestamp:"2026-05-07T01:33:15Z"},
  {event_id:"EVT_B79D89AA",headline:"CNBC Daily Open: Peace on the horizon (again?)",event_type:"Geopolitical Tension",category:"Geopolitics",directional_bias:"Neutral",confidence_score:0.65,source:"CNBC",sentiment_score:0.0,timestamp:"2026-05-07T01:03:55Z"}
];

const MACROS = [
  {event_id:"EVT_9F7B9357",macro_thesis:"The oil market is in a highly volatile and fragile equilibrium, where persistent demand headwinds are currently neutralizing strong underlying supply tightness and elevated geopolitical risks.",market_regime:"Volatile, Range-bound with Upside Sensitivity",expected_impact:"Neutral",conviction_score:2},
  {event_id:"EVT_2F9EA5C2",macro_thesis:"Global oil markets face an overwhelming structural challenge from accelerating demand destruction, which establishes a predominant bearish trend. However, tight inventories amplify any supply disruptions.",market_regime:"Demand-driven contraction with episodic supply-side volatility",expected_impact:"Bearish Brent",conviction_score:4},
  {event_id:"EVT_1AF6CC79",macro_thesis:"The oil market is experiencing a precarious tug-of-war: strong macroeconomic headwinds actively destroy demand, while low inventories and high geopolitical risk prevent deeper collapse.",market_regime:"Volatile, Contested Range-Bound",expected_impact:"Neutral",conviction_score:2},
  {event_id:"EVT_3D83EBB6",macro_thesis:"Brent Crude faces significant downside risk as persistent global economic headwinds accelerate demand destruction, rapidly eroding current inventory tightness.",market_regime:"Volatile with Downside Bias",expected_impact:"Bearish Brent",conviction_score:3},
  {event_id:"EVT_B79D89AA",macro_thesis:"A perceived de-escalation of geopolitical tensions will likely trigger a swift downward correction; however, critically tight physical inventories constrain the decline.",market_regime:"Volatile with underlying supply tightness",expected_impact:"Bearish Brent",conviction_score:2}
];

const SIGNALS = [
  {event_id:"EVT_9F7B9357",direction:"FLAT",conviction:2,signal_strength:0.30},
  {event_id:"EVT_2F9EA5C2",direction:"SHORT",conviction:4,signal_strength:0.72},
  {event_id:"EVT_1AF6CC79",direction:"FLAT",conviction:2,signal_strength:0.30},
  {event_id:"EVT_3D83EBB6",direction:"SHORT",conviction:3,signal_strength:0.72},
  {event_id:"EVT_B79D89AA",direction:"SHORT",conviction:2,signal_strength:0.72}
];

const RISKS = [
  {event_id:"EVT_9F7B9357",direction:"FLAT",conviction:2,approved:false,veto_reason:"VETO: Conviction 2 < 3",risk_multiplier:0.0},
  {event_id:"EVT_2F9EA5C2",direction:"SHORT",conviction:4,approved:true,veto_reason:"APPROVED. VIX 22.0 -> 0.5x",risk_multiplier:0.5},
  {event_id:"EVT_1AF6CC79",direction:"FLAT",conviction:2,approved:false,veto_reason:"VETO: Conviction 2 < 3",risk_multiplier:0.0},
  {event_id:"EVT_3D83EBB6",direction:"SHORT",conviction:3,approved:true,veto_reason:"APPROVED. VIX 22.0 -> 0.5x",risk_multiplier:0.5},
  {event_id:"EVT_B79D89AA",direction:"SHORT",conviction:2,approved:false,veto_reason:"VETO: Conviction 2 < 3",risk_multiplier:0.0}
];

const TRADES = [
  {date:"2026-05-08",asset:"Brent Crude Oil",direction:"SHORT",size_usd:40000,entry_price_ref:80.0,reasoning_trace:"A4 Risk Mult: 0.5x. A5 Sizing: 4.0% = $40,000. Cash remaining: $110,000 (Core: $800,000)."},
  {date:"2026-05-08",asset:"Brent Crude Oil",direction:"SHORT",size_usd:30000,entry_price_ref:80.0,reasoning_trace:"A4 Risk Mult: 0.5x. A5 Sizing: 3.0% = $30,000. Cash remaining: $80,000 (Core: $800,000)."}
];

const BACKTEST = {
  summary:{total_signals:20,signals_approved:5,signals_vetoed:15,total_pnl:4813.13,win_rate:0.6,sharpe_ratio:8.9885,max_drawdown_pct:0.1591},
  trades:[
    {date:"2022-03-11",direction:"SHORT",pnl:1803.83,cumulative_pnl:1803.83},
    {date:"2022-05-19",direction:"SHORT",pnl:1575.84,cumulative_pnl:3379.66},
    {date:"2022-06-13",direction:"LONG",pnl:3024.78,cumulative_pnl:6404.44},
    {date:"2022-09-17",direction:"LONG",pnl:-651.20,cumulative_pnl:5753.24},
    {date:"2023-01-16",direction:"SHORT",pnl:-940.12,cumulative_pnl:4813.12}
  ]
};

const ABLATION = {
  baseline:{capital_deployed:250000,approved:5,vetoed:0,trades:5},
  no_risk:{capital_deployed:500000,approved:5,vetoed:0,trades:5},
  strict:{capital_deployed:250000,approved:5,vetoed:0,trades:5}
};

// ── ROTH IRA CORE HOLDINGS ──────────────────────────────────────
const PORTFOLIO_STRUCTURE = {
  total: 1000000, core_pct: 0.80, tactical_pct: 0.20, cash_buffer_pct: 0.15,
  core_value: 800000, tactical_pool: 200000, min_cash_buffer: 150000
};
const CORE_HOLDINGS = [
  {ticker:'FXAIX',name:'Fidelity 500 Index',type:'Index Fund'},
  {ticker:'FZROX',name:'Fidelity Total Market',type:'Index Fund'},
  {ticker:'BRK-B',name:'Berkshire Hathaway',type:'Equity'},
  {ticker:'GOOG',name:'Alphabet',type:'Equity'},
  {ticker:'VRT',name:'Vertiv Holdings',type:'Equity'},
  {ticker:'GBX',name:'Greenbrier Companies',type:'Equity'},
  {ticker:'MAIN',name:'Main Street Capital',type:'BDC / Dividend'},
  {ticker:'WSM',name:'Williams-Sonoma',type:'Equity'},
  {ticker:'BF-A',name:'Brown-Forman',type:'Equity'}
];

// ── CHART DEFAULTS ──────────────────────────────────────────────
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';
Chart.defaults.font.family = "'Inter', sans-serif";

// ── CLOCK ───────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent = now.toLocaleString('en-US', {
    year:'numeric', month:'short', day:'2-digit',
    hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:false
  });
}
setInterval(updateClock, 1000);
updateClock();

// ── EVENT FEED ──────────────────────────────────────────────────
function renderEvents() {
  const el = document.getElementById('event-list');
  el.innerHTML = EVENTS.map(e => {
    const sentClass = e.sentiment_score > 0.3 ? 'positive' : e.sentiment_score < -0.1 ? 'negative' : 'neutral';
    const biasClass = e.directional_bias.includes('Bullish') ? 'bullish' : e.directional_bias.includes('Bearish') ? 'bearish' : 'neutral';
    const time = new Date(e.timestamp).toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit'});
    return `<div class="event-item">
      <div class="evt-sentiment ${sentClass}">${e.sentiment_score >= 0 ? '+' : ''}${e.sentiment_score.toFixed(2)}</div>
      <div>
        <div class="evt-headline">${e.headline}</div>
        <div class="evt-meta">${e.source} &bull; ${time} &bull; ${e.event_type} &bull; Conf: ${(e.confidence_score*100).toFixed(0)}%</div>
      </div>
      <div class="evt-badge ${biasClass}">${e.directional_bias}</div>
    </div>`;
  }).join('');
}

// ── SIGNAL CHART ────────────────────────────────────────────────
function renderSignals() {
  const long = SIGNALS.filter(s=>s.direction==='LONG').length;
  const short = SIGNALS.filter(s=>s.direction==='SHORT').length;
  const flat = SIGNALS.filter(s=>s.direction==='FLAT').length;

  new Chart(document.getElementById('signalChart'), {
    type: 'doughnut',
    data: {
      labels: ['LONG','SHORT','FLAT'],
      datasets: [{
        data: [long, short, flat],
        backgroundColor: ['#10b981','#ef4444','#64748b'],
        borderWidth: 0, borderRadius: 4
      }]
    },
    options: {
      cutout: '70%', responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { backgroundColor: '#1e293b', titleColor: '#e2e8f0', bodyColor: '#e2e8f0', cornerRadius: 8 }
      }
    }
  });

  const stats = document.getElementById('signal-stats');
  stats.innerHTML = [
    {label:'LONG',count:long,color:'#10b981'},
    {label:'SHORT',count:short,color:'#ef4444'},
    {label:'FLAT',count:flat,color:'#64748b'}
  ].map(s => `<div class="sig-row">
    <div class="sig-dot" style="background:${s.color}"></div>
    <div class="sig-label">${s.label}</div>
    <div class="sig-count">${s.count}</div>
  </div>`).join('') + `<div class="sig-row" style="margin-top:8px;border-top:1px solid rgba(255,255,255,.06);padding-top:12px">
    <div class="sig-label" style="color:var(--text3);font-size:.7rem">Avg Conviction</div>
    <div class="sig-count">${(SIGNALS.reduce((a,s)=>a+s.conviction,0)/SIGNALS.length).toFixed(1)}/5</div>
  </div>
  <div class="sig-row">
    <div class="sig-label" style="color:var(--text3);font-size:.7rem">Avg Strength</div>
    <div class="sig-count">${(SIGNALS.reduce((a,s)=>a+s.signal_strength,0)/SIGNALS.length*100).toFixed(0)}%</div>
  </div>`;
}

// ── MACRO THESES ────────────────────────────────────────────────
function renderMacros() {
  const el = document.getElementById('macro-list');
  el.innerHTML = MACROS.map(m => {
    const impClass = m.expected_impact.includes('Bullish') ? 'bullish' : m.expected_impact.includes('Bearish') ? 'bearish' : 'neutral';
    const bars = Array.from({length:5}, (_,i) => `<div class="conv-bar ${i < m.conviction_score ? 'filled' : ''}"></div>`).join('');
    return `<div class="macro-item">
      <div class="macro-header">
        <div class="macro-regime">${m.market_regime}</div>
        <div class="macro-conviction">${bars}</div>
      </div>
      <div class="macro-thesis">${m.macro_thesis}</div>
      <span class="macro-impact ${impClass}">${m.expected_impact}</span>
    </div>`;
  }).join('');
}

// ── RISK GATING ─────────────────────────────────────────────────
function renderRisk() {
  const approved = RISKS.filter(r=>r.approved).length;
  const vetoed = RISKS.filter(r=>!r.approved).length;

  new Chart(document.getElementById('riskChart'), {
    type: 'bar',
    data: {
      labels: ['Approved','Vetoed'],
      datasets: [{
        data: [approved, vetoed],
        backgroundColor: ['rgba(16,185,129,.6)','rgba(239,68,68,.6)'],
        borderRadius: 6, borderSkipped: false
      }]
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { stepSize: 1 } },
        y: { grid: { display: false } }
      }
    }
  });

  const el = document.getElementById('risk-table');
  el.innerHTML = RISKS.map(r => `<div class="risk-row">
    <span style="font-family:var(--mono);font-size:.7rem;color:var(--text3)">${r.event_id.slice(-8)}</span>
    <span class="${r.direction==='SHORT'?'dir-short':r.direction==='LONG'?'dir-long':''}">${r.direction}</span>
    <span>${r.conviction}/5</span>
    <span class="risk-status ${r.approved?'approved':'vetoed'}">${r.approved?'APPROVED':'VETOED'}</span>
  </div>`).join('');
}

// ── PORTFOLIO ───────────────────────────────────────────────────
function renderPortfolio() {
  const deployed = TRADES.reduce((a,t)=>a+t.size_usd, 0);
  const PS = PORTFOLIO_STRUCTURE;
  const cashLeft = PS.tactical_pool - deployed;

  // Capital allocation donut: Core / Deployed / Cash
  new Chart(document.getElementById('capitalChart'), {
    type: 'doughnut',
    data: {
      labels: ['Core Holdings (80%)','Deployed Trades','Tactical Cash'],
      datasets: [{
        data: [PS.core_value, deployed, cashLeft],
        backgroundColor: ['rgba(139,92,246,.5)','rgba(59,130,246,.7)','rgba(255,255,255,.08)'],
        borderWidth: 0, borderRadius: 4
      }]
    },
    options: {
      cutout: '70%', responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: ctx => `${ctx.label}: $${ctx.parsed.toLocaleString()}` },
          backgroundColor: '#1e293b', cornerRadius: 8
        }
      }
    }
  });

  // Trades table
  const tbody = document.querySelector('#portfolio-table tbody');
  tbody.innerHTML = TRADES.map(t => `<tr>
    <td>${t.date}</td>
    <td>${t.asset}</td>
    <td class="${t.direction==='SHORT'?'dir-short':'dir-long'}">${t.direction}</td>
    <td style="font-family:var(--mono)">$${t.size_usd.toLocaleString()}</td>
    <td style="font-family:var(--mono)">$${t.entry_price_ref.toFixed(2)}</td>
    <td style="color:var(--text3);font-size:.72rem">${t.reasoning_trace}</td>
  </tr>`).join('');

  // Core holdings table
  const holdingsEl = document.getElementById('core-holdings');
  if (holdingsEl) {
    holdingsEl.innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:8px">
        ${CORE_HOLDINGS.map(h => `<div style="padding:8px 10px;border-radius:8px;background:rgba(255,255,255,.02);font-size:.75rem">
          <span style="font-family:var(--mono);color:var(--purple);font-weight:600">${h.ticker}</span>
          <span style="color:var(--text3);margin-left:6px">${h.name}</span>
        </div>`).join('')}
      </div>
      <div style="display:flex;gap:12px;margin-top:12px;flex-wrap:wrap">
        <div style="padding:8px 14px;border-radius:8px;background:rgba(139,92,246,.08);font-size:.72rem">
          <span style="color:var(--text3)">Core (80%)</span>
          <span style="font-family:var(--mono);font-weight:600;margin-left:8px;color:var(--purple)">$${PS.core_value.toLocaleString()}</span>
        </div>
        <div style="padding:8px 14px;border-radius:8px;background:rgba(59,130,246,.08);font-size:.72rem">
          <span style="color:var(--text3)">Deployed</span>
          <span style="font-family:var(--mono);font-weight:600;margin-left:8px;color:var(--blue)">$${deployed.toLocaleString()}</span>
        </div>
        <div style="padding:8px 14px;border-radius:8px;background:rgba(255,255,255,.04);font-size:.72rem">
          <span style="color:var(--text3)">Tactical Cash</span>
          <span style="font-family:var(--mono);font-weight:600;margin-left:8px">$${cashLeft.toLocaleString()}</span>
        </div>
        <div style="padding:8px 14px;border-radius:8px;background:rgba(245,158,11,.08);font-size:.72rem">
          <span style="color:var(--text3)">Min Buffer (15%)</span>
          <span style="font-family:var(--mono);font-weight:600;margin-left:8px;color:var(--amber)">$${PS.min_cash_buffer.toLocaleString()}</span>
        </div>
      </div>`;
  }
}

// ── BACKTEST PNL ────────────────────────────────────────────────
function renderBacktest() {
  const trades = BACKTEST.trades;
  new Chart(document.getElementById('pnlChart'), {
    type: 'line',
    data: {
      labels: trades.map(t=>t.date),
      datasets: [{
        label: 'Cumulative PnL',
        data: [0, ...trades.map(t=>t.cumulative_pnl)],
        borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,.08)',
        fill: true, tension: .3, pointRadius: 5, pointBackgroundColor: '#3b82f6',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: ctx => `$${ctx.parsed.y.toLocaleString()}` },
          backgroundColor: '#1e293b', cornerRadius: 8
        }
      },
      scales: {
        x: { grid: { display: false }, labels: ['Start', ...trades.map(t=>t.date)] },
        y: { grid: { color: 'rgba(255,255,255,.03)' },
          ticks: { callback: v => `$${v.toLocaleString()}` }
        }
      }
    }
  });

  const s = BACKTEST.summary;
  const metrics = [
    {label:'Total Signals',value:s.total_signals},
    {label:'Approved',value:s.signals_approved},
    {label:'Vetoed',value:s.signals_vetoed},
    {label:'Total PnL',value:`$${s.total_pnl.toLocaleString()}`,cls: s.total_pnl>=0?'pnl-positive':'pnl-negative'},
    {label:'Win Rate',value:`${(s.win_rate*100).toFixed(0)}%`},
    {label:'Sharpe Ratio',value:s.sharpe_ratio.toFixed(2)},
    {label:'Max Drawdown',value:`${s.max_drawdown_pct.toFixed(2)}%`}
  ];
  document.getElementById('bt-metrics').innerHTML = metrics.map(m =>
    `<div class="bt-metric"><span class="bt-metric-label">${m.label}</span><span class="bt-metric-value ${m.cls||''}">${m.value}</span></div>`
  ).join('');
}

// ── ABLATION CHART ──────────────────────────────────────────────
function renderAblation() {
  new Chart(document.getElementById('ablationChart'), {
    type: 'bar',
    data: {
      labels: ['Baseline', 'No Risk Gate', 'Strict Risk'],
      datasets: [
        {
          label: 'Capital Deployed ($)',
          data: [ABLATION.baseline.capital_deployed, ABLATION.no_risk.capital_deployed, ABLATION.strict.capital_deployed],
          backgroundColor: ['rgba(59,130,246,.6)','rgba(239,68,68,.6)','rgba(245,158,11,.6)'],
          borderRadius: 8, borderSkipped: false
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: ctx => `$${ctx.parsed.y.toLocaleString()}` },
          backgroundColor: '#1e293b', cornerRadius: 8
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(255,255,255,.03)' },
          ticks: { callback: v => `$${(v/1000).toFixed(0)}k` }
        }
      }
    }
  });
}

// ── INIT ────────────────────────────────────────────────────────
renderEvents();
renderSignals();
renderMacros();
renderRisk();
renderPortfolio();
renderBacktest();
renderAblation();
