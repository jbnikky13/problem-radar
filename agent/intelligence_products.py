from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'
PRODUCTS={
 'government_service_intelligence':('Government departments, regulators and public agencies','Service-failure trends, recurring citizen pain points, access gaps and regional signals','service redesign, prioritisation, monitoring'),
 'business_customer_intelligence':('Companies and SMEs','Customer complaints, workflow friction, trust gaps, pricing and service reliability signals','product improvement, CX, retention, new-service discovery'),
 'sector_intelligence':('Industry associations and sector operators','Cross-company problem patterns and emerging operational risks','benchmarking, policy input, shared infrastructure'),
 'insight_api':('Developers, researchers and data teams','Machine-readable aggregated problem signals and trend metadata','research, dashboards, internal decision systems'),
 'opportunity_intelligence':('Founders, investors and innovation teams','Validated problem clusters, unmet needs and cross-sector mechanisms','venture discovery and market validation')}
def load(n):
 try:return json.loads((DATA/n).read_text(encoding='utf-8'))
 except Exception:return {}
def main():
 clusters=load('problem_clusters.json').get('clusters',[]); patterns=load('cross_problem_patterns.json').get('patterns',[]); now=datetime.now(timezone.utc).isoformat(); products=[]
 for key,(buyers,value,use) in PRODUCTS.items(): products.append({'id':key,'buyers':buyers,'value':value,'uses':use,'data_inputs':['aggregated problem clusters','source diversity and recurrence signals','sector/category trends','cross-problem mechanisms'],'delivery':['dashboard','periodic intelligence report','API/export for eligible customers'],'privacy_boundary':'Do not expose raw personal data, identifiable complainants, private messages, or sensitive records. Customer products should use aggregation, minimisation and de-identification appropriate to the lawful purpose.','status':'concept'})
 out={'generated_at':now,'purpose':'turn aggregated problem evidence into decision-support products without selling personal data','products':products,'current_cluster_count':len(clusters),'current_cross_problem_pattern_count':len(patterns)}; (DATA/'intelligence_products.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
 lines=['# Problem Radar — Intelligence Products','',f'Generated: {now}','', 'Problem Radar can serve two connected purposes: discover businesses and sell aggregated intelligence to organizations improving services.','']
 for p in products: lines += [f"## {p['id'].replace('_',' ').title()}",f"**Customers:** {p['buyers']}",f"**Value:** {p['value']}",f"**Uses:** {p['uses']}",'','Delivery: '+', '.join(p['delivery']),'', '**Privacy boundary:** '+p['privacy_boundary'],'','---','']
 (REPORTS/'intelligence-products.md').write_text('\n'.join(lines),encoding='utf-8');print(f'[radar] defined {len(products)} intelligence products')
if __name__=='__main__':main()
