"""
app.py — NUMMY · Numerologia Streamlit
Bug corretti rispetto alla versione precedente:
  1. results salvato in session_state → sopravvive ai rerender
  2. generate_txt unica e corretta (legge dict, non stringa)
  3. download button nel posto giusto (dopo il calcolo)
  4. stampa risultati condizionata alla presenza di dati
  5. lru_cache rimossa per api_key (cache globale incompatibile con chiavi per-utente)
  6. seconda define di generate_txt rimossa
"""

import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64

import streamlit as st
from logic import calculate_numerology
from data import arr_vocs, arr_cons, arr_tots, arr_data
from llm_client import render_provider_selector, generate, active_provider_name

# ── Favicon via base64 ────────────────────────────────────────────────────────
def _favicon_b64() -> str:
    try:
        with open("favicon_nummy.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

_fav = _favicon_b64()
if _fav:
    st.markdown(
        f'<link rel="icon" type="image/png" href="data:image/png;base64,{_fav}">',
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="NUMMY · Numerologia",
    page_icon="favicon_nummy.png",
    layout="centered",
)

render_provider_selector()

# ── 1. REWRITE TEXT ───────────────────────────────────────────────────────────

def rewrite_text(text: str) -> str:
    try:
        return generate(
            prompt=f"riscrivi questo testo senza cambiarne il significato:\n{text}",
            max_tokens=1024,
            temperature=0.3,
        )
    except Exception:
        return text.replace("/n", "\n")


# ── 2. CORE LOGIC ─────────────────────────────────────────────────────────────

def calculate_api(name: str, surname: str, birthdate: str) -> dict:
    results = calculate_numerology(name, surname, birthdate)

    def get_text(arr, val):
        return arr[(val - 1) % len(arr)]

    return {
        "name":       name,
        "surname":    surname,
        "birthdate":  birthdate,
        "output_cons": results["output_cons"],
        "output_vocs": results["output_vocs"],
        "output_tots": results["output_tots"],
        "output_data": results["output_data"],
        "text_cons":   rewrite_text(get_text(arr_cons, results["output_cons"])),
        "text_vocs":   rewrite_text(get_text(arr_vocs, results["output_vocs"])),
        "text_tots":   rewrite_text(get_text(arr_tots, results["output_tots"])),
        "text_data":   rewrite_text(get_text(arr_data, results["output_data"])),
    }


# ── 3. PARSER ─────────────────────────────────────────────────────────────────

def parse_txt(file_content: str) -> list[dict]:
    people = []
    blocks = re.split(r"=+[\r\t ]*\n", file_content)
    for i, block in enumerate(blocks):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) < 3:
            continue
        people.append({
            "name":      lines[0],
            "surname":   lines[1],
            "birthdate": lines[2],
            "row":       i + 1,
        })
    return people


# ── 4. VALIDATION ─────────────────────────────────────────────────────────────

def validate_person(p: dict) -> list[str]:
    errors = []
    if not p["name"].isalpha():
        errors.append("Nome non valido")
    if not p["surname"].isalpha():
        errors.append("Cognome non valido")
    try:
        datetime.strptime(p["birthdate"], "%d/%m/%Y")
    except Exception:
        errors.append("Data non valida (gg/mm/aaaa)")
    return errors


# ── 5. EXPORT TXT ─────────────────────────────────────────────────────────────

def generate_txt(results: list[dict]) -> str:
    """Genera il testo scaricabile da una lista di dict risultato."""
    lines = []
    for r in results:
        lines.append("==============================")
        lines.append(f"{r['name']} {r['surname']} ({r['birthdate']})")
        if "error" in r:
            lines.append(f"ERRORE: {r['error']}")
            continue
        lines.append(f"CONS: {r['output_cons']}")
        lines.append(f"VOCS: {r['output_vocs']}")
        lines.append(f"TOTS: {r['output_tots']}")
        lines.append(f"DATA: {r['output_data']}")
        lines.append("")
        lines.append(r["text_cons"])
        lines.append(r["text_vocs"])
        lines.append(r["text_tots"])
        lines.append(r["text_data"])
        lines.append("")
    return "\n".join(lines)


# ── 6. HELPER: mostra un singolo risultato ────────────────────────────────────

