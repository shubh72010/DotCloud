const runBtn = document.getElementById('runBtn');
const chatBox = document.getElementById('chatBox');

runBtn.addEventListener('click', async () => {
    const apiKey = document.getElementById('apiKey').value.trim();
    const model = document.getElementById('model').value;
    const userInput = document.getElementById('userInput').value.trim();

    if(!apiKey || !userInput) return alert("Please enter your API key and prompt!");

    appendMessage("You", userInput);

    try {
        const response = await fetch(`https://openrouter.ai/api/v1/${model}/generate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
            },
            body: JSON.stringify({ input: userInput })
        });

        if(!response.ok) throw new Error("Failed to fetch AI response.");

        const data = await response.json();
        appendMessage("AI", data.output || "No response received.");

    } catch(err) {
        appendMessage("Error", err.message);
    }

    document.getElementById('userInput').value = "";
});

function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}