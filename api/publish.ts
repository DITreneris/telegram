import type { VercelRequest, VercelResponse } from "@vercel/node";

const TELEGRAM_API = "https://api.telegram.org";
const MAX_MESSAGE_CHARS = 4096;
/** Telegram Bot API: sendPhoto caption limit. */
const MAX_CAPTION_CHARS = 1024;
/** Bot API upload practical limit for photos (bytes). */
const MAX_PHOTO_BYTES = 10 * 1024 * 1024;
/** Decoded image max when sent as JSON base64 (Vercel ~4.5MB request body limit). */
const MAX_PHOTO_BASE64_BYTES = 3 * 1024 * 1024;

function splitTelegramChunks(text: string): string[] {
  if (text.length <= MAX_MESSAGE_CHARS) return [text];
  const parts: string[] = [];
  for (let i = 0; i < text.length; i += MAX_MESSAGE_CHARS) {
    parts.push(text.slice(i, i + MAX_MESSAGE_CHARS));
  }
  return parts;
}

/** Reject arbitrary URLs (SSRF-style abuse of our server → Telegram). Allow same public host as this request. */
function photoUrlAllowed(photoUrl: string, req: VercelRequest): boolean {
  let u: URL;
  try {
    u = new URL(photoUrl);
  } catch {
    return false;
  }
  const proto = u.protocol.toLowerCase();
  if (proto !== "https:") {
    if (proto !== "http:") return false;
    if (!/^(localhost|127\.0\.0\.1)$/i.test(u.hostname)) return false;
  }
  const forwarded = req.headers["x-forwarded-host"];
  const rawHost =
    typeof forwarded === "string"
      ? forwarded.split(",")[0]?.trim() ?? ""
      : typeof req.headers.host === "string"
        ? req.headers.host
        : "";
  if (!rawHost) return false;
  const allowedHost = rawHost.split(":")[0]?.toLowerCase() ?? "";
  return u.hostname.toLowerCase() === allowedHost;
}

function protectionBypassHeaders(): Record<string, string> {
  const secret = (
    process.env.VERCEL_AUTOMATION_BYPASS_SECRET ??
    process.env.PUBLISH_STATIC_BYPASS_SECRET ??
    ""
  ).trim();
  const h: Record<string, string> = { Accept: "image/*,*/*;q=0.8" };
  if (secret) {
    h["x-vercel-protection-bypass"] = secret;
  }
  return h;
}

async function sendPhotoBytesToTelegram(
  token: string,
  chatId: string,
  buf: Uint8Array,
  mime: string,
  filename: string,
  caption: string,
): Promise<{ ok: true } | { ok: false; detail: string }> {
  const form = new FormData();
  form.append("chat_id", chatId);
  const ab = new ArrayBuffer(buf.byteLength);
  new Uint8Array(ab).set(buf);
  form.append("photo", new Blob([ab], { type: mime }), filename);
  if (caption.length > 0) {
    form.append("caption", caption);
  }

  const tgPhoto = await fetch(`${TELEGRAM_API}/bot${token}/sendPhoto`, {
    method: "POST",
    body: form,
  });

  if (!tgPhoto.ok) {
    const detail = await tgPhoto.text();
    return { ok: false, detail: detail.slice(0, 500) };
  }
  return { ok: true };
}

/**
 * Fetch image from same deployment URL, then multipart to Telegram.
 * Uses Vercel deployment-protection bypass headers when env secret is set.
 */
async function sendPhotoMultipartFromUrl(
  token: string,
  chatId: string,
  photoUrl: string,
  caption: string,
): Promise<
  { ok: true } | { ok: false; phase: "fetch" | "telegram"; detail: string }
