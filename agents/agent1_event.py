"""
==============================================================================
  AGENT 1 -- EVENT DETECTION & CLASSIFICATION (Student A)
  FIN580 Quantamental Investment Project -- Brent Crude Oil
==============================================================================
  Processes raw news articles and outputs structured event objects.
  Pipeline: News -> FinBERT -> spaCy -> Gemini -> EventOutput JSON
  Usage: python -m agents.agent1_event
  Output: data/processed/a1_events.json  ->  consumed by Agent 2
==============================================================================
"""

import os, uuid, json, time
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Optional
from agents import load_config, load_prompt, resolve_path

_CFG = load_config()
_PIPELINE  = _CFG.get("pipeline", {})
_AGENT_CFG = _CFG.get("agent1", {})
_GEMINI    = _CFG.get("gemini", {})

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
NEWSAPI_KEY    = os.environ.get("NEWSAPI_KEY", "")
GEMINI_MODEL   = _GEMINI.get("model", "gemini-2.5-flash")
FINBERT_MODEL  = _AGENT_CFG.get("finbert_model", "ProsusAI/finbert")
SPACY_MODEL    = _AGENT_CFG.get("spacy_model", "en_core_web_sm")
MOCK_MODE      = _PIPELINE.get("mock_mode", True)
RATE_LIMIT_SEC = _PIPELINE.get("rate_limit_sec", 2)
MAX_ARTICLES   = _AGENT_CFG.get("max_articles", 5)

class EventOutput(BaseModel):
    event_id: str; timestamp: str; headline: str; event_type: str
    category: str; entities: List[str]; directional_bias: str
    confidence_score: float; source: str
    sentiment_score: Optional[float] = None
    raw_text: Optional[str] = None
    processing_timestamp: Optional[str] = None

class MockNewsScraper:
    def __init__(self, data_path=None):
        if data_path is None:
            data_path = str(resolve_path(_CFG.get("paths",{}).get("sample_news","data/sample/mock_news.json")))
        self.data_path = data_path

    def fetch_news(self) -> list:
        try:
            if not os.path.exists(self.data_path):
                print(f"[Agent 1] Mock file not found. Using internal fallback.")
                return [
                    {"headline":"OPEC+ agrees to extend voluntary oil output cuts of 2.2 million bpd.","source":"Internal Mock","timestamp":"2024-05-01T10:00:00Z"},
                    {"headline":"US crude inventories fell by 1.4 million barrels last week.","source":"Internal Mock","timestamp":"2024-05-02T15:30:00Z"},
                    {"headline":"Middle East tensions raise supply disruption fears for Brent Crude.","source":"Internal Mock","timestamp":"2024-05-03T09:15:00Z"},
                ]
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            out = []
            for item in raw:
                if "headline" in item:
                    out.append(item)
                else:
                    out.append({"headline":item.get("macro_thesis","Unknown")+" relating to "+", ".join(item.get("entities",[])),"source":"Mock DB","timestamp":item.get("timestamp","2024-01-01T00:00:00Z")})
            print(f"[Agent 1] Loaded {len(out)} articles from {self.data_path}")
            return out
        except Exception as e:
            print(f"[Agent 1] Error loading mock data: {e}"); return []

class NewsAPIScraper:
    def __init__(self, api_key): self.api_key = api_key
    def fetch_news(self, query=None) -> list:
        import requests
        if query is None: query = _AGENT_CFG.get("news_query","Brent Crude Oil OR 'Oil Prices'")
        print(f"[Agent 1] Fetching live news for: {query}...")
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&apiKey={self.api_key}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200: print(f"[Agent 1] NewsAPI Error: {r.status_code}"); return []
            arts = r.json().get("articles",[])
            return [{"headline":a.get("title",""),"source":a.get("source",{}).get("name","NewsAPI"),"timestamp":a.get("publishedAt",datetime.now(timezone.utc).isoformat())} for a in arts[:MAX_ARTICLES]]
        except Exception as e: print(f"[Agent 1] NewsAPI Exception: {e}"); return []

