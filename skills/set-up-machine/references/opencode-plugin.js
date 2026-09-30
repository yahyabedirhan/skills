// set-up-machine: the pre-tool hook, as an opencode plugin.
// Written by set-up-machine from references/opencode-plugin.js; change the skill, not this file.
// Every tool call goes to the hook first; a refusal is thrown, which stops the call and shows the agent why.
// The hook fails open: if its script is gone, or it can't run or read the call, opencode's own
// permission rules still decide.
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";

const COMMAND = __HOOK_COMMAND__;
const SCRIPT = COMMAND[1];
const TIMEOUT_MS = 10000;

function runHook(payload) {
  return new Promise((resolve) => {
    if (!existsSync(SCRIPT)) return resolve({ code: null, out: "" });
    let out = "";
    let child;
    try {
      child = spawn(COMMAND[0], COMMAND.slice(1), { stdio: ["pipe", "pipe", "ignore"] });
    } catch {
      return resolve({ code: null, out: "" });
    }
    const timer = setTimeout(() => child.kill(), TIMEOUT_MS);
    child.stdout.on("data", (chunk) => (out += chunk));
    child.on("error", () => { clearTimeout(timer); resolve({ code: null, out: "" }); });
    child.on("close", (code) => { clearTimeout(timer); resolve({ code, out }); });
    child.stdin.on("error", () => {});
    child.stdin.end(payload);
  });
}

export const SetUpMachinePreToolHook = async ({ directory }) => ({
  "tool.execute.before": async (input, output) => {
    const payload = JSON.stringify({ tool: input.tool, sessionID: input.sessionID, args: output.args, directory });
    const { code, out } = await runHook(payload);
    if (code === 0 && out.trim()) throw new Error(out.trim());
  },
});
