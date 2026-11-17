# cb-btc-recovery-race

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/azykrie/cb-btc-recovery-race/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/azykrie/cb-btc-recovery-race/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A Python 3.13 paper trader for one-minute cbBTC bars. It buys deep deviations after a short recovery, sizes at 25% of cash, and uses time, stop and drawdown exits. The measured dev profit is selection-biased after 182 prior parameter configurations on one day. The 4x/5x cost-threshold audit retained the original 3x bot; see THRESHOLD_AUDIT.md and RESULTS.md. No unseen-market edge is established.

## Run it

```sh
python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=w54ezzed&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>

Risk audit: [RISK_AUDIT.md](RISK_AUDIT.md) compares 25%, 35% and 50% sizing on 1,500 synthetic paths (4,500 paired replays). All bootstrap medians are negative; retain 25% sizing and 5% kill. Cumulative totals: 186 configurations / 5,405 research replays. These are one-day conditional scenarios, not race forecasts.
