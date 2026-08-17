import os
import json
import time
from flask import Flask, render_template, request, jsonify
from google import genai
from dotenv import load_dotenv

# .env फाईलमधून API Key सुरक्षितपणे लोड करा
load_dotenv()

app = Flask(__name__)

# System किंवा .env Environment मधून API Key घ्या
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result.html')
def result():
    return render_template('result.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    device = request.form.get('device_type', 'desktop')
    brand = request.form.get('brand', 'intel')
    era = request.form.get('cpu_era', '2011-2016')
    specific_cpu = request.form.get('specific_cpu', 'Core i5-3470')
    ram_spec = request.form.get('ram_spec', 'DDR3 8GB')
    storage_type = request.form.get('storage_type', '2.5-inch SATA SSD')
    gpu_type = request.form.get('gpu_type', 'No Dedicated GPU (Integrated Only)')
    gpu_vram = request.form.get('gpu_vram', 'Shared System Memory')

    prompt = f"""
Act as an expert PC Hardware Analyst.
Analyze this exact custom system configuration:
- Device: {device}
- Processor: {brand.capitalize()} {specific_cpu} ({era})
- Memory: {ram_spec}
- Storage: {storage_type}
- Graphics Card: {gpu_type} ({gpu_vram})

Task:
Generate tailored recommendations specific to this EXACT hardware setup.
For EACH item in all categories, return an object containing "title" and its official website domain "domain" for fetching exact logos.

JSON Structure:
{{
    "processor_model": "{brand.capitalize()} {specific_cpu}",
    "specs_summary": "{ram_spec} | {storage_type} | {gpu_type}",
    "gaming": [
        {{"title": "Counter-Strike 2", "domain": "counter-strike.net"}},
        {{"title": "GTA V", "domain": "rockstargames.com"}}
    ],
    "video_editing": [
        {{"title": "Adobe Premiere Pro", "domain": "adobe.com"}}
    ],
    "photo_editing": [
        {{"title": "Adobe Photoshop", "domain": "adobe.com"}}
    ],
    "office_work": [
        {{"title": "Microsoft Word", "domain": "microsoft.com"}}
    ]
}}
Provide EXACT 20 items per category array with correct official domain names.
CRITICAL INSTRUCTION: Return ONLY a valid, raw JSON object matching the requested schema.
"""

    models_to_try = ['gemini-3.6-flash', 'gemini-1.5-flash']
    last_error = ""

    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={'response_mime_type': 'application/json'}
                )
                
                result_data = json.loads(response.text)
                return jsonify({"success": True, "data": result_data})

            except Exception as e:
                last_error = str(e)
                time.sleep(1)

    return jsonify({
        "success": False, 
        "error": f"AI Server is currently busy. Please try again. ({last_error})"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)