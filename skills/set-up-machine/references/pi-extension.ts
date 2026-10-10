// set-up-machine: the pre-tool hook, as a Pi extension.
// Written by set-up-machine from references/pi-extension.ts; change the skill, not this file.
// Every tool call goes to the hook first. A refusal blocks the call and shows the agent why.
// An ask row asks the user in Pi's confirm dialog; without a UI, the hook refuses it.
// The hook fails open: if its script is gone, or it can't run or read the call, the call goes on.
// Pi has no permission system of its own, so nothing else stops the call then.
// @ts-nocheck
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

// The hook's answer: {"block": text}, {"ask": text} or {}. Anything else counts as no answer.
async function askHook(event, ctx) {
  try {
    let sessionId = "";
    try { sessionId = ctx.sessionManager?.getSessionId?.() ?? ""; } catch {}
    const payload = JSON.stringify({
      toolName: event.toolName, input: event.input, cwd: ctx.cwd, sessionId, hasUI: ctx.hasUI === true,
    });
    const { code, out } = await runHook(payload);
    if (code !== 0) return {};
    const answer = JSON.parse(out.trim() || "{}");
    return answer && typeof answer === "object" && !Array.isArray(answer) ? answer : {};
  } catch {
    return {};
  }
}

// Ask the user. Once the hook names an ask row, a failure to ask refuses the call instead of failing open.
async function askUser(pi, ctx, question) {
  if (!ctx.hasUI) return false;
  let blocked = false;
  try {
    ctx.ui.notify("set-up-machine: a tool call needs your approval", "warning");
    // Herdr's Pi integration shows the pane as blocked while this event is active; without it, nothing listens.
    pi.events.emit("herdr:blocked", { active: true, label: "set-up-machine: approve a tool call" });
    blocked = true;
    return (await ctx.ui.confirm("set-up-machine: allow this tool call?", question)) === true;
  } catch {
    return false;
  } finally {
    if (blocked) {
      try { pi.events.emit("herdr:blocked", { active: false }); } catch {}
    }
  }
}

export default function (pi) {
  pi.on("tool_call", async (event, ctx) => {
    const answer = await askHook(event, ctx);
    if (typeof answer.block === "string" && answer.block) return { block: true, reason: answer.block };
    if (typeof answer.ask === "string" && answer.ask) {
      if (await askUser(pi, ctx, answer.ask)) return undefined;
      const why = ctx.hasUI
        ? "Refused: the user declined this call when the pre-tool hook asked. Nothing in this call ran."
        : "Refused: the pre-tool hook needs the user's approval, and this Pi session has no UI to ask. Nothing in this call ran.";
      return { block: true, reason: `${why}\n${answer.ask}` };
    }
    return undefined;
  });
}
