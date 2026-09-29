#!/usr/bin/env python3
"""A stand-in model for a Codex session without a login: it answers the Responses API with
one shell call (the command given), then records what the agent read back and ends the turn.

    python3 stand_in_model.py --port 8765 --command 'rm -rf x' --out result.json

Point Codex at it with a `model_providers` entry (`wire_api = "responses"`, no key).
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--command", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    state = {"calls": 0}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or "{}")
            state["calls"] += 1
            outputs = [i for i in body.get("input", []) if isinstance(i, dict) and i.get("type") == "function_call_output"]
            if outputs:
                with open(args.out, "w") as f:
                    json.dump({"command": args.command, "output": outputs[-1].get("output")}, f, indent=2)
                item = {"type": "message", "role": "assistant", "id": "msg_2",
                        "content": [{"type": "output_text", "text": "done", "annotations": []}]}
            else:
                tools = [t.get("name") for t in body.get("tools", []) if isinstance(t, dict)]
                if "exec_command" in tools:
                    name, arguments = "exec_command", {"cmd": args.command}
                else:
                    name, arguments = "shell", {"command": ["bash", "-lc", args.command]}
                item = {"type": "function_call", "id": "fc_1", "call_id": "call_1", "name": name,
                        "arguments": json.dumps(arguments)}
            rid = f"resp_{state['calls']}"
            events = [
                ("response.created", {"type": "response.created", "response": {"id": rid}}),
                ("response.output_item.done", {"type": "response.output_item.done", "output_index": 0, "item": item}),
                ("response.completed", {"type": "response.completed", "response": {
                    "id": rid, "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2,
                                         "input_tokens_details": {"cached_tokens": 0},
                                         "output_tokens_details": {"reasoning_tokens": 0}}}}),
            ]
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for event, data in events:
                self.wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode())
            self.wfile.flush()

    HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
