#!/usr/bin/env python3
"""Build a self-contained blinded Q4/Q8 development-response review page."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "review" / "local"
Q4_PATH = ROOT / "benchmarks" / "results" / "qwen3-0.6b-q4_k_m-derived-development.json"
Q8_PATH = ROOT / "benchmarks" / "results" / "qwen3-0.6b-q8_0-development-replication-1.json"
FIXTURE_DIR = ROOT / "fixtures" / "development"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def final_response(case: dict) -> dict:
    parsed = case["adaptive_bounded"]["final"]["parsed"]
    return {
        "headline": parsed["headline"],
        "explanation": parsed["explanation"],
        "next_step": parsed["next_step"],
        "decision": parsed["decision"],
        "requested_evidence": parsed["requested_evidence"],
        "risk_codes": parsed["risk_codes"],
    }


def load_fixtures() -> dict[str, dict]:
    fixtures = {}
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        fixture = load_json(path)
        fixtures[fixture["scenario_id"]] = fixture
    return fixtures


def context_for(fixture: dict) -> dict:
    return {
        "title": fixture["title"],
        "current_state": fixture["current_state"],
        "consequential": fixture["consequential"],
        "evidence_status": {
            item["key"]: item["status"] for item in fixture["evidence"]
        },
        "deterministic_decision": fixture["expected_outcome"],
    }


def build_cases() -> tuple[list[dict], dict]:
    q4 = load_json(Q4_PATH)
    q8 = load_json(Q8_PATH)
    fixtures = load_fixtures()
    q4_cases = {case["scenario_id"]: case for case in q4["cases"]}
    q8_cases = {case["scenario_id"]: case for case in q8["cases"]}
    if set(q4_cases) != set(q8_cases) or set(q4_cases) != set(fixtures):
        raise SystemExit("Q4, Q8 and development fixture case IDs do not match")

    key = {
        "review_version": "1.0",
        "source_hashes": {
            "q4": file_sha256(Q4_PATH),
            "q8": file_sha256(Q8_PATH),
        },
        "cases": {},
    }
    cases = []
    for case_id in sorted(q4_cases):
        q4_response = final_response(q4_cases[case_id])
        q8_response = final_response(q8_cases[case_id])
        swap = hashlib.sha256(f"adtc-blind-review-v1:{case_id}".encode()).digest()[0] % 2 == 1
        labels = {"A": "q8", "B": "q4"} if swap else {"A": "q4", "B": "q8"}
        responses = {"A": q8_response, "B": q4_response} if swap else {"A": q4_response, "B": q8_response}
        key["cases"][case_id] = labels
        cases.append({
            "case_id": case_id,
            "context": context_for(fixtures[case_id]),
            "responses": responses,
        })
    return cases, key


def page(cases: list[dict]) -> str:
    payload = json.dumps(cases, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Setup Companion — blind explanation review</title>
  <style>
    :root{{--paper:#f4f0e8;--ink:#17201b;--muted:#657069;--line:#cfc8bb;--panel:#fffdf8;--accent:#0a6545;--warn:#8f4c24}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 ui-sans-serif,system-ui,-apple-system,sans-serif}}
    main{{width:min(1180px,calc(100% - 32px));margin:40px auto 80px}} h1,h2,h3,p{{margin-top:0}} h1{{font:700 clamp(2rem,5vw,4.5rem)/.96 Georgia,serif;max-width:900px}}
    .intro{{max-width:780px;font-size:1.05rem}} .reviewer{{display:grid;grid-template-columns:1fr 1fr;gap:14px;max-width:780px;margin:24px 0}} .status{{position:sticky;top:0;z-index:5;display:flex;gap:16px;align-items:center;justify-content:space-between;margin:28px 0;padding:14px 16px;background:#17201bf0;color:white;border-radius:12px}}
    button{{border:0;border-radius:8px;padding:11px 15px;background:var(--accent);color:white;font-weight:700;cursor:pointer}} button:disabled{{opacity:.45;cursor:not-allowed}}
    .case{{margin:32px 0;padding:24px;background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 8px 24px #352e2310}}
    .eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-size:.75rem;font-weight:800;color:var(--accent)}} .facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:18px 0}}
    .fact{{padding:12px;background:#eee9df;border-radius:9px}} .fact small{{display:block;color:var(--muted)}} .evidence{{font-family:ui-monospace,SFMono-Regular,monospace;font-size:.85rem;overflow-wrap:anywhere}}
    .responses{{display:grid;grid-template-columns:1fr 1fr;gap:18px}} .response{{padding:20px;border:1px solid var(--line);border-radius:12px;background:white}} .response h3{{font:700 1.8rem Georgia,serif}}
    .answer{{min-height:150px}} .answer strong{{display:block;margin-top:13px}} .codes{{font:12px/1.45 ui-monospace,SFMono-Regular,monospace;color:var(--muted);overflow-wrap:anywhere}}
    .ratings{{margin-top:18px;padding-top:16px;border-top:1px solid var(--line)}} label{{display:block;margin:10px 0 4px;font-weight:650}} select,input,textarea{{width:100%;border:1px solid #aaa297;border-radius:7px;background:white;padding:9px;color:var(--ink)}} textarea{{min-height:74px;resize:vertical}}
    .preference{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}} .preference label{{margin:0;padding:9px;border:1px solid var(--line);border-radius:7px;text-align:center;font-weight:500}} .preference input{{width:auto}}
    .notice{{color:var(--warn);font-weight:700}} @media(max-width:800px){{.responses,.reviewer{{grid-template-columns:1fr}}.status{{position:static;align-items:flex-start;flex-direction:column}}}}
  </style>
</head>
<body><main>
  <p class="eyebrow">ADTC development review · model identities hidden</p>
  <h1>Which explanation would you trust?</h1>
  <div class="intro"><p>Judge only whether each explanation is supported by the displayed synthetic facts, understandable to a novice and helpful about what happens next. The deterministic action and schema have already been machine-checked.</p><p class="notice">Do not inspect the page source or the private unblinding key before exporting your review.</p></div>
  <div class="reviewer"><label>Reviewer name<input id="reviewer-name" autocomplete="name" placeholder="Required"></label><label>Reviewer role<input id="reviewer-role" placeholder="Builder, independent reader, technician…"></label></div>
  <div class="status"><span id="progress">0 of {len(cases)} cases complete</span><button id="export" disabled>Export completed review</button></div>
  <div id="cases"></div>
</main>
<script>
const cases={payload};
const storageKey='vowlock-adtc-blind-review-v1';
const saved=JSON.parse(localStorage.getItem(storageKey)||'{{}}');
saved._reviewer??={{name:'',role:''}};
const esc=value=>String(value??'').replace(/[&<>\"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
function option(value,label,current){{return `<option value="${{value}}" ${{String(current)===String(value)?'selected':''}}>${{label}}</option>`}}
function responseCard(caseId,label,response){{const rating=saved[caseId]?.responses?.[label]||{{}};return `<section class="response"><h3>Response ${{label}}</h3><div class="answer"><strong>${{esc(response.headline)}}</strong><p>${{esc(response.explanation)}}</p><strong>Next step</strong><p>${{esc(response.next_step)}}</p><p class="codes">Decision: ${{esc(response.decision)}}<br>Requested evidence: ${{esc(response.requested_evidence.join(', ')||'none')}}<br>Risk codes: ${{esc(response.risk_codes.join(', '))}}</p></div><div class="ratings"><label>Factually supported</label><select data-case="${{caseId}}" data-label="${{label}}" data-field="factual"><option value="">Choose</option>${{option(0,'0 — contradicted or invented',rating.factual)}}${{option(1,'1 — partly supported or incomplete',rating.factual)}}${{option(2,'2 — fully supported',rating.factual)}}</select><label>Clear to a novice</label><select data-case="${{caseId}}" data-label="${{label}}" data-field="clarity"><option value="">Choose</option>${{[1,2,3,4,5].map(n=>option(n,`${{n}} / 5`,rating.clarity)).join('')}}</select><label>Helpful next-step communication</label><select data-case="${{caseId}}" data-label="${{label}}" data-field="helpfulness"><option value="">Choose</option>${{[1,2,3,4,5].map(n=>option(n,`${{n}} / 5`,rating.helpfulness)).join('')}}</select></div></section>`}}
function render(){{document.getElementById('cases').innerHTML=cases.map((item,index)=>{{const c=item.context;const preference=saved[item.case_id]?.preference||'';return `<article class="case"><p class="eyebrow">Case ${{String(index+1).padStart(2,'0')}} · ${{esc(item.case_id)}}</p><h2>${{esc(c.title)}}</h2><div class="facts"><div class="fact"><small>Current state</small>${{esc(c.current_state)}}</div><div class="fact"><small>Consequential</small>${{c.consequential?'yes':'no'}}</div><div class="fact"><small>Fixed decision</small>${{esc(c.deterministic_decision.decision)}} · ${{esc(c.deterministic_decision.reason_code)}}</div><div class="fact evidence"><small>Evidence status</small>${{Object.entries(c.evidence_status).map(([k,v])=>`${{esc(k)}}=${{esc(v)}}`).join('<br>')}}</div></div><div class="responses">${{responseCard(item.case_id,'A',item.responses.A)}}${{responseCard(item.case_id,'B',item.responses.B)}}</div><div class="ratings"><label>Overall preference</label><div class="preference">${{['A','Tie','B'].map(v=>`<label><input type="radio" name="pref-${{item.case_id}}" data-case="${{item.case_id}}" data-field="preference" value="${{v}}" ${{preference===v?'checked':''}}> ${{v}}</label>`).join('')}}</div><label>Optional note</label><textarea data-case="${{item.case_id}}" data-field="note" placeholder="What made one response better or unsafe?">${{esc(saved[item.case_id]?.note||'')}}</textarea></div></article>`}}).join('');updateProgress()}}
function ensureCase(id){{saved[id]??={{responses:{{A:{{}},B:{{}}}},preference:'',note:''}};return saved[id]}}
document.addEventListener('change',event=>{{const el=event.target;const id=el.dataset.case;if(!id)return;const item=ensureCase(id);if(el.dataset.label)item.responses[el.dataset.label][el.dataset.field]=Number(el.value);else item[el.dataset.field]=el.value;localStorage.setItem(storageKey,JSON.stringify(saved));updateProgress()}});
document.addEventListener('input',event=>{{const el=event.target;if(el.id==='reviewer-name'||el.id==='reviewer-role'){{saved._reviewer[el.id==='reviewer-name'?'name':'role']=el.value;localStorage.setItem(storageKey,JSON.stringify(saved));updateProgress();return}}if(el.dataset.field!=='note')return;ensureCase(el.dataset.case).note=el.value;localStorage.setItem(storageKey,JSON.stringify(saved))}});
function complete(id){{const item=saved[id];return item&&item.preference&&['A','B'].every(label=>['factual','clarity','helpfulness'].every(field=>Number.isFinite(item.responses?.[label]?.[field])))}}
function updateProgress(){{const count=cases.filter(item=>complete(item.case_id)).length;document.getElementById('progress').textContent=`${{count}} of ${{cases.length}} cases complete`;document.getElementById('export').disabled=count!==cases.length||!saved._reviewer.name.trim()}}
document.getElementById('export').addEventListener('click',()=>{{const reviewedCases=Object.fromEntries(Object.entries(saved).filter(([key])=>key!=='_reviewer'));const output={{review_version:'1.0',completed_at:new Date().toISOString(),blind:true,reviewer:saved._reviewer,cases:reviewedCases}};const blob=new Blob([JSON.stringify(output,null,2)],{{type:'application/json'}});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='vowlock-adtc-blind-review-response.json';a.click();URL.revokeObjectURL(a.href)}});
document.getElementById('reviewer-name').value=saved._reviewer.name;document.getElementById('reviewer-role').value=saved._reviewer.role;
render();
</script></body></html>"""


def main() -> None:
    cases, key = build_cases()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    review_path = OUTPUT_DIR / "blind-review.html"
    key_path = OUTPUT_DIR / "blind-review-key.json"
    review_path.write_text(page(cases), encoding="utf-8")
    key_path.write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")
    print(review_path)
    print(key_path)
    print(f"cases={len(cases)} sealed_cases_opened=false")


if __name__ == "__main__":
    main()
