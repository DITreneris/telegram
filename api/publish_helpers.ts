/**
 * Pure helpers for /api/publish (testable without Vercel runtime).
 */

export type IncomingHeaders = {
  "x-forwarded-host"?: string | string[] | undefined;
  host?: string | string[] | undefined;
};

/** Public site hostname for this request (lowercase, no port). Empty if unknown. */
export function siteHostFromRequestHeaders(headers: IncomingHeaders): string {
  const forwarded = headers["x-forwarded-host"];
  const rawHost =
    typeof forwarded === "string"
      ? forwarded.split(",")[0]?.trim() ?? ""
      : typeof headers.host === "string"
        ? headers.host
        : "";
  if (!rawHost) {
    return "";
  }
  return rawHost.split(":")[0]?.toLowerCase() ?? "";
}

/**
 * Reject arbitrary URLs (SSRF-style abuse of our server → Telegram).
 * Allow https when the URL host matches `allowedSiteHost`.
 * Allow http only for localhost / 127.0.0.1, and the URL host must still equal `allowedSiteHost`.
 */
export function photoUrlAllowed(photoUrl: string, allowedSiteHost: string): boolean {
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
  if (!allowedSiteHost) {
    return false;
  }
  return u.hostname.toLowerCase() === allowedSiteHost;
}

/** Constant-time comparison is not required for long random bearer tokens; keep simple equality. */
export function authorizationMatchesBearer(
  authorizationHeader: string | undefined,
  bearerToken: string,
): boolean {
  const t = bearerToken.trim();
  if (!t) {
    return false;
  }
  return (authorizationHeader ?? "") === `Bearer ${t}`;
}
