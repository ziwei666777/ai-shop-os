const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const moduleName = process.argv[2];
const moduleArgs = process.argv.slice(3);

if (!moduleName) {
  console.error("缺少 Python 模块名，例如：apps.api.app.infrastructure.daily_operations_job");
  process.exit(1);
}

const root = path.resolve(__dirname, "..");
const candidates = process.platform === "win32"
  ? [
      path.join(root, ".venv", "Scripts", "python.exe"),
      "python",
      "py"
    ]
  : [
      path.join(root, ".venv", "bin", "python"),
      "python3",
      "python"
    ];

let lastError = null;

for (const python of candidates) {
  if (python.includes(path.sep) && !fs.existsSync(python)) {
    continue;
  }

  const result = spawnSync(python, ["-m", moduleName, ...moduleArgs], {
    cwd: root,
    env: process.env,
    stdio: "inherit",
    shell: false
  });

  if (result.error) {
    lastError = result.error;
    continue;
  }

  process.exit(result.status ?? 0);
}

console.error(`无法找到可用的 Python 运行环境：${lastError?.message ?? "候选命令均不可用"}`);
process.exit(1);
