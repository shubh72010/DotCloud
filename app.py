from flask import Flask, request, Response, render_template_string
import requests
import json
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
pre { background: #f4f4f4; padding: 10px; white-space: pre-wrap; }
</style>
</head>
<body>
<h1>DotCloud AI</h1>
<input type="text" id="apiKey" placeholder="Enter your OpenRouter API key">
<input type="text" id="model" placeholder="Enter model (e.g., meta-llama/llama-3.3-8b-instruct:free)">
<textarea id="prompt" placeholder="Enter your prompt..."></textarea>
<button id="sendBtn">Send</button>

<h3>Response:</h3>
<pre id="response"></pre>

<script>
const sendBtn = document.getElementById('sendBtn');
const responseBox = document.getElementById('response');

sendBtn.addEventListener('click', () => {
    const prompt = document.getElementById('prompt').value;
    const model = document.getElementById('model').value;
    const apiKey = document.getElementById('apiKey').value;

    if (!prompt || !model || !apiKey) {
        alert('Please fill in all fields!');
        return;
    }

    responseBox.textContent = "";
    const eventSource = new EventSource(`/stream?prompt=${encodeURIComponent(prompt)}&model=${encodeURIComponent(model)}&apiKey=${encodeURIComponent(apiKey)}`);

    eventSource.onmessage = (e) => {
        responseBox.textContent += e.data;
    };

    eventSource.onerror = (e) => {
        responseBox.textContent += "\\n[Error streaming response]";
        eventSource.close();
    };
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/stream')
def stream():
    prompt = request.args.get("prompt")
    model = request.args.get("model")
    api_key = request.args.get("apiKey")

    if not prompt or not model or not api_key:
        return "Missing parameters", 400

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    def event_stream():
        with requests.post(url, headers=headers, json=body, stream=True, timeout=60) as r:
            for line in r.iter_lines():
                if line:
                    try:
                        decoded = line.decode('utf-8')
                        if decoded.startswith("data: "):
                            decoded = decoded[6:]
                        if decoded == "[DONE]":
                            break
                        obj = json.loads(decoded)
                        content = obj.get("choices", [{}])[0].get("delta", {}).get("content")
                        if content:
                            yield f"data: {content}\n\n"
                    except Exception:
                        continue

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)