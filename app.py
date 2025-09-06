from flask import Flask, request, render_template_string, jsonify
import requests
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DotCloud AI Chat</title>
<style>
body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f0f0f0; }
#chat-container { max-width: 600px; margin: 50px auto; background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
#messages { max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
.message { margin: 5px 0; }
.user { text-align: right; color: white; background: #4a90e2; padding: 5px 10px; border-radius: 5px; display: inline-block; }
.ai { text-align: left; color: black; background: #eee; padding: 5px 10px; border-radius: 5px; display: inline-block; }
input, button { padding: 10px; margin: 5px 0; width: 100%; }
</style>
</head>
<body>
<div id="chat-container">
    <h2>DotCloud AI Chat</h2>
    <input type="text" id="apiKey" placeholder="Enter your OpenRouter API key">
    <input type="text" id="model" placeholder="Enter model (e.g., meta-llama/llama-3.3-8b-instruct:free)">
    <div id="messages"></div>
    <input type="text" id="prompt" placeholder="Enter your message...">
    <button id="sendBtn">Send</button>
</div>

<script>
let messages = [];

function renderMessages() {
    const container = document.getElementById('messages');
    container.innerHTML = '';
    messages.forEach(msg => {
        const div = document.createElement('div');
        div.className = 'message ' + (msg.role === 'user' ? 'user' : 'ai');
        div.textContent = msg.content;
        container.appendChild(div);
    });
    container.scrollTop = container.scrollHeight;
}

document.getElementById('sendBtn').addEventListener('click', async () => {
    const prompt = document.getElementById('prompt').value;
    const model = document.getElementById('model').value;
    const apiKey = document.getElementById('apiKey').value;

    if (!prompt || !model || !apiKey) {
        alert('Fill all fields!');
        return;
    }

    messages.push({role: 'user', content: prompt});
    renderMessages();

    const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt, model, apiKey, history: messages})
    });
    const data = await res.json();
    messages.push({role: 'ai', content: data.response});
    renderMessages();
    document.getElementById('prompt').value = '';
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('prompt')
    model = data.get('model')
    api_key = data.get('apiKey')
    history = data.get('history', [])

    if not prompt or not model or not api_key:
        return jsonify({'response': 'Missing parameters'}), 400

    messages_payload = [{'role': m['role'], 'content': m['content']} for m in history]

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": model, "messages": messages_payload}

    try:
        r = requests.post(url, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        response_json = r.json()
        ai_content = response_json['choices'][0]['message']['content']
        return jsonify({'response': ai_content})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)