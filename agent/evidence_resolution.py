from __future__ import annotations
import json,re
from datetime import datetime,timezone
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; REPORTS=ROOT/'reports'
MECHANISM_TERMS={
 'trust_verification':['fake','fraud','scam','counterfeit','verify','verification','authentic','legitimate','warning','disowns'],
 'service_reliability':['outage','failed','failure','delay','dropped','slow','unavailable','disruption','complaint'],
 'price_access':['expensive','cost','price','fee','afford','access','shortage'],
 'workflow_information':['application','registration','notice','information','process','complaint','compensation','approval']}
def load(n,default=None):
 try:return json.loads((DATA/n).read_text(encoding='utf-8'))
 except Exception:return [] if default is None else default
def norm(s):return re.sub(r'\W+',' ',str(s).lower()).strip()
def mechanism(c):
 t=norm(' '.join(c.get('representative_problems',[]))+' '+c.get('title','')); scores={k:sum(t.count(x) for x in v) for k,v in MECHANISM_TERMS.items()}; return max(scores,key=scores.get) if max(scores.values()) else 'unclassified'
def main():
 clusters=load('clusters.json'); groups=defaultdict(list)
 for c in clusters: groups[mechanism(c)].append(c)
 candidates=[]
 for m,items in groups.items():
  if len(items)<3: continue
  obs=sum(int(x.get('observation_count',0)) for x in items); domains=set(d for x in items for d in x.get('source_domains',[])); avg_e=sum(float(x.get('evidence_score',0)) for x in items)/len(items); avg_r=sum(float(x.get('recurrence_score',0)) for x in items)/len(items); categories=sorted({x.get('category','unknown') for x in items});
  candidates.append({'id':f'ER-{len(candidates)+1:03d}','mechanism':m,'cluster_count':len(items),'observation_count':obs,'source_domain_count':len(domains),'categories':categories,'average_evidence_score':round(avg_e,2),'average_recurrence_score':round(avg_r,2),'evidence_status':'requires_external_resolution','resolution_questions':['Can independent primary or official sources corroborate the pattern?','Is the apparent recurrence caused by duplicate reporting?','What measurable population or economic impact supports the signal?','Which markets and sectors show the pattern independently?','What existing solutions and institutional responses exist?'],'candidate_clusters':[x['id'] for x in sorted(items,key=lambda z:z.get('observation_count',0),reverse=True)[:10]]})
 candidates.sort(key=lambda x:(x['source_domain_count'],x['observation_count'],x['average_evidence_score']),reverse=True); now=datetime.now(timezone.utc).isoformat(); out={'generated_at':now,'status':'research_queue','principle':'Resolve evidence before commercial or venture conclusions.','candidates':candidates}; (DATA/'evidence_resolution_queue.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8'); lines=['# Evidence Resolution Queue','',f'Generated: {now}','', 'These are research hypotheses, not validated market conclusions. Source diversity is treated as a critical quality control.','']
 for x in candidates: lines += [f"## {x['id']} — {x['mechanism'].replace('_',' ').title()}",f"- Clusters: {x['cluster_count']}",f"- Observations represented: {x['observation_count']}",f"- Source domains: {x['source_domain_count']}",f"- Categories: {', '.join(x['categories'])}",f"- Avg evidence score: {x['average_evidence_score']}",f"- Avg recurrence score: {x['average_recurrence_score']}",'','### Resolve before monetisation',*[f'- {q}' for q in x['resolution_questions']],'','---','']
 (REPORTS/'evidence-resolution-queue.md').write_text('\n'.join(lines),encoding='utf-8'); print(f'[radar] queued {len(candidates)} mechanism-level evidence resolutions')
if __name__=='__main__':main()
