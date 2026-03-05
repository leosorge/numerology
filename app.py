import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from logic import calculate_numerology
from data import arr_vocs, arr_cons, arr_tots, arr_data

app = Flask(__name__)

# Configure Gemini AI
# The user should provide an API key in the environment or directly here.
model_cache = {}

def rewrite_text(text, api_key):
    """Rewrites the text using Gemini AI as requested."""
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return text.replace("/n", "\n")
        
    try:
        # Reconfigure if key changed or not set
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
        
        prompt = f"riscrivi questo testo, senza modificarne il significato, in un numero simile di battute. Mantieni i ritorni a capo se presenti: {text.replace('/n', '\n')}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return text.replace("/n", "\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    name = data.get('name', '')
    surname = data.get('surname', '')
    birthdate = data.get('birthdate', '')
    api_key = data.get('apikey', '')
    
    if not name or not surname or not birthdate:
        return jsonify({"error": "Missing fields"}), 400
    
    results = calculate_numerology(name, surname, birthdate)
    
    def get_text(arr, val):
        idx = (val - 1) % len(arr)
        return arr[idx]

    # Get original texts
    t_cons = get_text(arr_cons, results['output_cons'])
    t_vocs = get_text(arr_vocs, results['output_vocs'])
    t_tots = get_text(arr_tots, results['output_tots'])
    t_data = get_text(arr_data, results['output_data'])

    # Rewrite texts using Gemini
    response = {
        "output_cons": results['output_cons'],
        "output_vocs": results['output_vocs'],
        "output_tots": results['output_tots'],
        "output_data": results['output_data'],
        "text_cons": rewrite_text(t_cons, api_key),
        "text_vocs": rewrite_text(t_vocs, api_key),
        "text_tots": rewrite_text(t_tots, api_key),
        "text_data": rewrite_text(t_data, api_key)
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
