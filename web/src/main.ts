import "./style.css";

type Post = {
  id: number;
  theme: string;
  option: number;
  image?: string;
  content: string;
  topic_key?: string;
};

type PollItem = {
  id: string;
  related_post_id: number;
  question: string;
  options: string[];
  correct_option_id: number;
  theme_note?: string;
};

type PublishFilter = "all" | "published" | "unpublished";
type SortMode = "order" | "id_asc" | "id_desc" | "theme_asc";

const TWITTER_HINT_LIMIT = 280;

const PUBLISH_BEARER_STORAGE_KEY = "tgPublishBearer";
const CONTENT_EDITS_STORAGE_KEY = "socialPostsContentEdits";
const PUBLISHED_STORAGE_KEY = "socialPostsPublished";

const publishApiBase = (import.meta.env.VITE_PUBLISH_API_URL ?? "/api/publish").replace(
  /\/$/,
  "",
);

/** Keep under api/publish JSON body limits on Vercel (~4.5MB); larger images use URL + server fetch. */
const MAX_PUBLISH_IMAGE_BASE64_BYTES = 3 * 1024 * 1024;

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => {
      const dataUrl = r.result as string;
      const i = dataUrl.indexOf(",");
      resolve(i >= 0 ? dataUrl.slice(i + 1) : dataUrl);
    };
    r.onerror = () => reject(r.error ?? new Error("FileReader failed"));
    r.readAsDataURL(blob);
  });
}

function getPublishBearer(): string | null {
  const fromEnv = import.meta.env.VITE_PUBLISH_BEARER_TOKEN?.trim();
  if (fromEnv) return fromEnv;
  const fromStore = sessionStorage.getItem(PUBLISH_BEARER_STORAGE_KEY)?.trim();
  if (fromStore) return fromStore;
  const entered = window.prompt(
    "Enter the publish key (same as PUBLISH_BEARER_TOKEN on the server):",
  )?.trim();
  if (!entered) return null;
  sessionStorage.setItem(PUBLISH_BEARER_STORAGE_KEY, entered);
  return entered;
}

