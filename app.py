from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Serve index page
@app.route('/')
def index():
    return render_template('index.html')

# Generate AI response
@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    api_key = data.get('apiKey')
    model = data.get('model') or "meta-llama/llama-3.3-8b-instruct:free"

    if not prompt or not api_key:
        return jsonify({"error": "Missing prompt, API key, or model"}), 400

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # Optional for app recognition on OpenRouter
        "HTTP-Referer": request.host_url,
        "X-Title": "DotCloud AI"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use 0.0.0.0 for Render deployment
    app.run(host='0.0.0.0', port=5000, debug=True)