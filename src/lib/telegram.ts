const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "";

const API_BASE = `https://api.telegram.org/bot${BOT_TOKEN}`;
const FILE_BASE = `https://api.telegram.org/file/bot${BOT_TOKEN}`;

export async function sendMessage(chatId: number | string, text: string, parseMode: string = "HTML") {
  const res = await fetch(`${API_BASE}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      parse_mode: parseMode,
      disable_web_page_preview: true,
    }),
  });
  return res.json();
}

export async function getFile(fileId: string) {
  const res = await fetch(`${API_BASE}/getFile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file_id: fileId }),
  });
  return res.json();
}

export function getFileUrl(filePath: string) {
  return `${FILE_BASE}/${filePath}`;
}

export async function setWebhook(url: string) {
  const res = await fetch(`${API_BASE}/setWebhook`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return res.json();
}

export async function deleteWebhook() {
  const res = await fetch(`${API_BASE}/deleteWebhook`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  return res.json();
}

export async function getWebhookInfo() {
  const res = await fetch(`${API_BASE}/getWebhookInfo`);
  return res.json();
}

export function getBotToken() {
  return BOT_TOKEN;
}
