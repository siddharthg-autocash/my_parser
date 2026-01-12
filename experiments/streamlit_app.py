import streamlit as st
import json, time
from typing import Dict, Any

from project_gamma.src.gamma.service.script import CTPTY
from project_gamma.src.gamma.alias_engine.resolve import resolve_one
from project_gamma.src.gamma.alias_engine.alias_store import insert_alias
from project_gamma.src.gamma.alias_engine.db import get_conn

# CONSTANTS

# MUST exist in public.counterparties (tenant_id = 1)
UNRESOLVED_CTPY_ID = "00000000-0000-0000-0000-000000000001"

# Page config
st.set_page_config(
    page_title="Alias CTPTY — Interactive Resolver",
    layout="wide",
)

st.session_state.setdefault("parsed_result", None)
st.session_state.setdefault("format", None)



# Sidebar

with st.sidebar:
    st.header("Settings")
    approver = st.text_input("Approver", "streamlit_user")



# Input

st.title("Alias CTPTY — Interactive Resolver")

col1, col2, col3, col4 = st.columns(4)
with col1:
    tenant_id_field = st.text_input("tenant_id")
with col2:
    bai_code_field = st.text_input("bai_code (optional)")
with col3:
    narrative_field = st.text_input("narrative")
with col4:
    amount_field = st.text_input("amount (optional)")

st.markdown("**OR**")

json_input = st.text_area(
    "Input JSON (fallback)",
    value='{"tenant_id":1,"bai_code":"","narrative":"","amount":null}',
    height=120,
)



# Resolve input fields

tenant_id = None
narrative = None
amount = None
bai_code = None

if tenant_id_field.strip():
    tenant_id = int(tenant_id_field)

if narrative_field.strip():
    narrative = narrative_field

if bai_code_field.strip():
    bai_code = bai_code_field.strip()

if amount_field.strip():
    try:
        amount = float(amount_field)
    except Exception:
        pass

if tenant_id is None or narrative is None:
    try:
        j = json.loads(json_input)
        tenant_id = tenant_id or j.get("tenant_id")
        narrative = narrative or j.get("narrative")
        bai_code = bai_code or j.get("bai_code")
        amount = amount if amount is not None else j.get("amount")
    except Exception:
        pass



# Parse & Extract

if st.button("Parse & Extract CTPTY"):
    if not narrative:
        st.error("Narrative is required")
        st.stop()

    with st.spinner("Parsing transaction..."):
        bar = st.progress(0)
        time.sleep(0.15)
        bar.progress(30)

        result, fmt = CTPTY(narrative, amount, bai_code)

        bar.progress(80)
        time.sleep(0.1)
        bar.progress(100)

    st.session_state.parsed_result = result
    st.session_state.format = fmt



# Display parsed output

if not st.session_state.parsed_result:
    st.stop()

result = st.session_state.parsed_result
fmt = st.session_state.format

st.success(f"Detected format: {fmt}")
st.json(result)

ctpty = result.get("ctpty", {})
payer_raw = ctpty.get("payer")
payee_raw = ctpty.get("payee")

st.subheader("Alias Resolution")



# Alias resolution block

def alias_block(label: str, raw: str, key: str) -> Dict[str, Any]:
    st.markdown(f"### {label}: `{raw}`")

    if not raw:
        st.info("No value extracted")
        return {"status": "empty"}

    res = resolve_one(raw.strip().upper(), tenant_id, approver)

    # exact / auto
    if res["status"] in ("exact", "auto"):
        match = res["match"]
        display_name = match.get("name") or match.get("accepted_name")
        st.success(f"Resolved → {display_name}")
        return res

    st.warning("Manual resolution required")

    #  TOP K DROPDOWN (RESTORED) 
    display_map = {}
    for i, c in enumerate(res["candidates"], 1):
        label = f"{i}. {c['name']} ({c['score']:.3f}) [{c['source']}]"
        display_map[label] = c

    choice = st.selectbox(
        "Choose mapping",
        ["— Enter manually —"] + list(display_map.keys()),
        key=f"{key}_select",
    )

    manual_name = None
    action = None
    ctype = None
    chosen = None

    if choice == "— Enter manually —":
        manual_name = st.text_input("Canonical name", key=f"{key}_manual")

        action = st.radio(
            "Manual action",
            ["Add as alias", "Add as counterparty"],
            key=f"{key}_action",
        )

        if action == "Add as counterparty":
            ctype = st.selectbox(
                "Counterparty type",
                ["vendor", "customer"],
                key=f"{key}_ctype",
            )
    else:
        chosen = display_map[choice]

    return {
        "status": "manual",
        "raw": raw,
        "choice": chosen,
        "manual_name": manual_name,
        "action": action,
        "ctype": ctype,
    }


payer_res = alias_block("payer / customer", payer_raw, "payer")
payee_res = alias_block("payee / vendor", payee_raw, "payee")



# Persist

