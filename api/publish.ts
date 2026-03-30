import type { VercelRequest, VercelResponse } from "@vercel/node";

const TELEGRAM_API = "https://api.telegram.org";
const MAX_MESSAGE_CHARS = 4096;

function splitTelegramChunks(text: string): string[] {
  if (text.length <= MAX_MESSAGE_CHARS) return [text];
  const parts: string[] = [];
  for (let i = 0; i < text.length; i += MAX_MESSAGE_CHARS) {
    parts.push(text.slice(i, i + MAX_MESSAGE_CHARS));
  }
  return parts;
}

export default async function handler(
  req: VercelRequest,
  res: VercelResponse,
): Promise<void> {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }

  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }

  const token = (process.env.TELEGRAM_BOT_TOKEN ?? process.env.BOT_TOKEN ?? "").trim();
  const chatId = (
    process.env.TELEGRAM_PUBLISH_CHAT_ID ??
    process.env.PUBLISH_CHAT_ID ??
    ""
  ).trim();
  const bearer = (process.env.PUBLISH_BEARER_TOKEN ?? "").trim();

  if (!token || !chatId || !bearer) {
    res.status(503).json({ error: "Publish is not configured on the server." });
    return;
  }

  const auth = req.headers.authorization ?? "";
  if (auth !== `Bearer ${bearer}`) {
    res.status(401).json({ error: "Unauthorized" });
    return;
  }

  let body: unknown;
  try {
    body = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
  } catch {
    res.status(400).json({ error: "Invalid JSON body" });
    return;
  }

  const text =
    typeof body === "object" &&
    body !== null &&
    typeof (body as { text?: unknown }).text === "string"
      ? (body as { text: string }).text
      : "";

  if (!text.trim()) {
    res.status(400).json({ error: "Missing or empty text" });
    return;
  }

  const chunks = splitTelegramChunks(text);
  for (const chunk of chunks) {
    const tgRes = await fetch(`${TELEGRAM_API}/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: chunk,
        disable_web_page_preview: true,
      }),
    });

    if (!tgRes.ok) {
      const detail = await tgRes.text();
      res.status(502).json({
        error: "Telegram API rejected the message.",
        detail: detail.slice(0, 500),
      });
      return;
    }
  }

  res.status(200).json({ ok: true, parts: chunks.length });
}
