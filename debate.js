// ================================================================
// DEBATE TRANSCRIPTS PAGE — Logic
// ================================================================

const DEBATE_DATA = [
  {
    event_id: "EVT_9F7B9357",
    headline: "Sensex up over 100 points, crosses 78,000; Nifty50 opens above 24,350",
    expected_impact: "Neutral", conviction_score: 2,
    market_regime: "Volatile, Range-bound with Upside Sensitivity",
    macro_thesis: "The oil market is in a highly volatile and fragile equilibrium, where persistent demand headwinds are currently neutralizing strong underlying supply tightness and elevated geopolitical risks.",
    rounds: [
      {role:"primary",num:"Round 1",text:"Supply shock tightens physical markets. Inventories 4% below average, plus elevated Geopolitical Risk Index (Middle East tensions). Initial thesis: upward pressure on Brent from supply-side fragility combined with India's positive stock market sentiment."},
      {role:"advocate",num:"Round 1",text:"Demand-side forces are far stronger than acknowledged. China PMI 49.2 (contraction), Fed rates 5.25%-5.50%, DXY 104.5 — these aren't future threats, they're actively destroying demand right now. A 4% inventory deficit is insufficient to offset this."},
      {role:"primary",num:"Round 2",text:"Concession: demand headwinds are indeed active, not just forward-looking. However, the 4% deficit creates a launchpad — any supply disruption triggers disproportionate spikes. Chinese stimulus potential and Fed pivot expectations are forward catalysts."},
      {role:"advocate",num:"Round 2",text:"'Potential catalysts' are not current reality. VIX 22.5 reflects broad economic anxiety. If bullish risks can 'instantly override' bearish forces, how can you call it a 'bearish tendency'? This is incoherent."},
      {role:"primary",num:"Round 3",text:"Final concession: withdrawing 'near-term bearish tendency.' The market is a fragile equilibrium with upside skew from supply tightness. Demand headwinds are moderating factors, not dominant forces."},
      {role:"advocate",num:"Round 3",text:"Challenge accepted. But 'fragile equilibrium with upside skew' still overstates supply power. The market is stuck, waiting for a decisive push. Neither side dominates — hence low conviction."},
      {role:"judge",num:"Synthesis",text:"Consensus: The oil market is in a highly volatile and fragile equilibrium. Persistent demand headwinds neutralize supply tightness and geopolitical risks. Range-bound environment, critically sensitive to sharp bullish shocks. Conviction: 2/5."}
    ]
  },
  {
    event_id: "EVT_2F9EA5C2",
    headline: "Oil Prices Edge Higher as Iran Deal Doubts Resurface",
    expected_impact: "Bearish Brent", conviction_score: 4,
    market_regime: "Demand-driven contraction with episodic supply-side volatility",
    macro_thesis: "Global oil markets face an overwhelming structural challenge from accelerating demand destruction, driven by macroeconomic headwinds, which establishes a predominant bearish trend.",
    rounds: [
      {role:"primary",num:"Round 1",text:"Iran deal doubts remove potential future supply, creating bullish supply-side pressure. Combined with 4% below-average inventories and high Geopolitical Risk Index — supply fragility is the dominant immediate driver."},
      {role:"advocate",num:"Round 1",text:"You're overweighting a headline event against massive structural headwinds. China PMI 49.2 = current contraction in the world's largest importer. Fed 5.25%-5.50% actively strangling credit. DXY 104.5 makes oil expensive globally. These are not future concerns — they're destroying demand NOW."},
      {role:"primary",num:"Round 2",text:"Major concession: demand destruction forces are indeed active and compounding, not merely forward-looking. Supply tightness (4% deficit) provides a floor but cannot sustain rallies against structural demand weakness. Adjusted to: 'Near-term bearish with supply-driven volatility.'"},
      {role:"advocate",num:"Round 2",text:"'Floor' from inventories is dynamic, not static. If demand contracts faster than 4%, inventories normalize rapidly. The geopolitical premium erodes without escalation. A 'floor' built on shrinking demand is fragile."},
      {role:"primary",num:"Round 3",text:"Full concession. Demand destruction is the defining structural force. Supply tightness amplifies volatility but doesn't prevent a downward grind. Reframed: supply as 'volatility amplifier, not equalizer.'"},
      {role:"advocate",num:"Round 3",text:"Largely agree, but don't underestimate the 'bumps' — they could be violent counter-moves from geopolitical flare-ups in a tight market. Path down is treacherous, not smooth."},
      {role:"judge",num:"Synthesis",text:"Clear consensus: demand destruction dominates. Bearish structural trend established. Supply tightness creates sharp but temporary volatility. Conviction: 4/5 — strong agreement on direction."}
    ]
  },
  {
    event_id: "EVT_1AF6CC79",
    headline: "Oil prices rise about $1 as investors weigh Middle East peace prospects",
    expected_impact: "Neutral", conviction_score: 2,
    market_regime: "Volatile, Contested Range-Bound",
    macro_thesis: "The oil market is experiencing a precarious tug-of-war: strong macroeconomic headwinds actively destroy demand, while low inventories and high geopolitical risk prevent deeper collapse.",
    rounds: [
      {role:"primary",num:"Round 1",text:"$1 increase indicates supply-side factors and geopolitical risk premium are currently overriding demand headwinds. Tight inventories (4% below avg) + high geopolitical risk = immediate bullish momentum."},
      {role:"advocate",num:"Round 1",text:"A $1 rise is noise, not momentum. VIX 22.5, DXY 104.5, China PMI 49.2 — these are crushing demand. Inventories at 4% below average isn't 'critical,' and geopolitical risk is already priced in. You're over-interpreting a minor move."},
      {role:"primary",num:"Round 2",text:"Concession: $1 is not 'strong bullish momentum.' Reframed as 'downside rigidity' — the market refuses to fall further. Supply tightness provides a floor, not upward thrust. Geopolitical premium is a 'support beam, not an engine.'"},
      {role:"advocate",num:"Round 2",text:"'Downside rigidity' from a $1 move is generous. The market could simply be pausing before the next leg down. A 'floor' built on 4% below average inventories crumbles if demand accelerates its decline. These are speed bumps, not structural floors."},
      {role:"primary",num:"Round 3",text:"Further refinement: not claiming equilibrium between equal forces. Demand destruction is the stronger pull. But supply constraints create 'significant downside rigidity' preventing freefall. It's a controlled descent, not collapse."},
      {role:"advocate",num:"Round 3",text:"'Controlled descent' and 'precarious' are contradictory. If the floor is precarious, it can break. Still, acknowledge the supply side isn't zero. The market is stuck in a volatile, contested range with no clear winner."},
      {role:"judge",num:"Synthesis",text:"No clear consensus. Tug-of-war: demand headwinds vs. supply constraints. Range-bound with bearish underlying pressure but strong downside rigidity. Conviction: 2/5 — high uncertainty, low directional confidence."}
    ]
  },
  {
    event_id: "EVT_3D83EBB6",
    headline: "U.S. Stock Market: S&P 500, Nasdaq, Dow Jones eye five key factors",
    expected_impact: "Bearish Brent", conviction_score: 3,
    market_regime: "Volatile with Downside Bias",
    macro_thesis: "Brent Crude faces significant downside risk as persistent global economic headwinds accelerate demand destruction, rapidly eroding current inventory tightness.",
    rounds: [
      {role:"primary",num:"Round 1",text:"Brent faces downward pressure from macro headwinds — high Fed rates, weak China, strong dollar. But 4% inventory deficit and high geopolitical risk provide a counterbalance. Net: bearish demand offset by supply floor."},
      {role:"advocate",num:"Round 1",text:"'Substantial counterbalance' overstates supply's power. A 4% deficit isn't catastrophic. Geopolitical risk premium erodes if no new escalation. Demand headwinds are structural and compounding — they will eventually overwhelm the inventory buffer."},
      {role:"primary",num:"Round 2",text:"Concession: supply tightness is a 'floor,' not a counterbalance. It prevents collapse but can't sustain upside. Geopolitical premium is 'downside protection' that will erode. Demand destruction is the dominant force."},
      {role:"advocate",num:"Round 2",text:"If the 'floor' erodes (as you concede the premium will), and demand destruction accelerates (China PMI staying in contraction, rates staying high), then the 'range-bound' thesis breaks to the downside. This isn't equilibrium — it's a slow-motion decline."},
      {role:"primary",num:"Round 3",text:"Agreed. Demand destruction is the defining feature. 'Range-bound' holds only for the immediate term. Geopolitical premium is transient. The downside of any range is increasingly vulnerable to being broken."},
      {role:"advocate",num:"Round 3",text:"Good progress. But don't forget OPEC+ could cut supply to defend prices — a missing variable. And the 'pace' of demand destruction matters: if it's slow, the 4% deficit persists longer than you think."},
      {role:"judge",num:"Synthesis",text:"Moderate consensus: bearish bias from demand destruction. Inventory tightness provides near-term resilience but is being eroded. Downward grind expected. Conviction: 3/5."}
    ]
  },
  {
    event_id: "EVT_B79D89AA",
    headline: "CNBC Daily Open: Peace on the horizon (again?)",
    expected_impact: "Bearish Brent", conviction_score: 2,
    market_regime: "Volatile with underlying supply tightness",
    macro_thesis: "A perceived de-escalation will trigger a swift initial downward correction; however, critically tight inventories constrain the decline's depth and duration.",
    rounds: [
      {role:"primary",num:"Round 1",text:"Peace narrative → geopolitical risk premium erodes → bearish for Brent. Combined with high Fed rates, weak China PMI, strong DXY = overwhelming demand headwinds. Tight inventories (4% below avg) are the sole bullish support."},
      {role:"advocate",num:"Round 1",text:"Market is deeply cynical about 'peace on the horizon (again?).' Much of the geopolitical premium is already priced in as evergreen Middle East risk. The removable premium may be smaller than you think. And 4% below average has persisted DESPITE bearish headwinds — suggesting stronger underlying support than acknowledged."},
      {role:"primary",num:"Round 2",text:"Major concession: inventories persisting at 4% below average despite all headwinds is a powerful structural signal. This represents genuine tightness, not just a number. Adjusted: initial drop from de-escalation will be sharp but 'constrained and potentially short-lived' due to this robust physical floor."},
      {role:"advocate",num:"Round 2",text:"Contradiction: you say the floor is 'robust' but demand is 'fragile.' If demand is truly fragile with 'little bid to catch falling prices,' how robust is any floor? And VIX at 22.5 isn't necessarily an 'oil fear premium' — it's broader economic anxiety."},
      {role:"primary",num:"Round 3",text:"Final adjustment: the floor is 'dynamic' — robust in the near-term but increasingly vulnerable to prolonged macro headwinds. Initial correction swift, but depth constrained by physical tightness. Duration depends on whether peace narrative holds."},
      {role:"advocate",num:"Round 3",text:"Acceptable framing. But 'dynamic floor' essentially means uncertain. The market's cynicism about peace + tight physical supply = violent but short moves. Low conviction is appropriate."},
      {role:"judge",num:"Synthesis",text:"Partial consensus: de-escalation triggers downward correction, constrained by tight inventories. But market cynicism and physical tightness limit both depth and duration. Conviction: 2/5 — too many competing forces."}
    ]
  }
];

