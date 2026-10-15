// set-up-machine: the pre-tool hook, as a Pi extension.
// Written by set-up-machine from references/pi-extension.ts; change the skill, not this file.
// Every tool call goes to the hook first. A refusal blocks the call and shows the agent why.
// An ask row asks the user in a dialog whose first answer is No; without a UI, the hook refuses it.
// The hook fails closed: Pi has no permission system of its own, so when the hook can't check a call,
// the extension refuses it.
// @ts-nocheck
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";

const COMMAND = __HOOK_COMMAND__;
const SCRIPT = COMMAND[1];
const TIMEOUT_MS = 10000;

const NO = "No, refuse this call";
const YES = "Yes, allow this call";

function runHook(payload) {
  return new Promise((resolve) => {
    if (!existsSync(SCRIPT)) return resolve({ failed: "its script is missing" });
    let out = "";
    let timedOut = false;
    let child;
    try {
      child = spawn(COMMAND[0], COMMAND.slice(1), { stdio: ["pipe", "pipe", "ignore"] });
    } catch {
      return resolve({ failed: `${COMMAND[0]} can't start` });
    }
    const timer = setTimeout(() => { timedOut = true; child.kill(); }, TIMEOUT_MS);
    child.stdout.on("data", (chunk) => (out += chunk));
    child.on("error", () => { clearTimeout(timer); resolve({ failed: `${COMMAND[0]} can't start` }); });
    child.on("close", (code) => {
      clearTimeout(timer);
      if (timedOut) resolve({ failed: `it took over ${TIMEOUT_MS / 1000} seconds` });
      else if (code !== 0) resolve({ failed: `it exited with code ${code}` });
      else resolve({ out });
    });
    child.stdin.on("error", () => {});
    child.stdin.end(payload);
  });
}

// The hook's answer: {"block": text}, {"ask": text} or {}. Anything else is a failure.
async function askHook(event, ctx) {
  try {
    let sessionId = "";
    try { sessionId = ctx.sessionManager?.getSessionId?.() ?? ""; } catch {}
    const payload = JSON.stringify({
      toolName: event.toolName, input: event.input, cwd: ctx.cwd, sessionId, hasUI: ctx.hasUI === true,
    });
    const { failed, out } = await runHook(payload);
    if (failed) return { failed };
    let answer;
    try { answer = JSON.parse(out.trim()); } catch { return { failed: "its answer isn't JSON" }; }
    if (!answer || typeof answer !== "object" || Array.isArray(answer)) return { failed: "its answer isn't a JSON object" };
    return answer;
  } catch {
    return { failed: "the extension couldn't run it" };
  }
}

function unavailable(why) {
  return "Refused: the pre-tool hook couldn't check this call, because " + why + ". " +
    "Pi has no other guardrail, so nothing in this call ran. " +
    "Stop, and ask the user to run /set-up-machine to repair the hook.";
}

// Ask the user, with No as the first answer, so Enter refuses. Any failure to ask refuses the call.
async function askUser(pi, ctx, question) {
  if (!ctx.hasUI) return false;
  let blocked = false;
  try {
    ctx.ui.notify("set-up-machine: a tool call needs your approval", "warning");
    // Herdr's Pi integration shows the pane as blocked while this event is active; without it, nothing listens.
    pi.events.emit("herdr:blocked", { active: true, label: "set-up-machine: approve a tool call" });
    blocked = true;
    return (await ctx.ui.select(`set-up-machine: allow this tool call?\n${question}`, [NO, YES])) === YES;
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
    if (typeof answer.failed === "string") return { block: true, reason: unavailable(answer.failed) };
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
