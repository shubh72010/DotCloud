const sendBtn = document.getElementById("send-btn");
const chatMessages = document.getElementById("chat-messages");
const typingIndicator = document.getElementById("typing-indicator");
const promptInput = document.getElementById("prompt");
const apiKeyInput = document.getElementById("api-key");
const modelSelect = document.getElementById("model");

function appendMessage(message, sender) {
  const div = document.createElement("div");
  div.className = sender === "user" ? "message user" : "message bot";
  div.textContent = message;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendPrompt() {
  const prompt = promptInput.value.trim();
  const apiKey = apiKeyInput.value.trim();
  const model = modelSelect.value;

  if (!prompt || !apiKey) return;

  appendMessage(prompt, "user");
  promptInput.value = "";

  typingIndicator.style.display = "block";

  try {
    const response = await fetch("https://your-render-app.onrender.com/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, apiKey, model })
    });
    const data = await response.json();
    appendMessage(data.output || JSON.stringify(data), "bot");
  } catch (err) {
    appendMessage("Error: " + err.message, "bot");
  } finally {
    typingIndicator.style.display = "none";
  }
}

sendBtn.addEventListener("click", sendPrompt);
promptInput.addEventListener("keydown", e => {
  if (e.key === "Enter") sendPrompt();
});