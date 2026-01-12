from threading import Lock
from typing import List, Dict
from project_gamma.src.gamma.alias_engine.db import get_conn

_MASTER = []
_LOADED = False
_LOCK = Lock()

def load_master():
    global _LOADED
    if _LOADED:
        return

    with _LOCK:
        if _LOADED:
            return

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, type, tenant_id
                    FROM public.counterparties
                    WHERE active = true
                """)
                for cid, name, ctype, tid in cur.fetchall():
                    _MASTER.append({
                        "kind": "counterparty",
                        "id": cid,
                        "name": name or "",
                        "ctype": ctype,
                        "tenant_id": tid,
                    })
        finally:
            conn.close()

        _LOADED = True

def all_counterparties() -> List[Dict]:
    load_master()
    return _MASTER
