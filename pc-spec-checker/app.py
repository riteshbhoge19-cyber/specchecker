import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Fetch API Key
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result.html')
def result():
    return render_template('result.html')

@app.route('/analyze', methods=['POST'])
@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    # Dynamic Key check for environment changes
    current_key = os.getenv("GEMINI_API_KEY") or API_KEY
    if not current_key:
        return jsonify({"error": "GEMINI_API_KEY is missing on server."}), 500

    genai.configure(api_key=current_key)

    # Accept both JSON payload and Form Data
    data = request.get_json(force=True, silent=True) or request.form or {}

    device_type = data.get('device_type', 'Desktop')
    cpu = data.get('specific_cpu') or data.get('cpu', 'Unknown CPU')
    ram = data.get('ram_spec') or data.get('ram', '8 GB')
    storage = data.get('storage_type') or data.get('storage', 'SSD')
    gpu = data.get('gpu_category') or data.get('gpu', 'Integrated GPU')
    category = data.get('category', 'Gaming')

    prompt = f"""
    Act as a PC Hardware Expert. 
    Analyze this system setup:
    - Device Type: {device_type}
    - CPU: {cpu}
    - RAM: {ram}
    - Storage: {storage}
    - GPU: {gpu}

    Provide recommendations for {category} workload based on these specs.
    List compatible games/software and expected performance.
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return jsonify({"recommendations": response.text})
    except Exception as e:
        print("API Failure Trace:", str(e))
        return jsonify({"error": f"AI Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)