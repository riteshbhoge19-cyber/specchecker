import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# .env फाईल लोड करा
load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY is not set in Environment Variables!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result.html')
@app.route('/result')
def result_page():
    return render_template('result.html')

@app.route('/analyze', methods=['POST'])
@app.route('/api/recommendations', methods=['GET', 'POST'])
def get_recommendations():
    try:
        current_key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
        if not current_key:
            return jsonify({"error": "GEMINI_API_KEY is missing on server."}), 500

        genai.configure(api_key=current_key)

        data = request.get_json(force=True, silent=True) or request.args or request.form or {}

        device_type = data.get('device_type', 'Desktop')
        cpu = data.get('specific_cpu') or data.get('cpu') or 'Intel Core i3'
        ram = data.get('ram_spec') or data.get('ram') or '8 GB'
        storage = data.get('storage_type') or data.get('storage') or 'SSD'
        gpu = data.get('gpu_type') or data.get('gpu_category') or 'Integrated GPU'
        category = data.get('category', 'Gaming')

        prompt = f"""
You are a PC Hardware Expert.

System Specifications:
- Device Type: {device_type}
- CPU: {cpu}
- RAM: {ram}
- Storage: {storage}
- GPU: {gpu}

Task: Provide ONLY the names of TOP 20 best compatible apps/games for "{category}" on this hardware.

CRITICAL FORMATTING INSTRUCTIONS:
1. Do NOT write any introduction, summary, FPS, settings, or explanation.
2. Output ONLY a clean numbered list from 1 to 20.
3. Every item MUST be on its own NEW LINE.
4. Format strictly as:
1. **[Name of Game/Software]**
2. **[Name of Game/Software]**

Provide exactly 20 titles and nothing else.
"""

        try:
            model = genai.GenerativeModel('gemini-3.6-flash')
            response = model.generate_content(prompt)
            return jsonify({"recommendations": response.text})
        except Exception as primary_err:
            print("Primary model error:", str(primary_err))
            model = genai.GenerativeModel('gemini-3.6-flash')
            response = model.generate_content(prompt)
            return jsonify({"recommendations": response.text})

    except Exception as e:
        print("Backend Error:", str(e))
        return jsonify({"error": f"AI Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)