from typing import Dict, List
from project_gamma.src.gamma.alias_engine.master_store import all_counterparties
from project_gamma.src.gamma.alias_engine.alias_store import all_aliases, insert_alias
from project_gamma.src.gamma.alias_engine.fuzzy import score

AUTO_THRESHOLD = 0.899
TOP_K = 5

def resolve_one(raw_name: str, tenant_id: int, approver=None) -> Dict:
    raw = (raw_name or "").strip()
    if not raw:
        return {"status": "empty"}

    # 1. exact alias hit
    for a in all_aliases():
        if raw == a["raw_name"]:
            return {
                "status": "exact",
                "match": a,
                "score": 1.0,
            }

    candidates: List[Dict] = []

    # 2a. fuzzy against counterparties
    for c in all_counterparties():
        s = score(raw, c["name"])
        candidates.append({
            "source": "counterparty",
            "name": c["name"],
            "ctpty_id": c["id"],
            "tenant_id": c["tenant_id"],
            "score": s,
        })

    # 2b. fuzzy against aliases
    for a in all_aliases():
        s_raw = score(raw, a["raw_name"])
        candidates.append({
            "source": "alias_raw",
            "name": a["raw_name"],
            "alias": a,
            "score": s_raw,
        })

        s_acc = score(raw, a["accepted_name"])
        candidates.append({
            "source": "alias_accepted",
            "name": a["accepted_name"],
            "alias": a,
            "score": s_acc,
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    top = candidates[:TOP_K]

    # print(top)

    # 3. auto-map
    if top and top[0]["score"] >= AUTO_THRESHOLD:
        best = top[0]

        if best["source"] == "counterparty":
            insert_alias(
                raw_name=raw,
                accepted_name=best["name"],
                ctpty_id=best["ctpty_id"],
                tenant_id=tenant_id,
                approver=approver,
            )

        else:
            insert_alias(
                raw_name=raw,
                accepted_name=best["name"],
                ctpty_id=best["alias"]["ctpty_id"],
                tenant_id=tenant_id,
                approver=approver,
            )

        return {
            "status": "auto",
            "match": best,
            "score": best["score"],
        }

    return {
        "status": "manual",
        "raw_name": raw,
        "candidates": top,
    }

def resolve_readonly(raw_name: str) -> Dict:
    raw = (raw_name or "").strip()
    if not raw:
        return {"status": "empty"}

    # exact alias hit
    for a in all_aliases():
        if raw == a["raw_name"]:
            return {"status": "exact", "match": a, "score": 1.0}

    candidates = []

    for c in all_counterparties():
        candidates.append({
            "source": "counterparty",
            "name": c["name"],
            "ctpty_id": c["id"],
            "score": score(raw, c["name"]),
        })

    for a in all_aliases():
        candidates.append({
            "source": "alias_raw",
            "name": a["raw_name"],
            "alias": a,
            "score": score(raw, a["raw_name"]),
        })
        candidates.append({
            "source": "alias_accepted",
            "name": a["accepted_name"],
            "alias": a,
            "score": score(raw, a["accepted_name"]),
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    top = candidates[:TOP_K]

    if top and top[0]["score"] >= AUTO_THRESHOLD:
        return {"status": "auto", "match": top[0], "score": top[0]["score"]}

    return {"status": "manual", "raw_name": raw, "candidates": top}


def autoMapAlias(raw_name: str, threshold: float = 0.9) -> str:
    if not raw_name:
        return raw_name

    res = resolve_readonly(raw_name)

    if res["status"] == "exact":
        m = res["match"]
        return m.get("name") or m.get("accepted_name")

    if res["status"] == "auto" and res["score"] >= threshold:
        m = res["match"]
        return m.get("name") or m.get("accepted_name")

    return raw_name

