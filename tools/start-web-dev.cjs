const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const logPath = path.join(root, "next-dev.detached.log");
const out = fs.openSync(logPath, "a");
const runner = path.join(root, "tools", "web-dev-runner.cjs");

const child = spawn(
  process.execPath,
  [runner],
  {
    cwd: root,
    detached: true,
    stdio: ["ignore", out, out],
    windowsHide: true
  }
);

child.unref();
console.log(`started ${child.pid}`);