// ── CLOCK ────────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent = now.toLocaleString('en-US', {
    year:'numeric', month:'short', day:'2-digit',
    hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:false
  });
}
setInterval(updateClock, 1000); updateClock();

// ── RENDER EVENT SELECTOR ───────────────────────────────────────
function renderSelector() {
  const el = document.getElementById('event-selector');
  el.innerHTML = DEBATE_DATA.map((d, i) => {
    const ic = d.expected_impact.includes('Bullish') ? 'bullish' : d.expected_impact.includes('Bearish') ? 'bearish' : 'neutral';
    return `<button class="evt-btn ${i===0?'active':''}" onclick="selectEvent(${i})">
      <span class="evt-btn-id">${d.event_id}</span>
      <span class="evt-btn-title">${d.headline}</span>
      <span class="evt-btn-impact ${ic}">${d.expected_impact} | Conv: ${d.conviction_score}/5</span>
    </button>`;
  }).join('');
}

// ── RENDER DEBATE ───────────────────────────────────────────────
function selectEvent(idx) {
  document.querySelectorAll('.evt-btn').forEach((b,i) => b.classList.toggle('active', i===idx));
  const d = DEBATE_DATA[idx];
  const panel = document.getElementById('debate-panel');

  const convBars = Array.from({length:5}, (_,i) =>
    `<span style="display:inline-block;width:8px;height:16px;border-radius:3px;margin-right:2px;background:${i<d.conviction_score?'var(--amber)':'rgba(255,255,255,.08)'}"></span>`
  ).join('');

  const roundsHTML = d.rounds.map(r => `
    <div class="debate-round ${r.role}">
      <div class="round-header">
        <span class="round-role ${r.role}">${r.role==='primary'?'Primary Analyst':r.role==='advocate'?"Devil's Advocate":'Head of Strategy'}</span>
        <span class="round-num">${r.num}</span>
      </div>
      <div class="round-text">${r.text}</div>
    </div>
  `).join('');

  panel.innerHTML = `
    <div class="debate-meta">
      <div class="meta-chip"><b>Event:</b> ${d.headline}</div>
      <div class="meta-chip"><b>Regime:</b> ${d.market_regime}</div>
      <div class="meta-chip"><b>Conviction:</b> ${convBars} ${d.conviction_score}/5</div>
    </div>
    <div class="debate-transcript">${roundsHTML}</div>
    <div class="thesis-box">
      <div class="thesis-label">Final Macro Thesis</div>
      <div class="thesis-text">${d.macro_thesis}</div>
    </div>
  `;
}

// ── INIT ────────────────────────────────────────────────────────
renderSelector();
selectEvent(0);
