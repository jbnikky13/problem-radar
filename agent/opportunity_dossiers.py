from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'
def main():
 d=json.loads((DATA/'problem_clusters.json').read_text(encoding='utf-8')); cs=d.get('clusters',[]); rows=[]
 for c in cs:
  evidence=c['evidence_score']; recurrence=c['recurrence_score']; diversity=c['source_diversity_score']; gap=c['information_gap_score']; auto=c['automation_score'];
  rows.append({**c,'dossier_status':'research_required','evidence_summary':f"{c['observation_count']} audited observations across {len(c['source_domains'])} source domain(s).",'what_to_verify':['Confirm the underlying user problem independently.','Check whether reports describe the same event or recurring condition.','Identify existing products/workarounds before building.','Validate willingness to pay with affected users.'],'build_hypotheses':['Verification or information service','Workflow/automation layer','Monitoring/alerting layer'],'decision_note':'This dossier is an evidence map, not an investment or business verdict.','research_priority_signal':round((evidence+recurrence+diversity+gap+auto)/5,3)})
 rows.sort(key=lambda x:x['research_priority_signal'],reverse=True); now=datetime.now(timezone.utc).isoformat(); (DATA/'opportunity_dossiers.json').write_text(json.dumps({'generated_at':now,'dossier_count':len(rows),'dossiers':rows},indent=2,ensure_ascii=False),encoding='utf-8'); lines=['# Problem Radar — Opportunity Dossiers','',f'Generated: {now}','',f'Dossiers: **{len(rows)}**',''];
 for c in rows[:25]: lines += [f"## {c['id']} — {c['title']}",f"**Category:** `{c['category']}`  ",f"**Research priority signal:** `{c['research_priority_signal']}`  ",f"**Evidence:** {c['evidence_summary']}",'','### What to verify',*[f'- {x}' for x in c['what_to_verify']],'','### Build hypotheses',*[f'- {x}' for x in c['build_hypotheses']],'','---','']
 (REPORTS/'opportunity-dossiers.md').write_text('\n'.join(lines),encoding='utf-8')
if __name__=='__main__':main()
