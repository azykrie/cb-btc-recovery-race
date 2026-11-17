# Distribution-based risk sizing audit

Decision: keep 25% sizing and the 5% portfolio kill. No production code changed.
The signal remains 120 bars, 3x estimated costs, 2-bar recovery confirmation,
90-bar timeout and 100 bps position stop. The $5 initial fallback is intact.
No size satisfies every requested gate: all have negative bootstrap medians
for every tested block length, and 50% also loses on the real dev window.
Choosing a higher real-day PnL at 35% would repeat selection on this same day.

## Public competitive field snapshot

Source: https://make.fun/api/competitions/btc-race-24h-20261117-0603/leaderboard
read during this audit on 2026-11-17 around 11:25 UTC. The API default phase
is dev. Official API docs specify ?phase=dev; a separate explicit dev call
with rows=first also returned the same top five. Counts below are from the
full default response, not its ten-row abbreviated view.

Returned rows: 4200; entrant rows excluding
house/baseline/internal: 4196, all with distinct handles.
Positive dev PnL: 4188; positive and prize-eligible:
3781; positive and compliant: 4188.
These are current leaderboard entries, not a count of every historic submission.
The fewer-than-10 rule does not apply. Positive dev PnL alone does not establish
an unseen-race advantage; the source exposes no evidence of future results.
Public non-owner PnLs are rounded by the server.

| Dev rank | Handle | Displayed net dev USDC | Fills |
|---|---|---:|---:|
| 1 | calm-owl-89 | 108.000 | 365 |
| 2 | imamm | 107.000 | 365 |
| 3 | jackpoot | 106.000 | 225 |
| 4 | alexcarterfox | 106.000 | 367 |
| 5 | luvmee | 106.000 | 205 |
| 6 | lucky-marten-16 | 103.000 | 275 |
| 7 | dutbld | 99.400 | 348 |
| 8 | keen-sparrow-32 | 98.500 | 311 |
| 9 | vinzsenzo | 88.300 | 54 |
| 10 | chad-weasel-77 | 78.100 | 30 |

## Predeclared experiment

Exactly three sizes (25%, 35%, 50%) at one kill level (5%); no second kill
level was tested. This uses three configurations, only two new compared to
the original bot. There are now **186 unique parameter sets** in the cumulative
record. The previous total was 184 sets / 902 research replays. This adds
4,500 synthetic strategy replays plus three real-dev replays: **5,405 total
research replays**, excluding official-grade/verification repeats.

For each block length 15, 30 and 60 minutes, create 500 synthetic 24h paths
of 1,440 bars. Fixed RNG seed 202611170603 plus block length. Each path starts
at the original first bar; subsequent 1,439 transitions come from uniformly
sampled overlapping contiguous blocks of original previous-close-to-OHLC
returns, without circular wrap. Use the same 500 paths for all three sizes
at each block length. This yields 1,500 synthetic paths and 4,500 paired size
replays, not 4,500 independent synthetic histories.

Scale OHLC by the synthetic previous close with integer floors; preserve
source next-open gaps, intra-bar geometry and source open/close depths.
Depth stays in original USD units, paired with its source return. Block seams
are artificial; liquidity dynamics under different prices are unobserved.
No fees are omitted: 4 bps fee, 2 bps slippage, exact one-hop constant-product
impact with integer rounding, next-open fills and terminal close liquidation,
using the same local replay previously matched to the official action log.
Cost-aware entry math naturally responds to stake-dependent impact; no signal
formula or parameter changes accompany the size change.

Quantiles use linear interpolation of sorted realized net USDC PnL, including
the $5 fallback's costs. Drawdown is measured from bar-close marked equity and
terminal liquidation. Percentages are empirical frequencies over 500 windows
per row. Full per-window statistics, including turnover/fees/trades and best
trade removal, are retained in recon/bootstrap-outcomes-{15,30,60}.json outside
the shipped repository; these are not new strategy variants.

## Distribution by block length and size