class AdvancedEventAgent:
    """Agent 1: FinBERT sentiment + spaCy NER + Gemini classification."""
    def __init__(self):
        self.mock_mode = MOCK_MODE
        print("[Agent 1] Initializing Event Detection Agent...")
        if not self.mock_mode:
            from google import genai; from google.genai import types
            self.genai, self.types = genai, types
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            from transformers import pipeline as hf_pipeline
            self.sentiment_analyzer = hf_pipeline("sentiment-analysis", model=FINBERT_MODEL)
            import spacy
            try: self.nlp = spacy.load(SPACY_MODEL)
            except OSError: print(f"  [WARN] {SPACY_MODEL} not found."); self.nlp = None
        else: self.nlp = None

    def _get_finbert_sentiment(self, text):
        if self.mock_mode: return 0.5
        r = self.sentiment_analyzer(text)[0]
        if r["label"]=="positive": return r["score"]
        elif r["label"]=="negative": return -r["score"]
        return 0.0

    def _get_spacy_entities(self, text):
        if self.mock_mode or not self.nlp: return ["OPEC"]
        doc = self.nlp(text); seen, ents = set(), []
        for e in doc.ents:
            if e.label_ in ("ORG","GPE") and e.text not in seen: ents.append(e.text); seen.add(e.text)
        return ents

    def process_news(self, news_text, timestamp, source="Unknown") -> EventOutput:
        eid = f"EVT_{uuid.uuid4().hex[:8].upper()}"
        pt = datetime.now(timezone.utc).isoformat()
        sent = self._get_finbert_sentiment(news_text)
        ents = self._get_spacy_entities(news_text)
        if self.mock_mode:
            return EventOutput(event_id=eid,timestamp=timestamp,headline=news_text,event_type="Supply Shock",category="Energy Policy",entities=ents,directional_bias="Bullish Brent",confidence_score=0.91,source=source,sentiment_score=sent,raw_text=news_text,processing_timestamp=pt)
        ents_str = ", ".join(ents) if ents else "None detected"
        sys_prompt = load_prompt("event_classification.txt",SENTIMENT_SCORE=f"{sent:.2f}",ENTITIES=ents_str)
        try:
            resp = self.client.models.generate_content(model=GEMINI_MODEL,contents=f"News Headline: {news_text}",config=self.types.GenerateContentConfig(system_instruction=sys_prompt,response_mime_type="application/json"))
            d = json.loads(resp.text)
            return EventOutput(event_id=eid,timestamp=timestamp,headline=news_text,event_type=d.get("event_type","Unknown"),category=d.get("category","Unknown"),entities=ents,directional_bias=d.get("directional_bias","Neutral"),confidence_score=d.get("confidence_score",0.5),source=source,sentiment_score=sent,raw_text=news_text,processing_timestamp=pt)
        except Exception as e:
            print(f"  [WARN] Gemini error: {e}")
            return EventOutput(event_id=eid,timestamp=timestamp,headline=news_text,event_type="Unknown Error",category="Unknown",entities=ents,directional_bias="Neutral",confidence_score=0.1,source=source,sentiment_score=sent,raw_text=news_text,processing_timestamp=pt)

def run_event_agent(news_text, timestamp) -> EventOutput:
    return AdvancedEventAgent().process_news(news_text=news_text,timestamp=timestamp,source="Pipeline Input")

def main():
    print("="*70+"\n  AGENT 1 -- EVENT DETECTION & CLASSIFICATION\n"+"="*70)
    if not MOCK_MODE:
        scraper = NewsAPIScraper(api_key=NEWSAPI_KEY); news = scraper.fetch_news()
        if not news: scraper = MockNewsScraper(); news = scraper.fetch_news()
    else: scraper = MockNewsScraper(); news = scraper.fetch_news()
    agent = AdvancedEventAgent(); events = []
    for i, art in enumerate(news):
        print(f"\n[{i+1}/{len(news)}] Processing: {art['headline'][:80]}...")
        ev = agent.process_news(art["headline"],art["timestamp"],art["source"])
        events.append(ev)
        print(f"  -> Type:{ev.event_type} Sent:{ev.sentiment_score:.2f} Bias:{ev.directional_bias} Conf:{ev.confidence_score:.2f}")
        if not MOCK_MODE and i < len(news)-1: time.sleep(RATE_LIMIT_SEC)
    out = str(resolve_path(_CFG["paths"]["a1_events"]))
    os.makedirs(os.path.dirname(out),exist_ok=True)
    with open(out,"w",encoding="utf-8") as f: json.dump([e.model_dump() for e in events],f,indent=4)
    print(f"\n[OK] Agent 1 complete -- saved {len(events)} events to {out}")

if __name__ == "__main__": main()
