import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result.html')
def result():
    return render_template('result.html')

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    if not client:
        return jsonify({"error": "Gemini API key is not configured on server."}), 500

    data = request.json or {}
    device_type = data.get('device_type', 'Desktop')
    cpu = data.get('cpu', 'Unknown CPU')
    ram = data.get('ram', '8 GB')
    storage = data.get('storage', 'SSD')
    gpu = data.get('gpu', 'Integrated GPU')
    category = data.get('category', 'Gaming')

    prompt = f"""
    Acts as a PC Specs Expert. 
    Analyze this hardware system:
    - Type: {device_type}
    - CPU: {cpu}
    - RAM: {ram}
    - Storage: {storage}
    - GPU: {gpu}

    Provide recommendations for {category} workload based on these specs.
    List compatible games/software and performance expectations.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return jsonify({"recommendations": response.text})
    except Exception as e:
        return jsonify({"error": f"AI Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)