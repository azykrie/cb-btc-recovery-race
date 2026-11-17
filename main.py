"""Deterministic cbBTC paper trader; all signals use delivered closes only.

The selected rule buys a deep deviation after a short recovery, then exits
at its frozen entry mean, timeout, stop, or portfolio drawdown limit.
Momentum mode remains available only through the local research constructor.
The production protocol accepts no configuration other than the fixed defaults.
"""

import json
import math
import sys


DEFAULTS = {
    "mode": "reversion", "lookback": 120, "impulse": 12,
    "fast": 12, "slow": 48, "signal_sigma": 0.6, "cost_multiple": 3.0,
    "rsi_cap": 75.0, "hold": 90, "stop_bps": 100.0,
    "vol_min": 0.5, "vol_max": 50.0, "size": 0.25,
    "cooldown": 15, "kill": 0.05, "fallback_after": 120,
    "fallback_size": 0.005, "fallback_hold": 1, "slippage": 150,
    "recovery": True,
    "recovery_bars": 2,
}


class Trader:
    """One position, no pyramiding; account/fills are the source of truth."""

    def __init__(self, hello, overrides=None):
        self.p = {**DEFAULTS, **(overrides or {})}
        self.hello = hello
        self.symbol = hello["symbols"][0]["symbol"]
        self.closes = []
        self.returns = []
        self.fast = self.slow = None
        self.entered = None
        self.exit_after = 0
        self.fallback = False
        self.traded = False
        self.peak = int(hello["capital"]["quote_units"])
        self.killed = False
        self.last_exit = -10000
        self.entry_target = None

    def on_batch(self, batch):
        p = self.p
        seq = batch["seq"]
        account = batch["account"]
        equity = int(account["equity_quote_units"])
        self.peak = max(self.peak, equity)
        self.killed |= equity < self.peak * (1 - p["kill"])
        for event in batch["fills"]:
            if event["status"] == "filled":
                if event["side"] == "buy":
                    self.traded = True
                    self.entered = seq
                else:
                    self.entered = None
                    self.last_exit = seq
        bar = next((b for b in batch["bars"] if b["symbol"] == self.symbol), None)
        position = next((x for x in account["positions"] if x["symbol"] == self.symbol), None)
        if bar is None:
            return []
        close = int(bar["c"])
        if self.closes:
            self.returns.append(10000 * (close / self.closes[-1] - 1))
        self.closes.append(close)
        self.fast = close if self.fast is None else self.fast + 2 / (p["fast"] + 1) * (close - self.fast)
        self.slow = close if self.slow is None else self.slow + 2 / (p["slow"] + 1) * (close - self.slow)
        # Bound storage independently of the length of the feed.
        self.closes = self.closes[-max(p["lookback"], p["impulse"] + 1, 20):]
        self.returns = self.returns[-max(p["lookback"], 14):]
        if seq < self.hello.get("warmup_bars", 0):
            return []
        order = {"client_id": "cb-" + str(seq), "symbol": self.symbol,
                 "max_slippage_bps": p["slippage"]}
        mean = sum(self.closes) / len(self.closes)
        if position:
            scale = self.hello["symbols"][0]
            value = int(position["qty"]) * close * 10 ** self.hello["capital"]["quote_scale"] // 10 ** (scale["price_scale"] + scale["qty_scale"])
            stopped = value <= int(position["cost_quote_units"]) * (1 - p["stop_bps"] / 10000)
            timed = self.entered is not None and seq - self.entered >= self.exit_after
            # Freeze the reference on entry: a falling rolling mean is not a recovery.
            reverted = p["mode"] == "reversion" and self.entry_target is not None and close >= self.entry_target
            if self.killed or stopped or timed or (reverted and not self.fallback):
                # Emergency exits widen the limit to avoid repeatedly refusing a stop.
                order["max_slippage_bps"] = 10000 if self.killed or stopped else p["slippage"]
                return [{**order, "side": "sell", "qty": position["qty"]}]
            return []
        if self.killed or seq - self.last_exit < p["cooldown"]:
            return []
        if len(self.returns) < p["lookback"]:
            return []
        vol = math.sqrt(sum(x * x for x in self.returns) / len(self.returns))
        gain = sum(max(0, x) for x in self.returns[-14:])
        loss = sum(max(0, -x) for x in self.returns[-14:])
        rsi = 100 * gain / (gain + loss) if gain + loss else 50
        stake = int(int(account["cash_quote_units"]) * p["size"])
        depth = min(int(x) for x in bar["c_depth"])
        fees = self.hello["fees"]
        round_trip = 2 * (fees["fee_bps"] + fees["slippage_bps"] + 10000 * stake / depth)
        regime = p["vol_min"] <= vol <= p["vol_max"]
        if p["mode"] == "momentum":
            move = 10000 * (close / self.closes[-p["impulse"] - 1] - 1)
            signal = move >= max(p["cost_multiple"] * round_trip, p["signal_sigma"] * vol * math.sqrt(p["impulse"])) and self.fast > self.slow and rsi <= p["rsi_cap"]
        else:
            deviation = 10000 * (mean / close - 1)
            signal = deviation >= max(p["cost_multiple"] * round_trip, p["signal_sigma"] * vol * math.sqrt(p["lookback"]))
            if p["recovery"]:
                signal = signal and close > self.closes[-p["recovery_bars"] - 1]
        fallback = not self.traded and seq >= p["fallback_after"]
        if (regime and signal) or fallback:
            self.fallback = fallback and not (regime and signal)
            self.entry_target = mean
            self.exit_after = p["fallback_hold"] if self.fallback else p["hold"]
            if self.fallback:
                stake = max(int(fees["min_notional_quote_units"]), int(int(account["cash_quote_units"]) * p["fallback_size"]))
                # The participation probe keeps the same bounded entry slippage.
                # A rejected probe retries later; no price gap justifies chasing it.
            if stake >= int(fees["min_notional_quote_units"]):
                return [{**order, "side": "buy", "notional_quote_units": str(stake)}]
        return []


def run():
    trader = None
    for line in sys.stdin:
        message = json.loads(line)
        if message["type"] == "hello":
            trader = Trader(message)
        elif message["type"] == "batch":
            reply = {"type": "reply", "seq": message["seq"], "orders": trader.on_batch(message)}
            print(json.dumps(reply, separators=(",", ":")), flush=True)
        elif message["type"] == "done":
            break


if __name__ == "__main__":
    run()
