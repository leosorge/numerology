# NUMMY

# Versione ancora con la parte API di AI non inserita

import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

import streamlit as st
from logic import calculate_numerology
from data import arr_vocs, arr_cons, arr_tots, arr_data
import google.generativeai as genai

# ---------------------------
# 1. REWRITE TEXT
# ---------------------------
def rewrite_text(text, api_key):
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return text.replace("/n", "\n")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-8b')

        prompt = f"riscrivi questo testo senza cambiarne il significato:\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return text

# 2. CACHE BY CHATGPT

@lru_cache(maxsize=128)
def rewrite_text_cached(text, api_key):
    return rewrite_text(text, api_key)

# ---------------------------
# 3. Core logic (ex /calculate)
# ---------------------------
def calculate_api(name, surname, birthdate, api_key):
    results = calculate_numerology(name, surname, birthdate)

    def get_text(arr, val):
        idx = (val - 1) % len(arr)
        return arr[idx]

    t_cons = get_text(arr_cons, results['output_cons'])
    t_vocs = get_text(arr_vocs, results['output_vocs'])
    t_tots = get_text(arr_tots, results['output_tots'])
    t_data = get_text(arr_data, results['output_data'])

    return {
        "output_cons": results['output_cons'],
        "output_vocs": results['output_vocs'],
        "output_tots": results['output_tots'],
        "output_data": results['output_data'],
        "text_cons": rewrite_text_cached(t_cons, api_key),
        "text_vocs": rewrite_text_cached(t_vocs, api_key),
        "text_tots": rewrite_text_cached(t_tots, api_key),
        "text_data": rewrite_text_cached(t_data, api_key)
    }

# 4 PARSER

def parse_txt(file_content):
    people = []
    blocks = re.split(r"=+\n", file_content)

    for i, block in enumerate(blocks):
        lines = [l.strip() for l in block.split("\n") if l.strip()]

        if len(lines) < 3:
            continue

        name, surname, birthdate = lines[:3]

        people.append({
            "name": name,
            "surname": surname,
            "birthdate": birthdate,
            "row": i + 1
        })

    return people

# 5. VALIDATION

def validate_person(p):
    errors = []

    if not p["name"].isalpha():
        errors.append("Nome non valido")

    if not p["surname"].isalpha():
        errors.append("Cognome non valido")

    try:
        datetime.strptime(p["birthdate"], "%d/%m/%Y")
    except:
        errors.append("Data non valida (gg/mm/aaaa)")

    return errors

# 6. EXPORT

def generate_txt(results, people):
    lines = []

    for p, r in zip(people, results):
        lines.append("==============================")
        lines.append(f"{p['name']} {p['surname']} ({p['birthdate']})")

        if "error" in r:
            lines.append(f"ERRORE: {r['error']}")
            continue

        lines.append(f"CONS: {r['output_cons']}")
        lines.append(f"VOCS: {r['output_vocs']}")
        lines.append(f"TOTS: {r['output_tots']}")
        lines.append(f"DATA: {r['output_data']}")

        lines.append(r["text_cons"])
        lines.append(r["text_vocs"])
        lines.append(r["text_tots"])
        lines.append(r["text_data"])

    return "\n".join(lines)
# ---------------------------
# 7. UI Streamlit
# ---------------------------
st.title("🔢 Numerologia")

name = st.text_input("Nome")
surname = st.text_input("Cognome")
birthdate = st.text_input("Data di nascita (gg/mm/aaaa)")
api_key = st.text_input("Gemini API Key (opzionale)", type="password")

if st.button("Calcola"):
    if not name or not surname or not birthdate:
        st.error("Compila tutti i campi")
    else:
        result = calculate_api(name, surname, birthdate, api_key)

        st.subheader("Risultati numerici")
        st.json({
            "Consonanti": result["output_cons"],
            "Vocali": result["output_vocs"],
            "Totale": result["output_tots"],
            "Data": result["output_data"],
        })

        st.subheader("Interpretazione")
        st.write("**Consonanti:**", result["text_cons"])
        st.write("**Vocali:**", result["text_vocs"])
        st.write("**Totale:**", result["text_tots"])
        st.write("**Data:**", result["text_data"])

st.divider()
st.header("📂 Elaborazione multipla da file")

uploaded_file = st.file_uploader("Carica file TXT", type="txt")

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    people = parse_txt(content)

    st.info(f"Trovati {len(people)} profili")

    valid_people = []
    errors_list = []

    for p in people:
        errs = validate_person(p)
        if errs:
            errors_list.append((p, errs))
        else:
            valid_people.append(p)

    if errors_list:
        st.warning("⚠️ Record non validi:")
        for p, errs in errors_list:
            st.write(f"{p} → {errs}")

    if st.button("🚀 Calcola da file"):
        progress = st.progress(0)
        status = st.empty()

        results = []
        total = len(valid_people)

        if total == 0:
            st.error("Nessun record valido")
        else:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(
                        calculate_api,
                        p["name"],
                        p["surname"],
                        p["birthdate"],
                        api_key
                    )
                    for p in valid_people
                ]

                for i, future in enumerate(as_completed(futures)):
                    try:
                        res = future.result()
                        results.append(res)
                    except Exception as e:
                        results.append({"error": str(e)})

                    progress.progress((i + 1) / total)
                    status.text(f"Elaborati {i+1}/{total}")

            st.success("✅ Completato!")

            # DOWNLOAD
            txt_output = generate_txt(results, valid_people)

            st.download_button(
                "📥 Scarica risultati TXT",
                txt_output,
                file_name="numerologia_results.txt",
                mime="text/plain"
            )
