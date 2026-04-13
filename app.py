# NUMMY

import streamlit as st
from logic import calculate_numerology
from data import arr_vocs, arr_cons, arr_tots, arr_data
import google.generativeai as genai

# ---------------------------
# Gemini rewrite
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


# ---------------------------
# Core logic (ex /calculate)
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
        "text_cons": rewrite_text(t_cons, api_key),
        "text_vocs": rewrite_text(t_vocs, api_key),
        "text_tots": rewrite_text(t_tots, api_key),
        "text_data": rewrite_text(t_data, api_key)
    }


# ---------------------------
# UI Streamlit
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
