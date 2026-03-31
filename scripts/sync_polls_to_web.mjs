/**
 * Copy canonical data/polls.json to web/public/polls.json for the Vite UI.
 * Run from repo root (Vercel build, or via web/package.json predev/prebuild).
 */
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const src = join(root, "data", "polls.json");
const destDir = join(root, "web", "public");
const dest = join(destDir, "polls.json");

try {
  mkdirSync(destDir, { recursive: true });
  copyFileSync(src, dest);
} catch (e) {
  console.error("sync_polls_to_web: failed to copy", src, "->", dest);
  console.error(e);
  process.exit(1);
}
