from __future__ import annotations
import json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'
REGIONS={'africa':('nigeria','ghana','kenya','south africa','rwanda','uganda','tanzania','egypt'), 'west_africa':('nigeria','ghana','senegal','cote d ivoire','ivory coast'), 'europe':('uk','united kingdom','france','germany','spain','italy','europe'), 'north_america':('usa','united states','canada','mexico'), 'asia':('india','pakistan','bangladesh','indonesia','philippines','singapore','japan','asia'), 'latin_america':('brazil','mexico','colombia','argentina','chile','latin america'), 'middle_east':('uae','saudi','qatar','israel','middle east')}
def load(n):
 try:return json.loads((DATA/n).read_text(encoding='utf-8'))
 except Exception:return {}
def main():
 audit=load('audit.json'); items=audit.get('items',[]); patterns=load('cross_problem_patterns.json').get('patterns',[]); regions=Counter()
 for x in items:
  t=f"{x.get('title','')} {x.get('text','')}".lower(); hit=False
  for r,terms in REGIONS.items():
   if any(term in t for term in terms): regions[r]+=1;hit=True
  if not hit: regions['unspecified']+=1
 out={'generated_at':datetime.now(timezone.utc).isoformat(),'scope':'global','regional_signal_counts':dict(regions),'design_principles':['country-aware evidence collection','global problem taxonomy with local context','compare recurrence within and across markets','separate observed evidence from inference','sell aggregated intelligence rather than identities'],'intelligence_units':['problem','mechanism','market','sector','population','trend','evidence','confidence'],'commercial_products':['Global Problem Radar','Country Intelligence','Sector Intelligence','Enterprise Customer Intelligence','Opportunity Intelligence API'],'privacy_boundary':'Raw identities are not a product. The system should minimise personal data, apply aggregation/anonymisation where appropriate, restrict access to source material, and assess jurisdiction-specific legal requirements before commercial use.'}
 (DATA/'global_intelligence.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8');REPORTS.mkdir(exist_ok=True);(REPORTS/'global-intelligence.md').write_text('# Problem Radar — Global Intelligence\n\nProblem Radar is global by design, with Nigeria as the initial market rather than a permanent boundary.\n\n## Product principle\n\n**Sell intelligence, not identities.** Customers receive aggregated patterns, evidence provenance, trends and decision support—not names, contact details, private messages or identifiable complainants.\n\n## Global model\n\nCountry → region → sector → problem → underlying mechanism → evidence → trend → action.\n\nThe same mechanism can be compared across countries without assuming that a problem has the same causes, economics or solution everywhere.\n\n## Commercial surfaces\n\n- Global Problem Radar\n- Country intelligence reports\n- Sector intelligence\n- Enterprise customer-intelligence feeds\n- Opportunity Intelligence API\n\n## Trust boundary\n\nPersonal data must be minimised and protected. Pseudonymisation is not equivalent to anonymisation where re-identification remains possible; truly anonymous data requires that the individual is no longer identifiable. This is a key principle under GDPR and should inform the platform architecture even when a specific customer is outside the EU. citeturn0search0turn0search1\n',encoding='utf-8');print('[radar] global intelligence layer ready')
if __name__=='__main__':main()
