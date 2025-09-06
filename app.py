from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/tos")
def tos():
    return render_template("tos.html")

@app.route("/api/run", methods=["POST"])
def run_ai():
    data = request.json
    api_key = data.get("apiKey")
    model = data.get("model")
    prompt = data.get("prompt")

    if not api_key or not model or not prompt:
        return jsonify({"error":"Missing fields"}),400

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"input": prompt}

    try:
        response = requests.post(f"https://openrouter.ai/api/v1/{model}/generate", headers=headers, json=payload)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}),500

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)