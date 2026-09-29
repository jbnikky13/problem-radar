from __future__ import annotations
import json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'

def load(name):
 try:return json.loads((DATA/name).read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError):return {}

def main():
 d=load('problem_clusters.json'); clusters=d.get('clusters',[]); out=[]
 for c in clusters:
  evidence=float(c.get('evidence_score',0)); recurrence=float(c.get('recurrence_score',0)); diversity=float(c.get('source_diversity_score',0)); gap=float(c.get('information_gap_score',0)); automation=float(c.get('automation_score',0)); monetization=float(c.get('monetization_signal_score',0));
  market_signal=min(1.0,0.28*recurrence+0.22*diversity+0.18*evidence+0.17*gap+0.15*monetization)
  buildability=min(1.0,0.55*automation+0.25*gap+0.20*monetization)
  validation_priority=round(0.55*market_signal+0.45*buildability,3)
  out.append({**c,'market_signal':round(market_signal,3),'buildability_signal':round(buildability,3),'validation_priority':validation_priority,'business_status':'validate_before_building','customer_questions':['Who experiences this problem most often?','How frequently does it occur?','What does the person/business currently do instead?','What does the problem cost in money, time, risk, or lost opportunity?','Would the affected user pay for a materially better solution?'],'business_model_hypotheses':['B2C transaction or subscription','B2B workflow/service fee','Verification or information fee','Marketplace/lead-generation fee'],'anti_overclaim_note':'Signals indicate what to investigate; they do not establish market size, profitability, or likelihood of success.'})
 out.sort(key=lambda x:x['validation_priority'],reverse=True); now=datetime.now(timezone.utc).isoformat();
 (DATA/'business_opportunities.json').write_text(json.dumps({'generated_at':now,'opportunity_count':len(out),'opportunities':out},indent=2,ensure_ascii=False),encoding='utf-8')
 lines=['# Problem Radar — Business Opportunity Validation Map','',f'Generated: {now}','', 'Purpose: identify Nigerian problems that warrant direct customer and market validation before capital or significant engineering is committed.','',f'Candidate problem clusters: **{len(out)}**','']
 for x in out[:30]:
  lines += [f"## {x['id']} — {x['title']}",f"**Category:** `{x['category']}`  ",f"**Validation priority:** `{x['validation_priority']}`  ",f"**Evidence:** `{x['evidence_score']}`  ",f"**Recurrence:** `{x['recurrence_score']}`  ",f"**Source diversity:** `{x['source_diversity_score']}`  ", '', '### Questions to validate',*[f'- {q}' for q in x['customer_questions']], '', '### Business-model hypotheses',*[f'- {m}' for m in x['business_model_hypotheses']], '', '---','']
 (REPORTS/'business-opportunity-map.md').write_text('\n'.join(lines),encoding='utf-8')
 print(f'[radar] generated {len(out)} business validation candidates')
if __name__=='__main__':main()
