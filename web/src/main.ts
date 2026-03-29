import "./style.css";

type Post = {
  id: number;
  theme: string;
  option: number;
  image?: string;
  content: string;
};

const TWITTER_HINT_LIMIT = 280;

function isPostRow(x: unknown): x is Post {
  if (typeof x !== "object" || x === null) return false;
  const o = x as Record<string, unknown>;
  const imageOk =
    o.image === undefined ||
    (typeof o.image === "string" && o.image.length > 0);
  return (
    typeof o.id === "number" &&
    typeof o.theme === "string" &&
    typeof o.option === "number" &&
    typeof o.content === "string" &&
    imageOk
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

function uniqueThemes(posts: Post[]): string[] {
  const s = new Set<string>();
  for (const p of posts) s.add(p.theme);
  return [...s].sort((a, b) => a.localeCompare(b));
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

function render(
  root: HTMLElement,
  posts: Post[],
  themes: string[],
  filterTheme: string,
  copiedId: number | null,
): void {
  const filtered =
    filterTheme === "" ? posts : posts.filter((p) => p.theme === filterTheme);

  root.innerHTML = `
    <header class="page-header">
      <h1>Socialinių postų kopijavimas</h1>
      <p class="lede">
        Nukopijuokite tekstą ir įklijuokite rankiniu būdu į LinkedIn, X (Twitter), WhatsApp ar Facebook.
      </p>
      <div class="toolbar">
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
        <span class="count-badge">Rodoma: ${filtered.length} / ${posts.length}</span>
      </div>
    </header>
    <main class="cards" role="list">
      ${filtered
        .map(
          (p) => `
        <article class="card" role="listitem" data-post-id="${p.id}">
          <div class="card-meta">
            <span class="badge">Įrašas #${p.id}</span>
            <span class="badge badge-soft">Variantas ${p.option}</span>
            <span class="char-info" title="Įskaitant tarpus ir eilučių lūžius">
              Simbolių: ${p.content.length}
              ${
                p.content.length > TWITTER_HINT_LIMIT
                  ? `<span class="hint-x"> · viršija ${TWITTER_HINT_LIMIT} (X gali reikalauti santraukos ar gijos)</span>`
                  : ""
              }
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
          <pre class="card-body" tabindex="0">${escapeHtml(p.content)}</pre>
          <div class="card-actions">
            <button type="button" class="btn-copy" data-copy-id="${p.id}">
              ${p.id === copiedId ? "Nukopijuota" : "Kopijuoti tekstą"}
            </button>
          </div>
        </article>`,
        )
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

  const themes = uniqueThemes(posts);
  let filterTheme = "";
  let copiedId: number | null = null;
  let copyResetTimer: ReturnType<typeof setTimeout> | null = null;

  const paint = (): void => {
    render(app, posts, themes, filterTheme, copiedId);
    wireEvents();
  };

  const wireEvents = (): void => {
    const sel = app.querySelector<HTMLSelectElement>("#theme-filter");
    sel?.addEventListener("change", () => {
      filterTheme = sel.value;
      copiedId = null;
      if (copyResetTimer) clearTimeout(copyResetTimer);
      paint();
    });

    app.querySelectorAll<HTMLButtonElement>(".btn-copy").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = Number(btn.dataset.copyId);
        const post = posts.find((p) => p.id === id);
        if (!post) return;
        const ok = await copyText(post.content);
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
  };

  paint();
}

main();
