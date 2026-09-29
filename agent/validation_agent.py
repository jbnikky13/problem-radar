from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'
PUBLIC_SOURCES=[('NBS National Business Sample Survey 2024','business prevalence, sector, firm characteristics'),('NBS General Household Survey 2023-2024','household, mobile and internet access'),('NBS Telecoms Data 2025','connectivity and telecom usage'),('NBS Job Creation Survey 2025','employment and labour-market context'),('NBS GDP collection','sector/economic context')]
def load(n):
 try:return json.loads((DATA/n).read_text(encoding='utf-8'))
 except Exception:return {}
def main():
 d=load('cross_problem_patterns.json'); ps=d.get('patterns',[]); rows=[]
 for p in ps:
  rows.append({'id':p['id'],'mechanism':p['mechanism'],'sectors':p['categories'],'hypothesis':p['business_thesis'],'validation_stage':'problem_validation','customer_segments':['Consumers directly affected','Small businesses affected','Businesses that currently pay to manage the problem','Institutions responsible for the underlying workflow'],'research_tasks':['Validate the same underlying pain across at least two sectors.','Quantify frequency and economic cost.','Identify the current workaround and its cost.','Map existing Nigerian alternatives and pricing.','Interview affected users and potential payers.','Run a manual concierge MVP before software.'],'public_data_checks':[{'source':s,'use':u} for s,u in PUBLIC_SOURCES],'experiment':{'duration_days':14,'type':'manual concierge','success_metrics':['qualified users requesting the service','repeat usage','willingness to pay','time/cost saved','referrals'],'failure_signal':'No repeat demand or no credible willingness to pay after targeted validation.'},'status':'do_not_build_yet'})
 now=datetime.now(timezone.utc).isoformat();(DATA/'validation_agent_queue.json').write_text(json.dumps({'generated_at':now,'queue_count':len(rows),'queue':rows},indent=2,ensure_ascii=False),encoding='utf-8'); lines=['# Problem Radar — Validation Agent Queue','',f'Generated: {now}','', 'This queue turns cross-sector hypotheses into experiments. No candidate is considered validated until external evidence and customer behaviour support it.','']
 for x in rows: lines += [f"## {x['id']} — {x['mechanism'].replace('_',' ').title()}",f"**Sectors:** {', '.join(x['sectors'])}",'','### Customer segments',*[f'- {q}' for q in x['customer_segments']],'','### Research tasks',*[f'- {q}' for q in x['research_tasks']],'','### Public-data checks',*[f"- **{q['source']}** — {q['use']}" for q in x['public_data_checks']],'','### 14-day manual experiment',*[f'- **{k}:** {v}' for k,v in x['experiment'].items() if k!='success_metrics'],*[f'- **Success metric:** {m}' for m in x['experiment']['success_metrics']],'','---','']
 (REPORTS/'validation-agent-queue.md').write_text('\n'.join(lines),encoding='utf-8');print(f'[radar] queued {len(rows)} validation experiments')
if __name__=='__main__':main()