async function publishPostToTelegram(
  text: string,
  options?: { imagePath?: string | null; imageFilename?: string },
): Promise<{ ok: true; parts: number } | { ok: false; message: string }> {
  const bearer = getPublishBearer();
  if (!bearer) {
    return { ok: false, message: "Publishing cancelled." };
  }

  const body: {
    text: string;
    photo?: string;
    photoBase64?: string;
    photoMime?: string;
    photoFilename?: string;
  } = { text };

  if (options?.imagePath) {
    const rel = options.imagePath;
    const imgRes = await fetch(rel);
    if (!imgRes.ok) {
      return {
        ok: false,
        message: `Nepavyko įkelti paveikslėlio (HTTP ${imgRes.status}).`,
      };
    }
    const blob = await imgRes.blob();
    const name = (options.imageFilename?.trim() || "photo.png").replace(/[/\\]/g, "_");
    if (blob.size <= MAX_PUBLISH_IMAGE_BASE64_BYTES) {
      try {
        body.photoBase64 = await blobToBase64(blob);
      } catch (e) {
        return {
          ok: false,
          message: `Nepavyko paruošti paveikslėlio: ${String(e)}`,
        };
      }
      body.photoMime =
        imgRes.headers.get("content-type")?.split(";")[0]?.trim() || "image/png";
      body.photoFilename = name;
    } else {
      body.photo = new URL(rel, window.location.origin).href;
    }
  }

  const res = await fetch(publishApiBase, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${bearer}`,
    },
    body: JSON.stringify(body),
  });

  let payload: unknown;
  try {
    payload = await res.json();
  } catch {
    payload = null;
  }

  if (res.status === 401) {
    sessionStorage.removeItem(PUBLISH_BEARER_STORAGE_KEY);
  }

  if (!res.ok) {
    const p =
      typeof payload === "object" && payload !== null
        ? (payload as { error?: unknown; detail?: unknown })
        : null;
    let msg =
      p && typeof p.error === "string" ? p.error : `HTTP ${res.status}`;
    if (p && typeof p.detail === "string" && p.detail.trim()) {
      msg += ` — ${p.detail.trim()}`;
    }
    return { ok: false, message: msg };
  }

  const parts =
    typeof payload === "object" &&
    payload !== null &&
    typeof (payload as { parts?: unknown }).parts === "number"
      ? (payload as { parts: number }).parts
      : 1;

  return { ok: true, parts };
}

function isPostRow(x: unknown): x is Post {
  if (typeof x !== "object" || x === null) return false;
  const o = x as Record<string, unknown>;
  const imageOk =
    o.image === undefined ||
    (typeof o.image === "string" && o.image.length > 0);
  const topicKeyOk =
    o.topic_key === undefined ||
    (typeof o.topic_key === "string" && o.topic_key.length > 0);
  return (
    typeof o.id === "number" &&
    typeof o.theme === "string" &&
    typeof o.option === "number" &&
    typeof o.content === "string" &&
    imageOk &&
    topicKeyOk
  );
}

async function loadPosts(): Promise<Post[]> {
  const res = await fetch("/posts.json");
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data: unknown = await res.json();
  if (!Array.isArray(data)) throw new Error("posts.json turi būti masyvas.");
  const posts = data.filter(isPostRow);
  if (posts.length === 0) throw new Error("Nėra tinkamų įrašų.");
  return posts;
}

function isPollItem(x: unknown): x is PollItem {
  if (typeof x !== "object" || x === null) return false;
  const o = x as Record<string, unknown>;
  if (typeof o.id !== "string" || !o.id.trim()) return false;
  if (typeof o.related_post_id !== "number" || !Number.isFinite(o.related_post_id)) {
    return false;
  }
  if (typeof o.question !== "string" || !o.question.trim()) return false;
  if (!Array.isArray(o.options)) return false;
  for (const opt of o.options) {
    if (typeof opt !== "string" || !opt.trim()) return false;
  }
  if (typeof o.correct_option_id !== "number" || !Number.isFinite(o.correct_option_id)) {
    return false;
  }
  if (o.correct_option_id < 0 || o.correct_option_id >= o.options.length) return false;
  if (o.theme_note !== undefined) {
    if (typeof o.theme_note !== "string" || !o.theme_note.trim()) return false;
  }
  return true;
}

async function loadPolls(): Promise<Map<number, PollItem[]>> {
  const empty = new Map<number, PollItem[]>();
  const res = await fetch("/polls.json");
  if (!res.ok) return empty;
  let data: unknown;
  try {
    data = await res.json();
  } catch {
    return empty;
  }
  if (typeof data !== "object" || data === null) return empty;
  const root = data as Record<string, unknown>;
  if (root.version !== 1) return empty;
  if (!Array.isArray(root.items)) return empty;
  const items = root.items.filter(isPollItem);
  const byPost = new Map<number, PollItem[]>();
  for (const p of items) {
    const pid = p.related_post_id;
    const list = byPost.get(pid) ?? [];
    list.push(p);
    byPost.set(pid, list);
  }
  for (const [, list] of byPost) {
    list.sort((a, b) => a.id.localeCompare(b.id));
  }
  return byPost;
}

function loadPublishedFromStorage(): Map<number, string> {
  const raw = localStorage.getItem(PUBLISHED_STORAGE_KEY);
  if (!raw) return new Map();
  try {
    const o = JSON.parse(raw) as unknown;
    if (typeof o !== "object" || o === null) return new Map();
    const m = new Map<number, string>();
    for (const [k, v] of Object.entries(o as Record<string, unknown>)) {
      const id = Number(k);
      if (!Number.isFinite(id) || typeof v !== "string") continue;
      m.set(id, v);
    }
    return m;
  } catch {
    return new Map();
  }
}

function savePublishedToStorage(m: Map<number, string>): void {
  if (m.size === 0) {
    localStorage.removeItem(PUBLISHED_STORAGE_KEY);
    return;
  }
  const o: Record<string, string> = {};
  for (const [id, at] of m) o[String(id)] = at;
  localStorage.setItem(PUBLISHED_STORAGE_KEY, JSON.stringify(o));
}

function prunePublished(posts: Post[], m: Map<number, string>): void {
  const ids = new Set(posts.map((p) => p.id));
  for (const id of [...m.keys()]) {
    if (!ids.has(id)) m.delete(id);
  }
}

function formatPublishedLabel(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

function loadContentEditsFromStorage(): Map<number, string> {
  const raw = sessionStorage.getItem(CONTENT_EDITS_STORAGE_KEY);
  if (!raw) return new Map();
  try {
    const o = JSON.parse(raw) as unknown;
    if (typeof o !== "object" || o === null) return new Map();
    const m = new Map<number, string>();
    for (const [k, v] of Object.entries(o as Record<string, unknown>)) {
      const id = Number(k);
      if (!Number.isFinite(id) || typeof v !== "string") continue;
      m.set(id, v);
    }
    return m;
  } catch {
    return new Map();
  }
}

function saveContentEditsToStorage(m: Map<number, string>): void {
  if (m.size === 0) {
    sessionStorage.removeItem(CONTENT_EDITS_STORAGE_KEY);
    return;
  }
  const o: Record<string, string> = {};
  for (const [id, text] of m) o[String(id)] = text;
  sessionStorage.setItem(CONTENT_EDITS_STORAGE_KEY, JSON.stringify(o));
}

function pruneContentEdits(posts: Post[], m: Map<number, string>): void {
  const byId = new Map(posts.map((p) => [p.id, p] as const));
  for (const id of [...m.keys()]) {
    const post = byId.get(id);
    if (!post || m.get(id) === post.content) m.delete(id);
  }
}

function uniqueThemes(posts: Post[]): string[] {
  const s = new Set<string>();
  for (const p of posts) s.add(p.theme);
  return [...s].sort((a, b) => a.localeCompare(b));
}

function matchesSearch(p: Post, q: string): boolean {
  const s = q.trim().toLowerCase();
  if (!s) return true;
  const tk = p.topic_key?.toLowerCase() ?? "";
  return (
    p.theme.toLowerCase().includes(s) ||
    p.content.toLowerCase().includes(s) ||
    tk.includes(s)
  );
}

function filterAndSortPosts(
  posts: Post[],
  opts: {
    filterTheme: string;
    searchQuery: string;
    publishFilter: PublishFilter;
    sortMode: SortMode;
    published: Map<number, string>;
  },
): Post[] {
  let list = posts.filter((p) =>
    opts.filterTheme === "" ? true : p.theme === opts.filterTheme,
  );
  list = list.filter((p) => matchesSearch(p, opts.searchQuery));
  if (opts.publishFilter === "published") {
    list = list.filter((p) => opts.published.has(p.id));
  } else if (opts.publishFilter === "unpublished") {
    list = list.filter((p) => !opts.published.has(p.id));
  }
  const orderIndex = new Map(posts.map((p, i) => [p.id, i] as const));
  list = [...list];
  if (opts.sortMode === "order") {
    list.sort((a, b) => (orderIndex.get(a.id) ?? 0) - (orderIndex.get(b.id) ?? 0));
  } else if (opts.sortMode === "id_asc") {
    list.sort((a, b) => a.id - b.id);
  } else if (opts.sortMode === "id_desc") {
    list.sort((a, b) => b.id - a.id);
  } else if (opts.sortMode === "theme_asc") {
    list.sort((a, b) => a.theme.localeCompare(b.theme));
  }
  return list;
}

async function copyText(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    /* fallback below */
  }
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(ta);
    return ok;
  } catch {
    return false;
  }
}

function imageDownloadFilename(post: Post): string {
  if (!post.image) return `post-${post.id}.png`;
  const base = post.image.split("/").pop() ?? "";
  if (base && /\.[a-z0-9]+$/i.test(base)) return base;
  return `post-${post.id}.png`;
}

async function downloadPostImage(post: Post): Promise<void> {
  if (!post.image) return;
  const abs = new URL(post.image, window.location.origin).href;
  const filename = imageDownloadFilename(post);
  try {
    const res = await fetch(abs);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.rel = "noopener";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch {
    window.alert(
      "Nepavyko atsisiųsti failo automatiškai. Atidaromas paveikslėlis naujame skirtuke — išsaugokite jį rankiniu būdu (dešinysis paspaudimas → Save image).",
    );
    window.open(abs, "_blank", "noopener,noreferrer");
  }
}

function charInfoHtml(length: number): string {
  const hint =
    length > TWITTER_HINT_LIMIT
      ? `<span class="hint-x"> · viršija ${TWITTER_HINT_LIMIT} (X gali reikalauti santraukos ar gijos)</span>`
      : "";
  return `Simbolių: ${length}${hint}`;
}

function pollBlockHtml(p: Post, pollsByPost: Map<number, PollItem[]>): string {
  const polls = pollsByPost.get(p.id);
  if (!polls || polls.length === 0) return "";
  const blocks = polls.map((poll) => {
    const opts = poll.options
      .map(
        (opt, i) =>
          `<li class="poll-option"><span class="poll-option-idx">${i + 1}.</span> ${escapeHtml(opt)}</li>`,
      )
      .join("");
    const correctIdx = poll.correct_option_id;
    const correctLabel =
      correctIdx >= 0 && correctIdx < poll.options.length
        ? escapeHtml(poll.options[correctIdx] ?? "")
        : "";
    const note =
      poll.theme_note?.trim() ?
        `<p class="poll-theme-note">${escapeHtml(poll.theme_note.trim())}</p>`
      : "";
    return `
      <div class="poll-item" data-poll-id="${escapeAttr(poll.id)}">
        <h3 class="poll-question">${escapeHtml(poll.question.trim())}</h3>
        <ol class="poll-options">${opts}</ol>
        <p class="poll-correct"><span class="poll-correct-label">Teisingas variantas:</span> ${correctLabel}</p>
        ${note}
      </div>`;
  });
  return `
    <section class="poll-block" aria-label="Apklausos">
      <h3 class="poll-block-title">Apklausa (quiz)</h3>
      ${blocks.join("")}
    </section>`;
}

function render(
  root: HTMLElement,
  posts: Post[],
  themes: string[],
  filterTheme: string,
  searchQuery: string,
  publishFilter: PublishFilter,
  sortMode: SortMode,
  pollsByPost: Map<number, PollItem[]>,
  published: Map<number, string>,
  copiedId: number | null,
  publishingId: number | null,
  editingIds: Set<number>,
  getEffectiveContent: (p: Post) => string,
): void {
  const displayed = filterAndSortPosts(posts, {
    filterTheme,
    searchQuery,
    publishFilter,
    sortMode,
    published,
  });

  root.innerHTML = `
    <header class="page-header">
      <h1>Socialinių postų kopijavimas</h1>
      <p class="lede">
        Nukopijuokite tekstą ir įklijuokite rankiniu būdu į LinkedIn, X (Twitter), WhatsApp ar Facebook.
        Jei sukonfigūruotas Vercel API, galite publikuoti į Telegram mygtuku žemiau.
        Tekstą galite pataisyti šioje naršyklės sesijoje; perkrovus puslapį vėl bus <code>posts.json</code> turinys.
        Apklausos kraunamos iš <code>polls.json</code> (sinchronizuojama iš <code>data/polls.json</code> prieš build).
        Žyma „Publikuota“ saugoma šioje naršyklėje (ne Telegram istorija).
      </p>
      <div class="toolbar toolbar-grid">
        <div class="toolbar-row">
          <label class="filter-label" for="theme-filter">Filtruoti pagal temą</label>
          <select id="theme-filter" class="theme-select" aria-label="Filtruoti pagal temą">
            <option value="">Visos temos</option>
            ${themes
              .map(
                (t) =>
                  `<option value="${escapeAttr(t)}" ${t === filterTheme ? "selected" : ""}>${escapeHtml(t)}</option>`,
              )
              .join("")}
          </select>
        </div>
        <div class="toolbar-row">
          <label class="filter-label" for="search-posts">Paieška</label>
          <input
            type="search"
            id="search-posts"
            class="search-input"
            placeholder="Tema, tekstas, topic_key…"
            value="${escapeAttr(searchQuery)}"
            aria-label="Ieškoti postų"
          />
        </div>
        <div class="toolbar-row toolbar-row-split">
          <div class="toolbar-field">
            <label class="filter-label" for="publish-filter">Būsena (Telegram publish)</label>
            <select id="publish-filter" class="theme-select" aria-label="Filtruoti pagal publikavimą">
              <option value="all" ${publishFilter === "all" ? "selected" : ""}>Visi</option>
              <option value="unpublished" ${publishFilter === "unpublished" ? "selected" : ""}>Tik nepublikuoti</option>
              <option value="published" ${publishFilter === "published" ? "selected" : ""}>Tik publikuoti</option>
            </select>
          </div>
          <div class="toolbar-field">
            <label class="filter-label" for="sort-posts">Rūšiavimas</label>
            <select id="sort-posts" class="theme-select" aria-label="Rūšiavimas">
              <option value="order" ${sortMode === "order" ? "selected" : ""}>Kaip posts.json</option>
              <option value="id_asc" ${sortMode === "id_asc" ? "selected" : ""}>ID didėjančiai</option>
              <option value="id_desc" ${sortMode === "id_desc" ? "selected" : ""}>ID mažėjančiai</option>
              <option value="theme_asc" ${sortMode === "theme_asc" ? "selected" : ""}>Tema A–Z</option>
            </select>
          </div>
        </div>
        <span class="count-badge">Rodoma: ${displayed.length} / ${posts.length}</span>
      </div>
    </header>
    <main class="cards" role="list">
      ${displayed
        .map((p) => {
          const eff = getEffectiveContent(p);
          const isEditing = editingIds.has(p.id);
          const dirty = eff !== p.content;
          const pubAt = published.get(p.id);
          const topicKeyBadge =
            p.topic_key?.trim() ?
              `<span class="badge badge-topic" title="topic_key">${escapeHtml(p.topic_key.trim())}</span>`
            : "";
          const publishedBadge =
            pubAt ?
              `<span class="badge badge-published" title="${escapeAttr(pubAt)}">Publikuota: ${escapeHtml(formatPublishedLabel(pubAt))}</span>`
            : "";
          return `
        <article class="card" role="listitem" data-post-id="${p.id}">
          <div class="card-meta">
            <span class="badge">Įrašas #${p.id}</span>
            <span class="badge badge-soft">Variantas ${p.option}</span>
            ${topicKeyBadge}
            ${publishedBadge}
            ${
              dirty
                ? `<span class="badge badge-dirty" title="Pakeitimas galioja tik šioje naršyklės sesijoje">Sesija</span>`
                : ""
            }
            <span class="char-info" data-char-for="${p.id}" title="Įskaitant tarpus ir eilučių lūžius">
              ${charInfoHtml(eff.length)}
            </span>
          </div>
          ${
            p.image
              ? `<figure class="card-figure">
            <img
              class="card-img"
              src="${escapeAttr(p.image)}"
              alt="${escapeAttr(p.theme)}"
              width="1600"
              height="900"
              loading="lazy"
              decoding="async"
            />
          </figure>`
              : ""
          }
          <h2 class="card-theme">${escapeHtml(p.theme)}</h2>
          ${
            isEditing
              ? `<textarea class="card-body card-body-edit" data-content-id="${p.id}" rows="14" aria-label="Redaguojamas tekstas"></textarea>`
              : `<pre class="card-body" tabindex="0">${escapeHtml(eff)}</pre>`
          }
          ${pollBlockHtml(p, pollsByPost)}
          <div class="card-actions">
            ${
              p.image
                ? `<button type="button" class="btn-download" data-download-id="${p.id}">Atsisiųsti paveikslėlį</button>`
                : ""
            }
            <button
              type="button"
              class="btn-telegram"
              data-telegram-id="${p.id}"
              ${publishingId === p.id ? "disabled" : ""}
            >
              ${publishingId === p.id ? "Siunčiama…" : "Publikuoti į Telegram"}
            </button>
            <button type="button" class="btn-copy" data-copy-id="${p.id}">
              ${p.id === copiedId ? "Nukopijuota" : "Kopijuoti tekstą"}
            </button>
            <button type="button" class="btn-edit" data-edit-id="${p.id}">
              ${isEditing ? "Baigti redagavimą" : "Redaguoti tekstą"}
            </button>
            ${
              dirty
                ? `<button type="button" class="btn-restore" data-restore-id="${p.id}">Atkurti originalą</button>`
                : ""
            }
          </div>
        </article>`;
        })
        .join("")}
    </main>
  `;
}

function escapeHtml(s: string): string {
  return s
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttr(s: string): string {
  return escapeHtml(s).replaceAll("'", "&#39;");
}

function parsePublishFilter(v: string): PublishFilter {
  if (v === "published" || v === "unpublished") return v;
  return "all";
}

function parseSortMode(v: string): SortMode {
  if (v === "id_asc" || v === "id_desc" || v === "theme_asc" || v === "order") return v;
  return "order";
}

async function main(): Promise<void> {
  const app = document.querySelector<HTMLElement>("#app");
  if (!app) return;

  let posts: Post[];
  try {
    posts = await loadPosts();
  } catch (e) {
    app.innerHTML = `<p class="error">Nepavyko įkelti duomenų: ${escapeHtml(String(e))}</p>`;
    return;
  }

  const pollsByPost = await loadPolls();

  const contentEdits = loadContentEditsFromStorage();
  pruneContentEdits(posts, contentEdits);
  saveContentEditsToStorage(contentEdits);

  const published = loadPublishedFromStorage();
  prunePublished(posts, published);
  savePublishedToStorage(published);

  const getEffectiveContent = (p: Post): string =>
    contentEdits.get(p.id) ?? p.content;

  const themes = uniqueThemes(posts);
  let filterTheme = "";
  let searchQuery = "";
  let publishFilter: PublishFilter = "all";
  let sortMode: SortMode = "order";
  let copiedId: number | null = null;
  let publishingId: number | null = null;
  let copyResetTimer: ReturnType<typeof setTimeout> | null = null;
  const editingIds = new Set<number>();

  const paint = (): void => {
    render(
      app,
      posts,
      themes,
      filterTheme,
      searchQuery,
      publishFilter,
      sortMode,
      pollsByPost,
      published,
      copiedId,
      publishingId,
      editingIds,
      getEffectiveContent,
    );
    wireEvents();
  };

  const wireEvents = (): void => {
    const sel = app.querySelector<HTMLSelectElement>("#theme-filter");
    sel?.addEventListener("change", () => {
      filterTheme = sel.value;
      copiedId = null;
      editingIds.clear();
      if (copyResetTimer) clearTimeout(copyResetTimer);
      paint();
    });

    const searchEl = app.querySelector<HTMLInputElement>("#search-posts");
    searchEl?.addEventListener("input", () => {
      searchQuery = searchEl.value;
      copiedId = null;
      editingIds.clear();
      if (copyResetTimer) clearTimeout(copyResetTimer);
      paint();
    });

    const pubEl = app.querySelector<HTMLSelectElement>("#publish-filter");
    pubEl?.addEventListener("change", () => {
      publishFilter = parsePublishFilter(pubEl.value);
      copiedId = null;
      editingIds.clear();
      if (copyResetTimer) clearTimeout(copyResetTimer);
      paint();
    });

    const sortEl = app.querySelector<HTMLSelectElement>("#sort-posts");
    sortEl?.addEventListener("change", () => {
      sortMode = parseSortMode(sortEl.value);
      copiedId = null;
      editingIds.clear();
      if (copyResetTimer) clearTimeout(copyResetTimer);
      paint();
    });

    app.querySelectorAll<HTMLTextAreaElement>("textarea.card-body-edit").forEach((ta) => {
      const id = Number(ta.dataset.contentId);
      const post = posts.find((p) => p.id === id);
      if (!post) return;
      ta.value = getEffectiveContent(post);
      ta.addEventListener("input", () => {
        const t = ta.value;
        if (t === post.content) contentEdits.delete(id);
        else contentEdits.set(id, t);
        saveContentEditsToStorage(contentEdits);
        const info = ta.closest(".card")?.querySelector<HTMLElement>(
          `[data-char-for="${id}"]`,
        );
        if (info) info.innerHTML = charInfoHtml(t.length);
      });
    });

    app.querySelectorAll<HTMLButtonElement>(".btn-download").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = Number(btn.dataset.downloadId);
        const post = posts.find((p) => p.id === id);
        if (!post?.image) return;
        await downloadPostImage(post);
      });
    });

    app.querySelectorAll<HTMLButtonElement>(".btn-telegram").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = Number(btn.dataset.telegramId);
        const post = posts.find((p) => p.id === id);
        if (!post || publishingId !== null) return;
        publishingId = id;
        paint();
        const result = await publishPostToTelegram(getEffectiveContent(post), {
          imagePath: post.image ?? null,
          imageFilename: post.image ? imageDownloadFilename(post) : undefined,
        });
        publishingId = null;
        if (result.ok) {
          published.set(id, new Date().toISOString());
          savePublishedToStorage(published);
        }
        paint();
        if (result.ok) {
          const mediaNote = post.image ? " Tekstas ir paveikslėlis." : "";
          const note =
            result.parts > 1
              ? ` Posted in ${result.parts} parts (Telegram message length limit).`
              : "";
          window.alert(`Įrašas išsiųstas į Telegram.${mediaNote}${note}`);
        } else {
          window.alert(`Nepavyko publikuoti: ${result.message}`);
        }
      });
    });

    app.querySelectorAll<HTMLButtonElement>(".btn-copy").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = Number(btn.dataset.copyId);
        const post = posts.find((p) => p.id === id);
        if (!post) return;
        const ok = await copyText(getEffectiveContent(post));
        if (!ok) {
          window.alert("Nepavyko nukopijuoti. Bandykite pažymėti tekstą rankiniu būdu.");
          return;
        }
        copiedId = id;
        if (copyResetTimer) clearTimeout(copyResetTimer);
        paint();
        copyResetTimer = setTimeout(() => {
          copiedId = null;
          paint();
        }, 2000);
      });
    });

    app.querySelectorAll<HTMLButtonElement>(".btn-edit").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = Number(btn.dataset.editId);
        const post = posts.find((p) => p.id === id);
        if (!post) return;
        if (editingIds.has(id)) {
          const ta = app.querySelector<HTMLTextAreaElement>(
            `textarea.card-body-edit[data-content-id="${id}"]`,
          );
          if (ta) {
            const t = ta.value;
            if (t === post.content) contentEdits.delete(id);
            else contentEdits.set(id, t);
            pruneContentEdits(posts, contentEdits);
            saveContentEditsToStorage(contentEdits);
          }
          editingIds.delete(id);
        } else {
          editingIds.add(id);
        }
        paint();
      });
    });

    app.querySelectorAll<HTMLButtonElement>(".btn-restore").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = Number(btn.dataset.restoreId);
        contentEdits.delete(id);
        saveContentEditsToStorage(contentEdits);
        paint();
      });
    });
  };

  paint();
}

main();