def show_result(r: dict):
    if "error" in r:
        st.error(f"Errore: {r['error']}")
        return
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Consonanti", r["output_cons"])
    col2.metric("Vocali",     r["output_vocs"])
    col3.metric("Totale",     r["output_tots"])
    col4.metric("Data",       r["output_data"])
    st.markdown("**Consonanti:** " + r["text_cons"])
    st.markdown("**Vocali:** "     + r["text_vocs"])
    st.markdown("**Totale:** "     + r["text_tots"])
    st.markdown("**Data:** "       + r["text_data"])


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

st.title("🔢 NUMMY · Numerologia")

st.divider()

# ── SEZIONE SINGOLA ───────────────────────────────────────────────────────────

st.header("👤 Calcolo singolo")

c1, c2, c3 = st.columns(3)
with c1: name      = st.text_input("Nome")
with c2: surname   = st.text_input("Cognome")
with c3: birthdate = st.text_input("Data di nascita (gg/mm/aaaa)")

if st.button("Calcola", type="primary"):
    if not name or not surname or not birthdate:
        st.error("Compila tutti i campi.")
    else:
        with st.spinner("Calcolo in corso…"):
            r = calculate_api(name.strip(), surname.strip(), birthdate.strip())
        st.session_state["singolo"] = r

# Mostra risultato singolo se presente
if "singolo" in st.session_state:
    st.subheader(f"Risultato — {st.session_state['singolo']['name']} {st.session_state['singolo']['surname']}")
    show_result(st.session_state["singolo"])
    txt = generate_txt([st.session_state["singolo"]])
    st.download_button(
        "📥 Scarica risultato .txt",
        data=txt,
        file_name=f"nummy_{name}_{surname}.txt",
        mime="text/plain",
        key="dl_singolo",
    )

st.divider()

# ── SEZIONE MULTIPLA ──────────────────────────────────────────────────────────

st.header("📂 Elaborazione multipla da file")

st.markdown("""
**Formato file TXT atteso** — ogni persona separata da una riga di `=`:
```
==============================
Mario
Rossi
15/03/1980
==============================
Laura
Bianchi
22/07/1995
==============================
```
""")

uploaded_file = st.file_uploader("Carica file TXT", type="txt")

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    people  = parse_txt(content)

    st.info(f"Trovati {len(people)} profili nel file.")

    valid_people  = []
    errors_list   = []

    for p in people:
        errs = validate_person(p)
        if errs:
            errors_list.append((p, errs))
        else:
            valid_people.append(p)

    if errors_list:
        st.warning("⚠️ Record non validi (ignorati):")
        for p, errs in errors_list:
            st.write(f"  • {p['name']} {p['surname']} — {', '.join(errs)}")

    if valid_people:
        if st.button("🚀 Calcola tutti", type="primary", key="btn_multi"):
            progress = st.progress(0)
            status   = st.empty()
            results  = []
            total    = len(valid_people)

            # Legge il provider nel thread principale prima di lanciare i worker
            # (st.session_state non è thread-safe nei worker Streamlit)
            _ = active_provider_name()

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(
                        calculate_api,
                        p["name"], p["surname"], p["birthdate"]
                    ): p
                    for p in valid_people
                }
                for i, future in enumerate(as_completed(futures)):
                    try:
                        results.append(future.result())
                    except Exception as e:
                        p = futures[future]
                        results.append({
                            "name": p["name"], "surname": p["surname"],
                            "birthdate": p["birthdate"], "error": str(e),
                        })
                    progress.progress((i + 1) / total)
                    status.text(f"Elaborati {i + 1}/{total}…")

            status.text("✅ Completato!")
            # Salva in session_state per sopravvivere ai rerender
            st.session_state["multi_results"] = results
            st.session_state["multi_people"]  = valid_people

# Mostra risultati multipli se presenti (anche dopo rerender da download button)
if "multi_results" in st.session_state:
    results = st.session_state["multi_results"]
    st.subheader(f"Risultati — {len(results)} profili")

    for r in results:
        with st.expander(
            f"{'❌' if 'error' in r else '✅'}  {r['name']} {r['surname']}  ({r['birthdate']})",
            expanded=False,
        ):
            show_result(r)

    # Download
    txt_multi = generate_txt(results)
    st.download_button(
        "📥 Scarica tutti i risultati .txt",
        data=txt_multi,
        file_name="nummy_risultati.txt",
        mime="text/plain",
        key="dl_multi",
    )
