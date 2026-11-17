# Measured results and limits

Follow-up audit: see [THRESHOLD_AUDIT.md](THRESHOLD_AUDIT.md) for all 3x/4x/5x results, the 182 prior parameter-set count, explicit selection bias, and timestamp diagnostics. The original 3x bot is retained.

Selected: reversion-recovery-wide. It has the lowest measured drawdown among
the five finalists with positive dev PnL and nonnegative PnL at 1.5x costs.
**No candidate satisfies the stronger requirement of a robust positive edge:**
all lose when their single best trade is removed. The selected bot loses in
the second half. It passes the contest dev-profit gate, not a statistical
proof of profitability. These results are likely dominated by noise.

The official kit verified 29 files and re-derived 1,440 bars from 42,798
pool-state samples. Window return was +0.488539%. No race data was used.
The bot uses no timestamps to identify this dev window.

## Finalists, all costs included

| Candidate | Net USDC | Max DD % | Round trips | Win % | Edge bps | Turnover / initial equity | 1.5x costs | 2x costs | Without best | Active neighbors positive |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reversion-recovery | 0.321052 | 0.26702 | 4 | 50.0 | -1.343 | 1.51172 | -0.132064 | -0.585079 | -0.766850 | 29/30 |
| reversion-recovery-wide | 0.593726 | 0.19818 | 4 | 50.0 | 1.385 | 1.51205 | 0.140164 | -0.312571 | -0.494949 | 26/30 |
| momentum-short | 0.936567 | 0.27320 | 3 | 33.3 | 6.420 | 1.01192 | 0.632670 | 0.329097 | -1.039979 | 31/34 |
| momentum-medium | 0.805256 | 0.36097 | 3 | 33.3 | 4.646 | 1.01133 | 0.501254 | 0.198222 | -0.271421 | 29/34 |
| reversion-sustained | 0.601670 | 0.22211 | 4 | 50.0 | 1.464 | 1.51207 | 0.148182 | -0.304481 | -0.495017 | 26/30 |

Costs include integer-rounded fees, slippage and next-open constant-product
impact at recorded depths. Research stress multiplies BOTH the 4 bps fee and
2 bps slippage; pool impact is unchanged. The official grader's separate
2x-FEES-only replay gives -0.011108 USDC for the selected bot; this is not the
same experiment as the research 2x-costs column. Fees at 1x were 0.604948 USDC.
Research PnL and every production reply were compared with the official grade.
The official Docker driver executed Python twice and L1 rescoring matched.
Our Linux host Node is 22.21.1; the server reports 26.13.1, so result digests
cannot be claimed equal across hosts. The Python container is kit-pinned.

Trades in this table mean completed round trips; official trades mean fills
(8 for the selected bot). Win rate is winning completed round trips / all
round trips. Edge is the arithmetic mean of (net trade profit / entry cash)
in bps, including the $5 probe. Turnover sums entry cash and net sell proceeds,
divided by initial $1,000 equity. Max drawdown uses bar-close marks and the
terminal liquidation mark. Without best subtracts the best realized trade
from the original PnL; it does not simulate a different compounding path.

## Fresh-state splits

| Candidate | Half 1 | Half 2 | Third 1 | Third 2 | Third 3 |
|---|---:|---:|---:|---:|---:|
| reversion-recovery | 1.736895 | -1.418354 | 1.078573 | 0.658277 | -1.413206 |
| reversion-recovery-wide | 2.010143 | -1.418354 | 2.010143 | -0.011852 | 0.151542 |
| momentum-short | 0.936567 | -0.005145 | -0.009329 | -1.040093 | -0.011896 |
| momentum-medium | 0.805256 | -0.005145 | -0.009329 | -0.273416 | -0.011896 |
| reversion-sustained | 2.018155 | -1.418354 | 2.018155 | -0.011852 | -0.009348 |

Each half/third starts with $1,000 and empty indicators, uses no earlier bars,
and liquidates its remaining position at its endpoint. Each incurs its own
participation fallback. They are subperiod sensitivity checks, not independent
out-of-sample tests: the whole day was already available in research.

## Plateau audit

Every numeric parameter was changed individually to 75% and 125%, with integer
parameters rounded and valid RSI bounded at 100. No cross-product grid was
searched. For the selected reversion bot, 26/30 neighbors of parameters used
by this strategy are profitable (34/38 counting momentum-only parameters).
Worst is -1.460849 USDC. Failures occur at both 68- and 112-bar holding
timeouts and cost-hurdle multiples 2.25 and 3.75. Many neighbors do not
change any order because a gate is inactive in this day. Thus a large fraction
of profitable neighbors overstates the evidence for a useful plateau.

## Chosen parameters and mechanics

- Mean/volatility history: 120 observed bars; vol is RMS close-return bps.
- Entry: mean/close deviation at least max(3x estimated round-trip cost,
  0.6 x RMS volatility x sqrt(120)); close above its close two observations ago.
- Volatility gate: 0.5 through 50 bps per bar. No volume exists, so the mean is
  equally time weighted over observed closes; calling it VWAP would be false.
- Estimated round-trip cost: 2 x (fee + slippage + stake/depth in bps), using
  the latest close depth. At $250 and $795k depth it is about 18.3 bps; the
  entry hurdle is about 54.9 bps. This is a hurdle, not a proven expectation.
- Stake: 25% of available cash; never add to an existing position.
- Exit: frozen entry mean recovered, 90 bars after fill, or value at/below
  99% of recorded entry cash. Orders fill one bar later.
- Cooldown: 15 batch steps after a sell fill. Permanent 5% equity-peak
  drawdown kill closes the position and disables new entries.
- Participation fallback: after seq 120 if no buy has filled, buy 0.5% of
  cash (initially $5), subject to 150 bps entry slippage, then send a full
  exit one batch after fill. It intentionally pays a small cost; no profitable
  edge is claimed for it. It retries rejected entries on subsequent bars.
- Normal slippage cap 150 bps. Stop/kill exits accept up to 10,000 bps to
  prioritize flattening. Positions still held at the end flatten officially.

## Verification and key risks

Production imports only json, math and sys. It reads protocol stdin, writes
stdout, and keeps bounded process state. No network, clock, randomness,
environment reads, additional file opens or third-party dependencies are used.
Two direct Python process runs must produce identical bytes, and parsed
replies must equal the official action log. Flat-price and drawdown-shock
checks cover the fallback and permanent kill switch. Research scripts live
outside this shipped repository and are not imported by the running bot.

The sample has only three full-size trades and one small probe. There is no
credible confidence interval for unseen daily PnL. The kit's bootstrap samples
symbols; with one symbol it reports a degenerate interval, which is not useful
evidence about time-series uncertainty. Selection on this same day adds bias.
Mean reversion can buy into persistent declines. A next-open gap, lost bars or
liquidity collapse can overshoot stop/kill levels. Five percent is a trigger,
not a guaranteed drawdown bound. The fallback guarantees an attempted small
entry on a sufficiently long window; no bot can guarantee a fill on arbitrary
missing-bar or rejecting markets. No claim of likely race profitability is made.

Public repository creation, About metadata, push and submission are left for
the owner as requested. Nothing has been submitted and no quota was consumed.

Risk audit: [RISK_AUDIT.md](RISK_AUDIT.md) compares 25%, 35% and 50% sizing on 1,500 synthetic paths (4,500 paired replays). All bootstrap medians are negative; retain 25% sizing and 5% kill. Cumulative totals: 186 configurations / 5,405 research replays. These are one-day conditional scenarios, not race forecasts.