| Block min | Size | P5 USDC | P25 | Median | P75 | P95 | P(PnL>0) | P(DD>15%) | P(DD>25%) | P(no buy filled before fallback eligibility) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | 25% | -6.091808 | -2.815731 | -0.759131 | 1.088607 | 3.245745 | 39.0% | 0.0% | 0.0% | 100.0% |
| 15 | 35% | -8.051562 | -3.432627 | -0.836810 | 1.469166 | 4.256324 | 38.6% | 0.0% | 0.0% | 100.0% |
| 15 | 50% | -10.595956 | -4.303844 | -0.851731 | 1.474625 | 4.792739 | 34.0% | 0.0% | 0.0% | 100.0% |
| 30 | 25% | -6.016117 | -2.710236 | -0.646272 | 0.770664 | 2.973498 | 34.8% | 0.0% | 0.0% | 100.0% |
| 30 | 35% | -7.895357 | -3.622847 | -1.035054 | 0.807429 | 3.796879 | 31.8% | 0.0% | 0.0% | 100.0% |
| 30 | 50% | -10.266775 | -4.471178 | -1.044539 | 0.234913 | 4.704407 | 28.6% | 0.0% | 0.0% | 100.0% |
| 60 | 25% | -5.367997 | -2.271154 | -0.316956 | 0.872619 | 3.057316 | 39.4% | 0.0% | 0.0% | 100.0% |
| 60 | 35% | -7.961563 | -2.691722 | -0.452061 | 1.227943 | 3.878941 | 39.2% | 0.0% | 0.0% | 100.0% |
| 60 | 50% | -9.588007 | -3.255330 | -0.257887 | 1.298173 | 4.958058 | 37.4% | 0.0% | 0.0% | 100.0% |

| Block min | Size | Profitable / 500 | DD>15 / DD>25 counts | Fallback buy sent | Zero completed trades | Max observed DD % |
|---|---:|---:|---:|---:|---:|---:|
| 15 | 25% | 195 | 0 / 0 | 488 | 0 | 1.36576 |
| 15 | 35% | 193 | 0 / 0 | 490 | 0 | 1.85229 |
| 15 | 50% | 170 | 0 / 0 | 493 | 0 | 2.58797 |
| 30 | 25% | 174 | 0 / 0 | 484 | 0 | 1.22590 |
| 30 | 35% | 159 | 0 / 0 | 485 | 0 | 1.71357 |
| 30 | 50% | 143 | 0 / 0 | 489 | 0 | 2.53696 |
| 60 | 25% | 197 | 0 / 0 | 481 | 0 | 1.30631 |
| 60 | 35% | 196 | 0 / 0 | 486 | 0 | 1.91212 |
| 60 | 50% | 187 | 0 / 0 | 489 | 0 | 2.24834 |

No buy filled before fallback eligibility in 100% of paths. This is structural:
the 120-return warmup first permits an entry at seq 120, exactly when fallback
eligibility starts. A normal signal may replace the fallback on that batch,
so the actual fallback-sent count can be below 500. Every tested path completed
at least one round trip. Arbitrary absent bars/rejections can still prevent a
fill; the code guarantees an attempted probe on a sufficiently long feed,
not successful execution under all possible market paths.

Zero observed drawdowns above 25% does not establish zero true risk. Under
independent draws from this fitted bootstrap generator, 0/500 has a one-sided
95% binomial upper bound of 0.597355%. That bound is conditional on this
generator, not an unconditional live-race risk bound. The 5% kill was never
tested against an unseen price gap or liquidity crisis in this data.

## Real dev and hard-rule verdict

| Size | Net USDC | Max DD % | Round trips / fills | Win % | Edge bps | Turnover | Fees USDC | Without best |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 25% | 0.593726 | 0.19818 | 4 / 8 | 50.00 | 1.385 | 1.51205 | 0.604948 | -0.494949 |
| 35% | 0.919507 | 0.28549 | 4 / 8 | 50.00 | 1.998 | 2.11409 | 0.845807 | -0.639208 |
| 50% | -0.692120 | 0.45651 | 3 / 6 | 33.33 | -10.757 | 2.01044 | 0.804342 | -1.847372 |

All sizes have empirical P(DD>25%) below 2%, real-dev drawdown below 10%, and
fallback intact with trades in every simulated window. Only 25% and 35%
have positive real-dev PnL. **None has nonnegative median bootstrap PnL**,
even requiring it separately for each block length rather than hiding
sensitivity by pooling. Thus no size qualifies and the original is kept.
All real-dev runs had zero rejected orders.

The +0.325781 USDC real-dev gain from 25% to 35% is selection-biased and
noise-level as evidence of future performance. Differences among bootstrap
medians also do not establish a live edge; no statistical significance or
rank prediction is claimed. No new strategy family, signal, indicator,
trading-hour rule, averaging down, leverage or size above 50% was tested.

## Limits

**A bootstrap of one day cannot capture regime changes. These are rough
conditional scenario bounds, not forecasts of the race.** Dependence beyond
the sampled block length, unseen fat tails, quiet-to-active transitions,
pool liquidity collapses, market drift changes and other entrants' future
behavior are not learned from 24 hours. The original signal selection bias
remains. Holding 25% is an adherence to the fallback rule when no setting
passes, not a claim that the current bot has proven positive expectation.
