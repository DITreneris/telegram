/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_PUBLISH_API_URL?: string;
  /** Same value as server PUBLISH_BEARER_TOKEN; exposed in the bundle — prefer sessionStorage prompt instead. */
  readonly VITE_PUBLISH_BEARER_TOKEN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
