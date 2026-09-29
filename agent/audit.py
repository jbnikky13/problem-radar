from __future__ import annotations
import html, json, re
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"; REPORTS=ROOT/"reports"
NG=("nigeria","nigerian","lagos","abuja","port harcourt","rivers state","naira","₦")
FOREIGN=("pakistan","india","canada","united kingdom","america","american","united states","kenya","ghana","south africa","north korea")
PROBLEM=("problem","issue","difficult","expensive","scam","fraud","fake","counterfeit","delay","delayed","unavailable","not working","failed","complaint","shortage","lack of","queue","overcharged","lost money","reversal","frustrat","can't","cannot")
CATS={"power":("electricity","power outage","generator","diesel","fuel","phcn","nepa","inverter"),"connectivity":("internet","data","network","wifi","broadband","airtel","mtn","glo","9mobile"),"payments":("payment","transfer","pos","bank","invoice","refund","charge","reversal"),"security":("scam","fraud","fake","counterfeit","theft","robbery","unsafe"),"healthcare":("hospital","doctor","clinic","medicine","drug","health","patient","pharmacy"),"logistics":("delivery","package","shipping","courier","logistics","dispatch"),"business":("business","customer","sales","inventory","supplier","wholesale","merchant"),"jobs":("job","employment","hiring","salary","career","cv","unemployment"),"housing":("rent","house","landlord","property","apartment","housing"),"transport":("transport","bus","taxi","fare","traffic","commute","road"),"government":("government","cac","tax","passport","license","registration","agency"),"food":("food","rice","beans","tomato","market","grocery","price","shopping"),"education":("school","student","teacher","tuition","exam","university"),"water":("water","borehole","tanker","well"),"repairs":("repair","technician","plumber","electrician","mechanic","artisan")}

def load(p):
    try:return json.loads(p.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return []
def clean(s):return re.sub(r"\s+"," ",html.unescape(s or "")).strip()
def norm(s):return re.sub(r"[^a-z0-9\s]"," ",clean(s).lower()).strip()
def relevance(x):
    t=norm(f"{x.get('title','')} {x.get('text','')}"); ng=sum(m in t for m in NG); foreign=sum(m in t for m in FOREIGN); p=sum(m in t for m in PROBLEM)
    if foreign and ng==0:return "exclude_foreign",0.0,p
    if ng>=2:return "high",1.0,p
    if ng==1:return "medium",.75,p
    return "low",.4,p
def category(x):
    t=norm(f"{x.get('title','')} {x.get('text','')}"); scores={k:sum(t.count(z) for z in v) for k,v in CATS.items()}
    return max(scores,key=scores.get) if max(scores.values(),default=0) else "other"
def duplicate_groups(items):
    out=[];used=set();titles={x["id"]:norm(x.get("title","")) for x in items}
    for i,a in enumerate(items):
        if a["id"] in used:continue
        g=[a["id"]]
        for b in items[i+1:]:
            if b["id"] in used:continue
            sim=SequenceMatcher(None,titles[a["id"]],titles[b["id"]]).ratio()
            if sim>=.90 or ((a.get("source_domain") or "")==(b.get("source_domain") or "") and sim>=.78):
                g.append(b["id"]);used.add(b["id"])
        used.add(a["id"])
        if len(g)>1:out.append(g)
    return out

def run_audit():
    obs=load(DATA/"observations.json"); audited=[]
    for x in obs:
        label,score,p=relevance(x)
        audited.append({**x,"audit":{"nigeria_relevance":label,"nigeria_relevance_score":score,"problem_signal_count":p,"problem_relevance_score":min(1,p/3),"audit_category":category(x),"keep_candidate":score>=.75 and p>=1}})
    groups=duplicate_groups(audited); lookup={oid:i for i,g in enumerate(groups,1) for oid in g}
    for x in audited:
        x["audit"]["duplicate_group"]=lookup.get(x["id"])
        x["audit"]["independent_evidence"]=bool(x["audit"]["keep_candidate"] and x["audit"]["duplicate_group"] is None)
    kept=[x for x in audited if x["audit"]["keep_candidate"]]
    independent=[x for x in kept if x["audit"]["independent_evidence"]]
    result={"generated_at":datetime.now(timezone.utc).isoformat(),"raw_observations":len(obs),"audit_candidates":len(kept),"independent_candidates":len(independent),"excluded":len(obs)-len(kept),"duplicate_groups":len(groups),"observations_in_duplicate_groups":sum(map(len,groups)),"categories":dict(Counter(x["audit"]["audit_category"] for x in kept).most_common()),"sources":dict(Counter(x.get("source_domain","unknown") for x in kept).most_common(20)),"nigeria_relevance":dict(Counter(x["audit"]["nigeria_relevance"] for x in audited)),"items":audited}
    (DATA/"audit.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    REPORTS.mkdir(parents=True,exist_ok=True)
    lines=["# Problem Radar — Evidence Audit v2","",f"Generated: {result['generated_at']}","",f"- Raw observations: **{result['raw_observations']}**",f"- Audit candidates: **{result['audit_candidates']}**",f"- Independent candidates: **{result['independent_candidates']}**",f"- Excluded/noisy: **{result['excluded']}**",f"- Duplicate groups: **{result['duplicate_groups']}**",f"- Observations in duplicate groups: **{result['observations_in_duplicate_groups']}**",""]
    lines += ["Raw observations are preserved. Audit candidates are Nigeria-relevant and contain at least one problem signal. Duplicate records are flagged rather than deleted.","","## Candidate categories",""]+[f"- **{k}** — {v}" for k,v in Counter(x["audit"]["audit_category"] for x in kept).most_common()]
    lines += ["","## Source domains",""]+[f"- `{k}` — {v}" for k,v in Counter(x.get("source_domain","unknown") for x in kept).most_common(20)]
    lines += ["","## Next pass","", "Rebuild problem clusters from audit candidates, using duplicate/event suppression and evidence diversity rather than raw observation count."]
    (REPORTS/"evidence-audit.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":print(json.dumps(run_audit(),indent=2))
