from __future__ import annotations

import importlib.util
import json
import shutil
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "dist" / "sites-demo-console"
ARCHIVE_PATH = ROOT / "dist" / "sites-demo-console.tar.gz"
PROJECT_ID = "appgprj_6a5307e4aec0819197ad99d8de2b358b"


def _load_console_html() -> str:
    # 公开演示站和内部控制台复用同一份商家可用页面，避免出现一个宣传页、一个控制台的割裂体验。
    source = ROOT / "tools" / "create_sites_internal_app_archive.py"
    spec = importlib.util.spec_from_file_location("internal_console_archive", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法读取商家控制台生成器。")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_html()


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    if ARCHIVE_PATH.exists():
        ARCHIVE_PATH.unlink()

    (OUT_DIR / ".openai").mkdir(parents=True, exist_ok=True)
    worker = f"""const HTML = {json.dumps(_load_console_html(), ensure_ascii=False)};

export default {{
  async fetch() {{
    return new Response(HTML, {{
      headers: {{
        "content-type": "text/html; charset=utf-8",
        "cache-control": "public, max-age=60"
      }}
    }});
  }}
}};
"""
    (OUT_DIR / "index.js").write_text(worker, encoding="utf-8")
    (OUT_DIR / ".openai" / "hosting.json").write_text(
        json.dumps({"project_id": PROJECT_ID}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with tarfile.open(ARCHIVE_PATH, "w:gz") as archive:
        archive.add(OUT_DIR, arcname=".")
    print(ARCHIVE_PATH)


if __name__ == "__main__":
    main()
