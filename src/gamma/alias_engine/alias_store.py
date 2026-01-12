from threading import Lock
from typing import List, Dict, Optional
from project_gamma.src.gamma.alias_engine.db import get_conn
from project_gamma.src.gamma.util.util import normalize

_ALIASES: List[Dict] = []
_LOADED = False
_LOCK = Lock()


def load_aliases() -> None:
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
                    SELECT id, ctpty_id, raw_name, accepted_name, tenant_id
                    FROM public.counterparty_aliases
                    WHERE active = true
                """)
                for aid, cpid, raw, acc, tid in cur.fetchall():
                    _ALIASES.append({
                        "kind": "alias",
                        "id": aid,
                        "ctpty_id": cpid,   # can be NULL
                        "raw_name": raw or "",
                        "accepted_name": acc or "",
                        "tenant_id": tid,
                    })
        finally:
            conn.close()

        _LOADED = True


def all_aliases() -> List[Dict]:
    load_aliases()
    return _ALIASES


def insert_alias(raw_name: str,accepted_name: str,ctpty_id: str,tenant_id: int,approver: Optional[str] = None) -> None:
     
    if normalize(raw_name) == normalize(accepted_name): return 
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.counterparty_aliases
                (raw_name, accepted_name, ctpty_id, tenant_id, approved_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (raw_name, accepted_name, ctpty_id, tenant_id, approver))
            conn.commit()
    finally:
        conn.close()

    global _LOADED, _ALIASES
    _ALIASES.clear()
    _LOADED = False

