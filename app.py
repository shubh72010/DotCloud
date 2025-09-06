from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    api_key = data.get('apiKey')
    model = data.get('model') or "meta-llama/llama-3.3-8b-instruct:free"

    if not prompt or not api_key:
        return jsonify({"error": "Missing prompt or API key"}), 400

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    try:
        return jsonify(response.json())
    except Exception:
        return jsonify({"error": "Invalid response from OpenRouter"}), 500

if __name__ == '__main__':
    app.run(debug=True)