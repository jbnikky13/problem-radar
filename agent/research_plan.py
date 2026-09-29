from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'
def main():
 try:d=json.loads((DATA/'business_opportunities.json').read_text(encoding='utf-8'))
 except Exception:d={'opportunities':[]}
 rows=[]
 for x in d.get('opportunities',[])[:20]:
  rows.append({'id':x['id'],'problem':x['title'],'category':x['category'],'priority':x['validation_priority'],'research_tasks':['Find independent reports and first-person accounts.','Estimate affected population using public statistics.','Map existing Nigerian alternatives and their pricing.','Identify the paying customer, not only the beneficiary.','Interview or survey affected users.','Test a manual service before building software.'],'go_no_go_gates':['Evidence from multiple independent sources','Clear recurring pain','Identifiable paying customer','Existing workaround with measurable cost','Willingness-to-pay evidence','A small manual MVP can deliver value']})
 now=datetime.now(timezone.utc).isoformat();(DATA/'validation_plan.json').write_text(json.dumps({'generated_at':now,'plans':rows},indent=2,ensure_ascii=False),encoding='utf-8');lines=['# Problem Radar — Validation Plan','',f'Generated: {now}','', 'The goal is to validate a business, not merely rank complaints.','']
 for x in rows:lines += [f"## {x['id']} — {x['problem']}",f"Priority signal: **{x['priority']}**",'', '### Research tasks',*[f'- {t}' for t in x['research_tasks']],'', '### Go/no-go evidence gates',*[f'- {g}' for g in x['go_no_go_gates']],'','---','']
 (REPORTS/'validation-plan.md').write_text('\n'.join(lines),encoding='utf-8')
if __name__=='__main__':main()
