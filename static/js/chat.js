'use strict';

const form = document.querySelector('#chatForm');
const input = document.querySelector('#textInput');
const chat = document.querySelector('#chatMessages');
const sendButton = form.querySelector('button[type="submit"]');

function formatTime(date = new Date()) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function appendMessage(name, side, text) {
  const wrapper = document.createElement('div');
  wrapper.className = `msg ${side}-msg`;

  const image = document.createElement('div');
  image.className = 'msg-img';
  image.setAttribute('aria-hidden', 'true');

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  const info = document.createElement('div');
  info.className = 'msg-info';

  const infoName = document.createElement('div');
  infoName.className = 'msg-info-name';
  infoName.textContent = name;

  const infoTime = document.createElement('div');
  infoTime.className = 'msg-info-time';
  infoTime.textContent = formatTime();

  const message = document.createElement('div');
  message.className = 'msg-text';
  // textContent is intentional: never inject user/API text as HTML.
  message.textContent = text;

  info.append(infoName, infoTime);
  bubble.append(info, message);
  wrapper.append(image, bubble);
  chat.appendChild(wrapper);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage(message) {
  sendButton.disabled = true;

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    const data = await response.json().catch(() => ({}));

    if (response.status === 401) {
      window.location.href = '/login';
      return;
    }

    if (!response.ok) {
      throw new Error(data.error || 'Unable to get a response.');
    }

    appendMessage('Legal Bot', 'left', data.answer);
  } catch (error) {
    appendMessage('System', 'left', error.message);
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  appendMessage('You', 'right', message);
  input.value = '';
  sendMessage(message);
});
