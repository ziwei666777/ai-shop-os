const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const webRoot = path.join(root, "apps", "web");
const logPath = path.join(root, "next-dev.detached.log");
const nextBin = path.join(root, "node_modules", "next", "dist", "bin", "next");
const out = fs.openSync(logPath, "a");

const child = spawn(process.execPath, [nextBin, "dev"], {
  cwd: webRoot,
  stdio: ["pipe", out, out],
  windowsHide: true
});

process.on("exit", () => {
  child.kill();
});

setInterval(() => {
  if (child.killed || child.exitCode !== null) {
    process.exit(child.exitCode ?? 1);
  }
}, 1000);
