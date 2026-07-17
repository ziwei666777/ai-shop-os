import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const distServer = join(here, "..", "dist", "server");
mkdirSync(distServer, { recursive: true });

writeFileSync(
  join(distServer, "index.js"),
  `export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const assetResponse = await env.ASSETS.fetch(request);
    if (assetResponse.status !== 404) return assetResponse;

    const distUrl = new URL(url);
    distUrl.pathname = "/dist" + (url.pathname === "/" ? "/index.html" : url.pathname);
    const distAssetResponse = await env.ASSETS.fetch(new Request(distUrl, request));
    if (distAssetResponse.status !== 404) return distAssetResponse;

    const indexResponse = await env.ASSETS.fetch(new Request(new URL("/index.html", url), request));
    if (indexResponse.status !== 404) return indexResponse;

    return env.ASSETS.fetch(new Request(new URL("/dist/index.html", url), request));
  }
};
`,
  "utf8"
);
