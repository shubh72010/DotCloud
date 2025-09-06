from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DotCloud AI</title>
<style>
body { font-family: Arial, sans-serif; margin: 20px; }
input, textarea { width: 100%; margin: 5px 0; padding: 8px; }
button { padding: 10px 20px; margin: 5px 0; cursor: pointer; }
pre { background: #f4f4f4; padding: 10px; }
</style>
</head>
<body>
<h1>DotCloud AI</h1>
<div>
    <input type="text" id="apiKey" placeholder="Enter your OpenRouter API key">
</div>
<div>
    <input type="text" id="model" placeholder="Enter model (e.g., meta-llama/llama-3.3-8b-instruct:free)">
</div>
<div>
    <textarea id="prompt" placeholder="Enter your prompt..."></textarea>
</div>
<button id="sendBtn">Send</button>

<h3>Response:</h3>
<pre id="response"></pre>

<script>
const sendBtn = document.getElementById('sendBtn');
const responseBox = document.getElementById('response');

sendBtn.addEventListener('click', async () => {
    const prompt = document.getElementById('prompt').value;
    const model = document.getElementById('model').value;
    const apiKey = document.getElementById('apiKey').value;

    if (!prompt || !model || !apiKey) {
        alert('Please fill in all fields!');
        return;
    }

    responseBox.textContent = "Loading...";

    try {
        const res = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, model, apiKey })
        });

        const data = await res.json();

        if (data.error) {
            responseBox.textContent = "Error: " + data.error;
        } else {
            const message = data.choices?.[0]?.message?.content || JSON.stringify(data, null, 2);
            responseBox.textContent = message;
        }
    } catch (err) {
        responseBox.textContent = "Error: " + err.message;
    }
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt')
    model = data.get('model')
    api_key = data.get('apiKey')

    if not prompt or not model or not api_key:
        return jsonify({"error": "Missing prompt, model, or API key"}), 400

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)