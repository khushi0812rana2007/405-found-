<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rural Healthcare Chatbot</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f1f9f1;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    .chat-container {
      width: 350px;
      background: #fff;
      border-radius: 15px;
      box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .chat-header {
      background: #28a745;
      color: #fff;
      padding: 15px;
      text-align: center;
      font-weight: bold;
    }
    .chat-box {
      flex: 1;
      padding: 15px;
      overflow-y: auto;
      font-size: 14px;
    }
    .message {
      margin: 8px 0;
      padding: 10px;
      border-radius: 8px;
      max-width: 80%;
      clear: both;
    }
    .bot {
      background: #e8f5e9;
      float: left;
    }
    .user {
      background: #d4edda;
      float: right;
    }
    .chat-input {
      display: flex;
      border-top: 1px solid #ddd;
    }
    .chat-input input {
      flex: 1;
      border: none;
      padding: 12px;
      font-size: 14px;
      outline: none;
    }
    .chat-input button {
      background: #28a745;
      color: #fff;
      border: none;
      padding: 12px 15px;
      cursor: pointer;
    }
  </style>
</head>
<body>

<div class="chat-container">
  <div class="chat-header">Rural Healthcare Chatbot</div>
  <div class="chat-box" id="chat-box">
    <div class="message bot">👋 Namaste! I am your healthcare assistant. What health issue are you facing?</div>
  </div>
  <div class="chat-input">
    <input type="text" id="user-input" placeholder="Type your problem...">
    <button onclick="sendMessage()">Send</button>
  </div>
</div>

<script>
  const chatBox = document.getElementById("chat-box");

  function sendMessage() {
    let input = document.getElementById("user-input");
    let userText = input.value.trim();
    if (userText === "") return;

    appendMessage(userText, "user");
    input.value = "";

    setTimeout(() => {
      botReply(userText.toLowerCase());
    }, 800);
  }

  function appendMessage(text, sender) {
    let msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.innerText = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function botReply(userText) {
    let reply = "";

    if (userText.includes("fever")) {
      reply = "🌡️ It seems like you have a fever. Drink warm fluids, take rest. If high fever continues, please visit the nearest health center.";
    } else if (userText.includes("cough")) {
      reply = "🤧 For cough, drink warm water, avoid cold drinks, and inhale steam. If it lasts more than 7 days, consult a doctor.";
    } else if (userText.includes("headache")) {
      reply = "💊 For headache, drink enough water, rest in a quiet place. If pain is severe or frequent, seek medical advice.";
    } else if (userText.includes("injury") || userText.includes("cut")) {
      reply = "🩹 Clean the wound with clean water, apply antiseptic, and cover with a clean cloth. For deep cuts, go to the hospital.";
    } else if (userText.includes("thanks")) {
      reply = "🙏 You are welcome! Take care of your health.";
    } else {
      reply = "⚕️ I'm not sure about this problem. Please visit the nearest health worker or hospital for proper care.";
    }

    appendMessage(reply, "bot");
  }
</script>

</body>
</html>
