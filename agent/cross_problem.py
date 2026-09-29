from __future__ import annotations
import json,re
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'
MECHANISMS={
 'verification_trust':('verify','verification','fake','fraud','scam','counterfeit','legit','trust','authentic'),
 'access_discovery':('find','where','available','access','availability','locate','directory','information'),
 'payments_reconciliation':('payment','transfer','refund','reversal','charge','receipt','invoice','pos'),
 'coordination_logistics':('delivery','dispatch','queue','delay','booking','appointment','schedule','coordination'),
 'price_transparency':('price','cost','fee','expensive','overcharged','compare','quotation','quote'),
 'workflow_compliance':('registration','license','permit','compliance','documentation','form','application','approval'),
 'service_reliability':('failed','unavailable','delay','outage','not working','reliable','downtime'),
 'identity_records':('identity','record','credential','certificate','document','history','proof')}
def load(p):
 try:return json.loads((DATA/p).read_text(encoding='utf-8'))
 except Exception:return {}
def text(x):return re.sub(r'\s+',' ',f"{x.get('title','')} {' '.join(x.get('representative_problems',[]))}").lower()
def main():
 d=load('problem_clusters.json'); cs=d.get('clusters',[]); found=[]
 for name,terms in MECHANISMS.items():
  hits=[c for c in cs if sum(t in text(c) for t in terms)>=2]
  cats=sorted({c.get('category','other') for c in hits})
  if len(hits)>=2 and len(cats)>=2:
   evidence=sum(float(c.get('evidence_score',0)) for c in hits)/len(hits); reach=min(1,len(cats)/5); recurrence=min(1,sum(c.get('observation_count',0) for c in hits)/20); leverage=round(.35*reach+.35*recurrence+.30*evidence,3)
   found.append({'id':f'CP-{len(found)+1:03d}','mechanism':name,'clusters':[c['id'] for c in hits],'categories':cats,'cluster_count':len(hits),'observation_count':sum(c.get('observation_count',0) for c in hits),'cross_sector_reach':round(reach,3),'evidence_signal':round(evidence,3),'recurrence_signal':round(recurrence,3),'leverage_signal':leverage,'business_thesis':f"A shared {name.replace('_',' ')} layer may serve multiple Nigerian sectors.",'validation_questions':['Do affected users describe the same underlying failure across sectors?','Can one workflow solve the shared mechanism without sector-specific complexity?','Who is the common paying customer or economic beneficiary?','Can the service start as a narrow manual MVP?'],'status':'hypothesis_requires_validation'})
 found.sort(key=lambda x:x['leverage_signal'],reverse=True)
 now=datetime.now(timezone.utc).isoformat();(DATA/'cross_problem_patterns.json').write_text(json.dumps({'generated_at':now,'pattern_count':len(found),'patterns':found},indent=2,ensure_ascii=False),encoding='utf-8');lines=['# Problem Radar — Cross-Problem Patterns','',f'Generated: {now}','', 'These are hypotheses about shared mechanisms appearing across sectors. They are not business verdicts.','']
 for x in found:lines += [f"## {x['id']} — {x['mechanism'].replace('_',' ').title()}",f"- Sectors: {', '.join(x['categories'])}",f"- Clusters: {x['cluster_count']}",f"- Observations: {x['observation_count']}",f"- Cross-sector reach: {x['cross_sector_reach']}",f"- Leverage signal: **{x['leverage_signal']}**",'', '### Validation questions',*[f'- {q}' for q in x['validation_questions']],'','---','']
 (REPORTS/'cross-problem-patterns.md').write_text('\n'.join(lines),encoding='utf-8');print(f'[radar] found {len(found)} cross-problem patterns')
if __name__=='__main__':main()
