/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
  /** Set only at build time from a CI secret: never commit an address. */
  readonly VITE_FEEDBACK_EMAIL?: string;
}
interface ImportMeta { readonly env: ImportMetaEnv }
