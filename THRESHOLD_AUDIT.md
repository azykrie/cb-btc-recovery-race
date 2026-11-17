# Cost-threshold audit and original comparison

Decision: retain the original 3x bot. The production main.py bytes are
unchanged. Exactly one parameter was varied: cost_multiple, from 3 to 4 and 5.
No estimator, trading-hour filter, sizing, exit, fallback or strategy change
was tested. The $5 initial participation probe remains enabled in all cases.

## Selection bias and number of tests

Before this audit: **182 distinct complete parameter dictionaries**, comprising
10 named candidates and 190 neighbor slots, deduplicated across candidates
and repeated settings. Fields inactive for a given family are included, so
this counts configurations, not independent ideas. Historical absent
recovery_bars is normalized to its later default of 2.

The original session log records **887 completed research replays**:
2 initial runs + 19 successful candidate runs + four robustness batches of
176, 230, 230 and 230. Repeats, fresh halves/thirds and cost-stress executions
are included in 887; official grades, protocol cash baseline, verification
and the failed candidate-script import are excluded. Three reversion
parameter sets were also tested before freezing the exit target; those
implementation revisions are additional research exposure, not additional
parameter dictionaries. Changing the fallback slippage cap was another code
revision. Thus 182 is not an effective independent-trials count.

This audit adds exactly 2 new parameter sets: **184 in total**. It runs
15 replays: original plus two new values, each on full day, two fresh halves,
and 1.5x/2x costs. Research replay total becomes **902** under the same counting
policy. No historical strategy grid was rerun to count these.

**The original +0.593726 USDC dev PnL is selection-biased.** The code and
parameters were selected after inspecting this same 24h day many times.
Neither the splits nor these two new tests are independent validation.
No reliable numerical selection-bias correction or unseen-market confidence
interval can be estimated from this evidence.

## Before and after, all required tests

| Cost hurdle | Round trips / fills | Net USDC | Half 1 | Half 2 | 1.5x costs | 2x costs | Without best | Best trade | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3x | 4 / 8 | 0.593726 | 2.010143 | -1.418354 | 0.140164 | -0.312571 | -0.494949 | 1.088675 | 0.19818 |
| 4x | 3 / 6 | -0.043970 | 0.734111 | -0.782382 | -0.346869 | -0.649766 | -0.787410 | 0.743440 | 0.21371 |
| 5x | 1 / 2 | -0.009329 | -0.009329 | -0.005145 | -0.012766 | -0.015555 | 0.000000 | -0.009329 | 0.00093 |

The full-day 4x result is 0.637696 USDC below the original; the 5x result is
0.603055 below it. These tiny absolute dollar differences on $1,000 and
1-4 round trips cannot be distinguished from noise as evidence about unseen
returns; no statistical significance is claimed. The 5x bot takes no strategy
trade: its sole round trip is the $5 probe at entry seq 121, exit seq 123.
Its without-best value is zero because removing its only losing trade leaves
no trade, not because the strategy gained diversification.

Stress multiplies BOTH 4 bps fees and 2 bps slippage; impact remains at recorded
depth. At 1.5x this is 6+3 bps each way; at 2x it is 8+4 bps each way. Each
stress run recomputes decisions using the same original hello fees, matching
the earlier research procedure; equity-sensitive stakes may change. These
are not the official grader's separate 2x-fees-only sensitivity.
Fresh-state halves each start at $1,000, reset indicators, include their own
fallback and flatten at their endpoint; half PnLs need not sum to full-day PnL.
Without-best subtracts the best realized trade from the original final PnL,
without simulating a different compounding path.

Replacement requires positive net PnL, positive 1.5x-cost PnL, less dependence
on the best trade and no greater unrounded drawdown. Dependence is assessed
using both higher without-best PnL and lower best-trade/net-PnL ratio where
net PnL is positive. The original best trade is 1.088675 USDC, or 183.363201%
of its net profit. For a losing variant the ratio has no useful interpretation.
4x fails all four checks. 5x improves drawdown but fails both profit checks;
no dependence improvement can be inferred from its sole losing probe.
Therefore neither replaces the original. The earlier five-finalist results
remain documented in RESULTS.md.

## Timestamp and quiet-period diagnostic

Only the existing bar timestamp t is used in this diagnostic. No network,
wall clock, randomness, production timestamp rule, or hardcoded market hours
is used. Hour blocks are derived from (t - first_t) // 3,600,000 for reporting
only. The quietest/most-active six blocks are selected retrospectively for
describing this day, never supplied to the bot as a filter.

There are 1440 bars and 1439 close returns. Every
timestamp step is 60000 ms; 0 intervals differ.
There is no gap-induced compression of the 120-observation horizon.
116 returns are zero (8.061154%); 141 bars have flat OHLC.
Daily all-minute RMS is 6.435344 bps, versus 6.711541
bps on nonzero returns only. Excluding zeros changes the estimand from
per-minute risk to movement per active event; it is not an automatic fix.

The quietest six blocks average 3.968368 bps RMS
and 13.055556% zero returns. The most active six
average 8.945224 bps and 3.333333% zeros.
The 1320 rolling 120-return estimates range from
3.146957 to 12.804055 bps. None falls below
the 0.5 bps gate or above its 50 bps maximum, so the volatility regime gate
does not exclude any eligible bar in this day.
The ratio of 120-minute RMS to trailing 60-minute RMS ranges from
0.777077 to 1.918214,
median 0.993377. This shows regime mixing/lag:
after a change, a 120-minute estimate can differ substantially from the recent
hour. Quiet minutes lower the estimate legitimately for time-based marks;
stale pool prices may still understate unobserved price discovery. One day
cannot establish a stable time-of-day effect or justify removing quiet hours.
The estimator and trading rules remain unchanged.

