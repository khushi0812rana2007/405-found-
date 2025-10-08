const form = document.getElementById('chat-form').value;
const input = document.getElementById('input-msg');
const messages = document.getElementById('messages');


function addMessage(text, who='bot'){
const li = document.createElement('li');
li.className = 'msg ' + (who === 'user' ? 'user' : 'bot');
li.textContent = text;
messages.appendChild(li);
messages.scrollTop = messages.scrollHeight;
}


async function sendMessage(msg){
addMessage(msg, 'user');
try{
const res = await fetch('/api/chat', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ message: msg })
});
const data = await res.json();
if(data.reply) addMessage(data.reply, 'bot');
else addMessage('No reply from server', 'bot');
}catch(e){
console.error(e);
addMessage('Connection error. Try again later.', 'bot');
}
}


form.addEventListener('submit', e=>{
e.preventDefault();
const text = input.value.trim();
if(!text) return;
sendMessage(text);
input.value = '';
});


// Quick welcome message
addMessage('Hello — I can help with common symptoms, first aid steps, and local clinic info. Try: "I have fever" or "nearest clinic".');
document.getElementById('emergency-btn').addEventListener('click', () => {
  alert('🚨 Connecting you to emergency services...');
  // You can later integrate location or a helpline API here
});

document.getElementById('language-select').addEventListener('change', (event) => {
  const lang = event.target.value;
  alert(`Language changed to: ${event.target.options[event.target.selectedIndex].text}`);
  // You can add translation logic here later
});
