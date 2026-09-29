from __future__ import annotations
import json,re
from collections import Counter
from datetime import datetime,timezone
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; REPORTS=ROOT/'reports'
STOP={'the','and','for','with','from','that','this','are','was','were','has','have','into','after','about','nigeria','nigerian'}
GENERIC={'problem','issue','people','government','company','customers','users','new','says','report','reported','today'}
def load(p):
 try:return json.loads(p.read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError):return {}
def tokens(s):return {w for w in re.findall(r'[a-z0-9]+',(s or '').lower()) if len(w)>2 and w not in STOP}
def similarity(a,b):
 ta,tb=tokens(a),tokens(b)
 if not ta or not tb:return 0.0
 return .65*len(ta&tb)/len(ta|tb)+.35*SequenceMatcher(None,a.lower(),b.lower()).ratio()
def groups(items):
 out=[]
 for x in items:
  placed=False; cat=x.get('audit',{}).get('audit_category','other')
  for g in out:
   if g[0].get('audit',{}).get('audit_category','other')==cat and similarity(x.get('title',''),g[0].get('title',''))>=.38:g.append(x);placed=True;break
  if not placed:out.append([x])
 return [g for g in out if len(g)>=2]
def title(g):
 c=Counter()
 for x in g:c.update(w for w in tokens(x.get('title','')) if w not in GENERIC)
 return ' '.join(w for w,_ in c.most_common(5)).title() or 'Recurring Problem'
def build():
 a=load(DATA/'audit.json'); items=[x for x in a.get('items',[]) if x.get('audit',{}).get('keep_candidate')]; gs=groups(items); out=[]
 for i,g in enumerate(sorted(gs,key=len,reverse=True),1):
  domains={x.get('source_domain') or 'unknown' for x in g}; sources={x.get('source') or 'unknown' for x in g}; rec=min(1,len(g)/8); div=min(1,len(domains)/4); ver=min(1,(len(domains)+len(sources)-1)/6); q=[float(x.get('evidence_quality',0) or 0) for x in g]; p=[float(x.get('pain_score',0) or 0) for x in g]; avgq=sum(q)/len(q) if q else 0; avgp=sum(p)/len(p) if p else 0
  out.append({'id':f'PR-{i:03d}','title':title(g),'category':g[0].get('audit',{}).get('audit_category','other'),'observation_ids':[x['id'] for x in g],'observation_count':len(g),'evidence_score':round((rec+div+ver+avgq)/4,3),'pain_score':round(avgp,3),'recurrence_score':round(rec,3),'information_gap_score':round(min(1,.25+.08*len(g)),3),'automation_score':round(min(1,.2+.07*len(g)),3),'monetization_signal_score':round(min(1,.15+.06*len(domains)+.02*len(g)),3),'source_diversity_score':round(div,3),'verification_score':round(ver,3),'evidence_confidence':'high' if len(g)>=6 and len(domains)>=3 else 'medium' if len(g)>=3 else 'low','existing_solution_signal':0.0,'representative_problems':[x.get('title','') for x in g[:5]],'sources':sorted(sources),'source_domains':sorted(domains),'notes':['Generated from audited evidence; not a business recommendation.']})
 return out
def write(cs):
 DATA.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True); now=datetime.now(timezone.utc).isoformat(); (DATA/'problem_clusters.json').write_text(json.dumps({'generated_at':now,'cluster_count':len(cs),'clusters':cs},indent=2,ensure_ascii=False),encoding='utf-8'); lines=['# Problem Radar — Audited Problem Clusters','',f'Generated: {now}','',f'Clusters: **{len(cs)}**','']
 for c in cs[:30]:lines += [f"## {c['id']} — {c['title']}",f"- Category: `{c['category']}`",f"- Observations: **{c['observation_count']}**",f"- Evidence score: **{c['evidence_score']}**",f"- Confidence: **{c['evidence_confidence']}**",f"- Sources: {', '.join(c['source_domains'])}",'','Representative reports:',*[f'- {x}' for x in c['representative_problems']],'']
 (REPORTS/'audited-problem-clusters.md').write_text('\n'.join(lines),encoding='utf-8')
if __name__=='__main__':
 cs=build();write(cs);print(f'[radar] built {len(cs)} audited problem clusters')