| Hour offset from first close | Bars / returns | Zero returns % | All-minute RMS bps | Active-minute RMS bps |
|---|---:|---:|---:|---:|
| 0 | 60 / 59 | 8.474576 | 4.567816 | 4.774608 |
| 1 | 60 / 60 | 5.000000 | 6.076334 | 6.234187 |
| 2 | 60 / 60 | 10.000000 | 5.474150 | 5.770260 |
| 3 | 60 / 60 | 1.666667 | 6.664500 | 6.720741 |
| 4 | 60 / 60 | 11.666667 | 4.584833 | 4.878218 |
| 5 | 60 / 60 | 15.000000 | 4.597360 | 4.986537 |
| 6 | 60 / 60 | 0.000000 | 6.283139 | 6.283139 |
| 7 | 60 / 60 | 5.000000 | 6.972226 | 7.153353 |
| 8 | 60 / 60 | 6.666667 | 14.604376 | 15.116966 |
| 9 | 60 / 60 | 0.000000 | 10.197626 | 10.197626 |
| 10 | 60 / 60 | 1.666667 | 7.914299 | 7.981088 |
| 11 | 60 / 60 | 5.000000 | 7.318314 | 7.508432 |
| 12 | 60 / 60 | 0.000000 | 6.636979 | 6.636979 |
| 13 | 60 / 60 | 8.333333 | 4.213046 | 4.400383 |
| 14 | 60 / 60 | 5.000000 | 5.088661 | 5.220856 |
| 15 | 60 / 60 | 10.000000 | 5.644218 | 5.949529 |
| 16 | 60 / 60 | 11.666667 | 4.257658 | 4.530107 |
| 17 | 60 / 60 | 8.333333 | 4.414945 | 4.611259 |
| 18 | 60 / 60 | 8.333333 | 4.566168 | 4.769207 |
| 19 | 60 / 60 | 6.666667 | 5.364674 | 5.552965 |
| 20 | 60 / 60 | 8.333333 | 5.330410 | 5.567432 |
| 21 | 60 / 60 | 15.000000 | 6.494010 | 7.043743 |
| 22 | 60 / 60 | 23.333333 | 3.399566 | 3.882578 |
| 23 | 60 / 60 | 18.333333 | 2.958827 | 3.274140 |

## Every executed scenario in this audit

| Hurdle | Scenario | Round trips / fills | Net USDC | Max DD % | Win % | Edge bps | Turnover | Fees USDC | Without best | Rejected |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3x | full | 4 / 8 | 0.593726 | 0.19818 | 50.00 | 1.385 | 1.51205 | 0.604948 | -0.494949 | 0 |
| 3x | half1_fresh | 3 / 6 | 2.010143 | 0.10106 | 66.67 | 20.694 | 1.01247 | 0.405071 | 0.921468 | 0 |
| 3x | half2_fresh | 2 / 4 | -1.418354 | 0.18028 | 0.00 | -33.409 | 0.50858 | 0.203473 | -1.413209 | 0 |
| 3x | cost1.5 | 4 / 8 | 0.140164 | 0.21311 | 50.00 | -4.834 | 1.51137 | 0.907099 | -0.797790 | 0 |
| 3x | cost2 | 4 / 8 | -0.312571 | 0.22807 | 50.00 | -10.728 | 1.51069 | 1.209037 | -1.099585 | 0 |
| 4x | full | 3 / 6 | -0.043970 | 0.21371 | 33.33 | -6.674 | 1.01032 | 0.404212 | -0.787410 | 0 |
| 4x | half1_fresh | 2 / 4 | 0.734111 | 0.08631 | 50.00 | 5.540 | 0.51073 | 0.204335 | -0.009329 | 0 |
| 4x | half2_fresh | 2 / 4 | -0.782382 | 0.12800 | 0.00 | -20.690 | 0.50922 | 0.203728 | -0.777237 | 0 |
| 4x | cost1.5 | 3 / 6 | -0.346869 | 0.22863 | 33.33 | -12.958 | 1.00994 | 0.606148 | -0.940242 | 0 |
| 4x | cost2 | 3 / 6 | -0.649766 | 0.24355 | 33.33 | -18.820 | 1.00956 | 0.807970 | -1.092324 | 0 |
| 5x | full | 1 / 2 | -0.009329 | 0.00093 | 0.00 | -18.658 | 0.00999 | 0.003998 | 0.000000 | 0 |
| 5x | half1_fresh | 1 / 2 | -0.009329 | 0.00093 | 0.00 | -18.658 | 0.00999 | 0.003998 | 0.000000 | 0 |
| 5x | half2_fresh | 1 / 2 | -0.005145 | 0.00051 | 0.00 | -10.290 | 0.00999 | 0.003999 | 0.000000 | 0 |
| 5x | cost1.5 | 1 / 2 | -0.012766 | 0.00128 | 0.00 | -25.532 | 0.00999 | 0.005995 | 0.000000 | 0 |
| 5x | cost2 | 1 / 2 | -0.015555 | 0.00156 | 0.00 | -31.110 | 0.00998 | 0.007991 | 0.000000 | 0 |

All numbers come from executed local replays. Original production actions
were previously checked against the official Docker grade. Full precision,
individual trade amounts, parameter dictionaries and criterion verdicts are
kept outside the shipped repository in recon/threshold-audit.json; all 15
scenario metrics are also in recon/threshold-all-runs.csv. The historical
count and its session-record evidence are in recon/history-audit.json.
The $5 fallback attempts participation; actual fills cannot be guaranteed in
an arbitrary window with rejected orders or absent bars. It filled in every
scenario tested here. No guarantee of profitability is made.
