"""Causal cbBTC paper trader: first establish the NDJSON protocol baseline."""

import json
import sys


def run():
    for line in sys.stdin:
        message = json.loads(line)
        if message["type"] == "batch":
            reply = {"type": "reply", "seq": message["seq"], "orders": []}
            print(json.dumps(reply, separators=(",", ":")), flush=True)
        elif message["type"] == "done":
            break


if __name__ == "__main__":
    run()
