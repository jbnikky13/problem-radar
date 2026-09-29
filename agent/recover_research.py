from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'
def read(name,default):
 try:return json.loads((DATA/name).read_text(encoding='utf-8'))
 except Exception:return default
def main():
 clusters=read('clusters.json',[]); observations=read('observations.json',[]); heartbeat=read('heartbeat.json',{}); now=datetime.now(timezone.utc).isoformat()
 if not clusters: raise SystemExit('No canonical clusters.json available; refusing to fabricate recovery data.')
 total=sum(int(c.get('observation_count',0)) for c in clusters)
 manifest={'generated_at':now,'status':'recovered_from_committed_cluster_state','canonical_cluster_file':'data/clusters.json','canonical_observation_file':'data/observations.json','cluster_count':len(clusters),'cluster_observation_count':total,'observation_store_count':len(observations),'heartbeat':heartbeat,'recovery_note':'The committed repository currently contains the full cluster state but the observation store may be empty. Cluster state is preserved as the authoritative research snapshot until raw observations are committed by the collection workflow. No missing raw records are reconstructed.'}
 (DATA/'research_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
 (DATA/'problem_clusters.json').write_text(json.dumps(clusters,indent=2,ensure_ascii=False),encoding='utf-8')
 REPORTS.mkdir(exist_ok=True);(REPORTS/'data-recovery.md').write_text(f'''# Problem Radar — Data Recovery\n\nGenerated: `{now}`\n\nThe repository contains **{len(clusters)} committed clusters representing {total} observations**. The raw `observations.json` store currently contains **{len(observations)}** records.\n\nThe recovery layer therefore preserves the committed cluster state as the canonical research snapshot and explicitly refuses to invent missing raw observations. Future research runs must commit the raw observation store or an equivalent immutable evidence artifact.\n''',encoding='utf-8')
 print(f'[radar] recovered {len(clusters)} clusters / {total} cluster observations; raw store={len(observations)}')
if __name__=='__main__':main()