> {
  let imgRes: Response;
  try {
    imgRes = await fetch(photoUrl, {
      headers: protectionBypassHeaders(),
      redirect: "follow",
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { ok: false, phase: "fetch", detail: `Could not fetch image: ${msg}` };
  }

  if (!imgRes.ok) {
    const hint =
      imgRes.status === 401
        ? " If the site uses Vercel Deployment Protection, set VERCEL_AUTOMATION_BYPASS_SECRET (same value as in Vercel → Protection Bypass) or publish from the UI (small images are sent as base64)."
        : "";
    return {
      ok: false,
      phase: "fetch",
      detail: `Could not fetch image (HTTP ${imgRes.status}).${hint}`,
    };
  }

  const ctRaw = (imgRes.headers.get("content-type") ?? "").toLowerCase();
  if (ctRaw.includes("text/html")) {
    return {
      ok: false,
      phase: "fetch",
      detail:
        "Image URL returned HTML — static file missing or SPA caught the path; open the image URL in a new tab to verify.",
    };
  }

  const buf = new Uint8Array(await imgRes.arrayBuffer());
  if (buf.byteLength === 0) {
    return { ok: false, phase: "fetch", detail: "Image URL returned an empty file." };
  }
  if (buf.byteLength > MAX_PHOTO_BYTES) {
    return {
      ok: false,
      phase: "fetch",
      detail: "Image too large for Telegram (try under ~10MB).",
    };
  }

  let pathName: string;
  try {
    pathName = new URL(photoUrl).pathname;
  } catch {
    pathName = "/photo.png";
  }
  const filename = pathName.split("/").pop() || "photo.png";
  const mime =
    ctRaw && !ctRaw.startsWith("application/octet-stream")
      ? ctRaw.split(";")[0]?.trim() || "image/png"
      : "image/png";

  const up = await sendPhotoBytesToTelegram(
    token,
    chatId,
    buf,
    mime,
    filename,
    caption,
  );
  if (up.ok === false) {
    return { ok: false, phase: "telegram", detail: up.detail };
  }
  return { ok: true };
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

  const photoRaw =
    typeof body === "object" &&
    body !== null &&
    typeof (body as { photo?: unknown }).photo === "string"
      ? (body as { photo: string }).photo.trim()
      : "";

  const photoBase64 =
    typeof body === "object" &&
    body !== null &&
    typeof (body as { photoBase64?: unknown }).photoBase64 === "string"
      ? (body as { photoBase64: string }).photoBase64.replace(/\s+/g, "").trim()
      : "";

  const photoMimeRaw =
    typeof body === "object" &&
    body !== null &&
    typeof (body as { photoMime?: unknown }).photoMime === "string"
      ? (body as { photoMime: string }).photoMime.trim()
      : "";
  const photoMime =
    photoMimeRaw.length > 0
      ? photoMimeRaw.split(";")[0]?.trim() || "image/png"
      : "image/png";

  const photoFilenameRaw =
    typeof body === "object" &&
    body !== null &&
    typeof (body as { photoFilename?: unknown }).photoFilename === "string"
      ? (body as { photoFilename: string }).photoFilename.trim()
      : "";
  const photoFilename =
    photoFilenameRaw.length > 0 ? photoFilenameRaw : "photo.png";

  const hasPhotoBase64 = photoBase64.length > 0;
  const hasPhotoUrl = photoRaw.length > 0;
  const hasPhoto = hasPhotoBase64 || hasPhotoUrl;

  const hasText = text.trim().length > 0;

  if (!hasText && !hasPhoto) {
    res.status(400).json({ error: "Missing or empty text and photo" });
    return;
  }

  if (hasPhotoUrl && !hasPhotoBase64 && !photoUrlAllowed(photoRaw, req)) {
    res.status(400).json({
      error:
        "Photo URL must be https on the same host as this site (or http://localhost for local dev).",
    });
    return;
  }

  let remainder = hasText ? text : "";
  let parts = 0;

  if (hasPhoto) {
    const caption =
      remainder.length > MAX_CAPTION_CHARS
        ? remainder.slice(0, MAX_CAPTION_CHARS)
        : remainder;
    remainder =
      remainder.length > MAX_CAPTION_CHARS
        ? remainder.slice(MAX_CAPTION_CHARS)
        : "";

    if (hasPhotoBase64) {
      let decoded: Buffer;
      try {
        decoded = Buffer.from(photoBase64, "base64");
      } catch {
        res.status(400).json({ error: "Invalid photoBase64 encoding." });
        return;
      }
      if (decoded.length === 0) {
        res.status(400).json({ error: "photoBase64 decoded to empty data." });
        return;
      }
      if (decoded.length > MAX_PHOTO_BASE64_BYTES) {
        res.status(400).json({
          error: "Image too large for JSON upload (max ~3MB decoded).",
          detail:
            "Shrink the file or rely on photo URL + VERCEL_AUTOMATION_BYPASS_SECRET for large images with Deployment Protection.",
        });
        return;
      }
      const up = await sendPhotoBytesToTelegram(
        token,
        chatId,
        new Uint8Array(decoded),
        photoMime,
        photoFilename,
        caption,
      );
      if (up.ok === false) {
        res.status(502).json({
          error: "Telegram API rejected the photo.",
          detail: up.detail,
        });
        return;
      }
      parts += 1;
    } else {
      const photoResult = await sendPhotoMultipartFromUrl(
        token,
        chatId,
        photoRaw,
        caption,
      );
      if (photoResult.ok === false) {
        const errMsg =
          photoResult.phase === "fetch"
            ? "Could not load image for upload."
            : "Telegram API rejected the photo.";
        res.status(502).json({
          error: errMsg,
          detail: photoResult.detail,
        });
        return;
      }
      parts += 1;
    }
  }

  const chunks = remainder.length > 0 ? splitTelegramChunks(remainder) : [];
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
    parts += 1;
  }

  res.status(200).json({ ok: true, parts: parts > 0 ? parts : 1 });
}
