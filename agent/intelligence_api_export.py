from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'
def load(n):
 try:return json.loads((DATA/n).read_text(encoding='utf-8'))
 except Exception:return {}
def main():
 clusters=load('problem_clusters.json').get('clusters',[]); patterns=load('cross_problem_patterns.json').get('patterns',[]); markets=load('global_intelligence.json').get('regional_signal_counts',{}); now=datetime.now(timezone.utc).isoformat(); records=[]
 for c in clusters:
  records.append({'problem_id':c['id'],'market':'global_pending_market_resolution','sector':c.get('category'),'mechanism':'pending_cross_problem_resolution','observation_count':c.get('observation_count',0),'evidence_score':c.get('evidence_score',0),'recurrence_score':c.get('recurrence_score',0),'confidence':c.get('evidence_confidence'),'source_domains':c.get('source_domains',[])})
 out={'generated_at':now,'schema_version':'1.0','privacy_mode':'aggregated_intelligence_only','records':records,'available_region_signals':markets,'cross_problem_patterns':patterns};(DATA/'intelligence_export.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8');(REPORTS/'api-contract.md').write_text('# Problem Radar — Intelligence API Contract\n\n## Purpose\nExpose aggregated problem intelligence to approved consumers without exposing identities.\n\n## Query dimensions\n- market/country\n- region\n- sector\n- problem category\n- underlying mechanism\n- evidence confidence\n- recurrence\n- time period\n\n## Response concept\nEach record returns a problem identifier, context, evidence metrics, trend metadata when available, and source-domain counts. Raw personal identifiers and private source content are excluded.\n\n## Trust requirements\nConsumers should receive provenance and confidence metadata so that intelligence is not presented as ground truth.\n',encoding='utf-8');print(f'[radar] exported {len(records)} intelligence records')
if __name__=='__main__':main()