if st.button("Persist & Finalize"):
    
    def persist(res: Dict[str, Any]):
        # exact / auto
        if res["status"] in ("exact", "auto"):
            m = res["match"]
            return m.get("name") or m.get("accepted_name")

        raw = res["raw"].strip().upper()

        #  determine accepted name 
        if res.get("choice"):
            accepted = res["choice"]["name"]
            ctpty_id = res["choice"]["ctpty_id"]

        else:
            accepted = (res.get("manual_name") or "").strip()
            if not accepted:
                return raw

            # add as alias 
            if res["action"] == "Add as alias":
                ctpty_id = UNRESOLVED_CTPY_ID

            # add as counterparty
            elif res["action"] == "Add as counterparty":
                ctype = res.get("ctype")
                if ctype not in ("customer", "vendor"):
                    st.error("Please select counterparty type")
                    st.stop()

                conn = get_conn()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT id
                            FROM public.counterparties
                            WHERE tenant_id = %s
                            AND lower(name) = lower(%s)
                            AND active = true
                            LIMIT 1
                            """,
                            (tenant_id, accepted),
                        )
                        row = cur.fetchone()

                        if row:
                            ctpty_id = row[0]
                        else:
                            cur.execute(
                                """
                                INSERT INTO public.counterparties
                                (id, name, type, tenant_id, active)
                                VALUES (gen_random_uuid(), %s, %s, %s, true)
                                RETURNING id
                                """,
                                (accepted, ctype, tenant_id),
                            )
                            ctpty_id = cur.fetchone()[0]

                        conn.commit()
                finally:
                    conn.close()

            else:
                return raw  
 
        insert_alias(
            raw_name=raw,
            accepted_name=accepted,
            ctpty_id=ctpty_id,
            tenant_id=tenant_id,
            approver=approver,
        )

        return accepted


    payer_final = persist(payer_res)
    payee_final = persist(payee_res)

    final = {
        "tenant_id": tenant_id,
        "format": fmt,
        "parsed": result.get("parsed"),
        "ctpty": {
            "payer": payer_final,
            "payee": payee_final,
            "amount": amount,
        },
    }

    st.success("Completed")
    st.json(final)


# Manual Alias Add (Standalone)

st.subheader("Add Alias Manually")

with st.expander("Add alias without parsing"):
    manual_raw = st.text_input("Raw name", key="manual_alias_raw")
    manual_accepted = st.text_input("Accepted name", key="manual_alias_acc")

    if st.button("Add Alias"):
        raw = manual_raw.strip().upper()
        accepted = manual_accepted.strip()

        if not raw or not accepted:
            st.error("Both raw name and accepted name are required")
            st.stop()

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # try resolving counterparty
                cur.execute("""
                    SELECT id
                    FROM public.counterparties
                    WHERE tenant_id = %s
                    AND lower(name) = lower(%s)
                    AND active = true
                    LIMIT 1
                """, (tenant_id, accepted))

                row = cur.fetchone()
                ctpty_id = row[0] if row else UNRESOLVED_CTPY_ID

            conn.commit()
        finally:
            conn.close()

        insert_alias(
            raw_name=raw,
            accepted_name=accepted,
            ctpty_id=ctpty_id,
            tenant_id=tenant_id,
            approver=approver,
        )

        st.success(
            f"Alias added: `{raw}` → `{accepted}` "
            f"({'resolved' if ctpty_id != UNRESOLVED_CTPY_ID else 'unresolved'})"
        )


# Manual Counterparty Add (Standalone)

st.subheader("Add Counterparty Manually")

with st.expander("Add counterparty without parsing"):
    cp_name = st.text_input("Counterparty name", key="manual_ctpty_name")
    cp_type = st.selectbox(
        "Counterparty type",
        ["vendor", "customer"],
        key="manual_ctpty_type",
    )

    if st.button("Add Counterparty"):
        name = (cp_name or "").strip()

        if not name:
            st.error("Counterparty name is required")
            st.stop()

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # check if counterparty already exists
                cur.execute("""
                    SELECT id
                    FROM public.counterparties
                    WHERE tenant_id = %s
                    AND lower(name) = lower(%s)
                    AND active = true
                    LIMIT 1
                """, (tenant_id, name))

                row = cur.fetchone()

                if row:
                    ctpty_id = row[0]
                    created = False
                else:
                    cur.execute("""
                        INSERT INTO public.counterparties
                        (id, name, type, tenant_id, active)
                        VALUES (gen_random_uuid(), %s, %s, %s, true)
                        RETURNING id
                    """, (name, cp_type, tenant_id))

                    ctpty_id = cur.fetchone()[0]
                    created = True

                conn.commit()
        finally:
            conn.close()

        insert_alias(
            raw_name=name.strip().upper(),
            accepted_name=name,
            ctpty_id=ctpty_id,
            tenant_id=tenant_id,
            approver=approver,
        )

        st.success(
            f"Counterparty {'created' if created else 'already exists'}: "
            f"`{name}` ({cp_type})"
        )
