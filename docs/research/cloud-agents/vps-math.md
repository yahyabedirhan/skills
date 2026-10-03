# How much machine five parallel agents need

This page holds the math behind decision [D4](README.md#d4-resize-the-vps). We redid it on **2026-10-02**, after the maintainer tried the current VPS and set a budget. Where this page and [vps-sizing.md](vps-sizing.md) disagree, this page replaces that file's sizing rule. This page also adds per-core speed. That file and [vps-providers.md](vps-providers.md) left it out. Provider details, latency and the steps to switch stay in those files.

The evidence tags are the same as in the sizing file:

- **[doc]**: a provider's page.
- **[api]**: its public catalogue.
- **[mac]**: a read-only command on the Mac.
- **[bench]**: a published Geekbench 6 result.
- **[user]**: what the maintainer reported.
- **Estimate**: a figure we derived here, with the working shown.

Prices are per month and **net of VAT**. We converted them at the ECB rate of 2026-10-01, **€1 = $1.13** [doc: [ECB reference rates](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml)]. A buyer in the EU adds their country's VAT.

## What the maintainer asked and reported

- **Goal:** about **5 agents at once** (Claude Code, Codex or Cursor), one per feature. Each agent runs sub-agents that run commands and tests in parallel. This includes **browser tests** (Playwright). The agents work much as they do on the Mac.
- **Budget:** the maintainer pays about **$6** today. The next step is **$10-15**. They would go to **about $20** if the gain over $10-15 is clear.
- **Today's VPS, Hetzner CX23, as observed [user]:** it can't run one agent properly. It can't run work in parallel. It can't run a browser test or an ordinary test suite properly.
- **Corrections to the earlier files [user]:**
  - The rescale dialog doesn't offer **CX33**, which the earlier files called the "cheapest step up".
  - It offers the Regular Performance line from **CPX12**, and dedicated cores from **CCX13** at about $50.
  - The Cost-Optimized line (CX, CAX) is unavailable. That line suits light REST backends, not agents that run tests and browsers.

The provider's pages agree. On 2026-10-02, Hetzner's Cost-Optimized page still marks all 8 CX and CAX rows "not available". The Regular Performance and General Purpose pages mark none [doc].

## 1. The two numbers that matter

A plan's "2 vCPU, 4 GB" hides the two quantities that decide whether agents work:

1. **Memory (GB), a hard limit.** Everything that runs at the same moment must fit. Today's VPS runs Linux with no swap. There, too much memory use **kills a process**. It doesn't slow down. The Mac never hits this wall, because macOS compresses memory and swaps (see below).
2. **CPU throughput, a speed limit.** It decides **how long** a test run takes, not whether it runs. It has two parts:
   - **single-core speed**: how fast one serial step runs (type-checking, one test file, rendering one page);
   - **multi-core speed**: how fast a parallel test suite finishes, or several agents' test runs at once.

"vCPU" counts neither of these. A vCPU is one hardware thread on someone else's server. Its speed varies about **3x** between plans (see below). So this page measures CPU as a **share of your Mac**. It uses Geekbench 6 (GB6), a cross-platform benchmark that publishes results per machine.

## 2. The baseline: your Mac [mac]

| | Value |
|---|---|
| Machine | Apple **M3 Pro**, 11 cores (5 performance + 6 efficiency), **18 GB** |
| GB6 single-core / multi-core | **3,089 / 14,029** (average of 16,046 results for this model) [bench: [Geekbench Browser, MacBook Pro 14-inch Nov 2023 M3 Pro](https://browser.geekbench.com/macs/macbook-pro-14-inch-nov-2023-11c-cpu-14c-gpu)] |
| Claude Code sessions running | **13**, each **280-660 MB** with its compressed pages counted (`top -stats mem,cmprs`). Together they use **5.2 GB**, about **400 MB** each |
| Memory the Mac is holding | Resident plus compressed memory adds up to about **41 GB** across all processes, on 18 GB of RAM. This is an over-count, because each process counts its shared pages again. The compressor holds **21 GB** of pages in 6.3 GB (`vm_stat`). **4.9 GB** of 6 GB swap is in use |
| Load average | 4.8 / 4.0 / 3.8, out of 11 cores |

What this means for a server:

- **An agent session costs about 0.4 GB, up to 0.65 GB.** The earlier Linux figure agrees (369 MB, 511 MB peak on the VPS). Claude Code sub-agents run inside the session's process. So they add to that figure and don't start new sessions. What they **start** costs memory: tests, builds and browsers.
- **The Mac copes with 18 GB because it compresses about 3:1 and swaps.** A stock Linux server does neither. Its RAM must hold everything uncompressed. If you turn on **zram** (compressed RAM) and a swap file on the server, you get part of that back (section 6).

## 3. What each part of the workload costs

| Unit | Memory | CPU | Source |
|---|---|---|---|
| System, Herdr, the box's own services | **1 GB** | ~0 | VPS measured 0.9 GB [sizing file] |
| One agent session (Claude Code, Codex, Cursor CLI), sub-agents included | **0.6 GB** (0.4 typical, 0.65 peak) | about 0 while it waits on the model | [mac] above. Codex's vendor floor is 4 GB per **machine**, not per session [doc: [Codex install](https://github.com/openai/codex/blob/main/docs/install.md)] |
| One test run (Node test runner with workers, type-checker, or a build) | **2 GB** | every core it gets, for seconds to minutes | Estimate: GitHub's standard Linux runner gives 2 CPU / 8 GB to one job [doc: [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)]. Node test runners start roughly one worker per core |
| One headless browser (Playwright Chromium, a few pages) | **1 GB** | spiky: one busy page fills a core | [mac] 18 Chrome processes average 226 MB each with compression counted. The sizing file gives 0.5-1 GB |

**The rule:** RAM needed = 1 + 0.6 × agents + 2 × test runs at the same moment + 1 × browsers at the same moment. Keep 20% free.

**How many test runs overlap?** Agents spend most of their time waiting on the model. So five agents rarely all test at the same moment. Say each agent runs tests a quarter of the time. Then the chance that 3 or more of 5 test at once is 10%. The chance that 4 or more do is under 2% (binomial, n = 5, p = 0.25). Sub-agents that test in parallel raise the overlap. So: **plan for 2-3 overlapping test runs. Plan for 5 only for comfort.**

| Level | What runs at the same moment | RAM sum | Machine |
|---|---|---|---|
| **Floor: it works, but tests take turns** | 5 agents, 1 test run, 1 browser | 1 + 3 + 2 + 1 = **7 GB** | **8 GB**, with zram, no margin |
| **Target: your workflow, normal day** | 5 agents, 3 test runs, 2 browsers | 1 + 3 + 6 + 2 = **12 GB** | **16 GB** |
| **Comfortable: everyone tests at once** | 5 agents, 5 test runs, 5 browsers | 1 + 3 + 10 + 5 = **19 GB** | **24-32 GB** |

The inverse table shows what fits in each size, with 20% kept free:

| RAM | Fits |
|---|---|
| 4 GB (today) | 1 agent and a browser, but **not** a test run. 1 + 0.6 + 2 = 3.6 GB is already over the 3.2 GB that keeps 20% free. With no swap, the overflow kills a process. This matches what the maintainer saw [user] |
| 8 GB | 5 agents with one test run at a time and no browser, or 1-2 agents with one test run and one browser |
| 12 GB | 5 agents, 2 test runs and 1 browser at once |
| 16 GB | 5 agents, 3 test runs and 2 browsers at once |
| 24 GB | 5 agents, 5 test runs and 3 browsers at once |
| 32 GB | everything in the comfortable row, with room to spare |

## 4. CPU: how much slower than the Mac

**Two ratios** turn GB6 scores into time:

- A **serial step** (one test file, type-checking) takes `Mac single-core ÷ server single-core` times as long.
- A **parallel test suite** that would spread across all the Mac's cores takes up to `Mac multi-core ÷ server multi-core` times as long. When **k** suites overlap, each takes up to k times that. This is a worst case. Many suites use fewer cores than the Mac has, so the gap is smaller in practice.

The table gives GB6 results per plan, for the current generation where someone published them. Each Hetzner and netcup root-server figure is the median of two runs from one public table [bench: [derhuerst, "VPS price & performance comparison", Geekbench 6 table](https://gist.github.com/derhuerst/4ef9a832e031bf82d6e640e2dd6b2d24), revision of 2026-09-07; each figure links to its Geekbench Browser result there]. "Estimate" rows scale a measured sibling plan and give the working.

| Plan | Cores | GB6 single | GB6 multi | Share of Mac (multi) | A 1-minute Mac suite takes | Serial step slower by | Source |
|---|---|---|---|---|---|---|---|
| **Mac M3 Pro** | 11 | 3,089 | 14,029 | 100% | 1 min | 1x | [bench] |
| **Hetzner CX23 (today)** | 2 shared | 714 | 1,253 | **9%** | **11 min** | **4.3x** | [bench] |
| Hetzner CPX12 | 1 shared | 1,897 | 1,890 | 13% | 7.4 min | 1.6x | [bench] |
| Hetzner CPX22 | 2 shared | 1,852 | 3,357 | 24% | 4.2 min | 1.7x | [bench] |
| Hetzner CPX32 | 4 shared | 2,002 | 6,417 | 46% | 2.2 min | 1.5x | [bench] |
| Hetzner CCX13 | 2 dedicated | 1,859 | 2,334 | 17% | 6.0 min | 1.7x | [bench] |
| Hetzner CX33 / CX43 (unavailable) | 4 / 8 shared | 1,372 / 1,302 | 4,483 / 6,938 | 32% / 49% | 3.1 / 2.0 min | 2.3x / 2.4x | [bench] |
| OVHcloud VPS-2 | 4 shared | ~920 | ~2,600 | ~19% | ~5.4 min | ~3.4x | [bench] for the 2026 VPS-1, which had the same 4 cores / 8 GB / 75 GB. Nobody has confirmed that the 2027 VPS-2 runs on the same hardware |
| OVHcloud VPS-3 / VPS-4 | 6 / 8 shared | ~920 | ~3,800 / ~5,000 | ~27% / ~36% | ~3.7 / ~2.8 min | ~3.4x | Estimate: VPS-2's ~650 per core, × 6 or × 8 |
| netcup VPS 1000 G12.5 | 4 shared | ~1,650 | ~5,000 | ~36% | ~2.8 min | ~1.9x | Estimate: the 2-core VPS 500 G12 measured 1,650 / 3,008 [bench]. 4 cores at about 1,250 each |
| netcup VPS 2000 G12.5 | 8 shared | ~1,650 | ~8,500 | ~61% | ~1.7 min | ~1.9x | Estimate: 8 cores at about 1,060 each. Multi-core speed scales less than linearly, as Hetzner's CX33 → CX43 shows |
| netcup VPS 4000 G12.5 | 12 shared | ~1,650 | ~11,000 | ~78% | ~1.3 min | ~1.9x | Estimate, same method |
| netcup RS 1000 G12.5 | 4 dedicated EPYC 9645 | ~2,250 | ~7,000 | ~50% | ~2.0 min | ~1.4x | Estimate: the 12-core RS 4000 G12 (same CPU) measured 2,250 / 14,060 [bench]. 4 cores at ~3.1x single-core, the ratio that Hetzner's 4-core CPX32 shows |
| netcup RS 2000 G12.5 | 8 dedicated | ~2,250 | ~10,000 | ~71% | ~1.4 min | ~1.4x | Estimate, same method |
| netcup RS 4000 G12 | 12 dedicated | 2,250 | 14,060 | **100%** | 1.0 min | 1.4x | [bench] |

What it shows:

- **Today's CX23 is about one eleventh of the Mac.** A test suite that takes 1 minute on the Mac can take up to 11 there. Each serial step takes 4.3 times as long. Add 4 GB of RAM with no swap, and the numbers predict the four failures that the maintainer reported [user].
- **Per-core speed varies 3x** between plans that all say "vCPU": CX23 714, OVH ~920, netcup VPS ~1,650, Hetzner CPX/CCX ~1,850-2,000, netcup RS ~2,250, Mac 3,089.
- **CPX12, the plan that Hetzner offers next, isn't an upgrade for this workload.** Its one core is faster. But it has **half the RAM** (2 GB) and only one core. So it runs fewer agents than today, for twice the price.

## 5. The options by price point

| Price point | Plan | Monthly (net) | RAM | CPU vs Mac | What it gets you |
|---|---|---|---|---|---|
| **Today, $6** | Hetzner CX23 | €5.99, **$6.77** | 4 GB | 9% | One agent with no tests. The maintainer saw it fail to cope [user] |
| **$10-15** | **netcup VPS 1000 G12.5**: 4 vCores, 128 GB disk | €12.18 on a 12-month term, **$13.76**. €14.02 month to month, $15.84 | 8 GB | ~36%. Per-core 2.3x today | **The floor.** 1-2 agents with one test run and one browser, or 5 agents whose tests take turns. 4x today's CPU |
| $10-15 | OVHcloud VPS-3: 6 vCores, 100 GB | €12.24 month to month, **$13.83**. €10.40 on 12 months, $11.75 | 12 GB | ~27%. Per-core 1.3x today | More room (5 agents, 2 test runs, 1 browser) on slower cores. No term needed |
| $10-15 | Hetzner CPX12 | €11.99, $13.55 | 2 GB | 13% | **Not an upgrade**: less RAM than today |
| **About $20-25** | **netcup VPS 2000 G12.5**: 8 vCores, 256 GB | €22.62 on 12 months, **$25.56**. €26.02 month to month, $29.40 | 16 GB | ~61% | **The target.** 5 agents, 3 test runs and 2 browsers at the same moment |
| ~$20-25 | netcup RS 1000 G12.5: 4 **dedicated** cores, 128 GB | €18.26 on 12 months, **$20.63**. €21.01 monthly, $23.74 | 8 GB | ~50%, steady | Fast and steady per core. But it has the same 8 GB as the $14 plan, so it doesn't add agents |
| ~$20-25 | OVHcloud VPS-4: 8 vCores, 200 GB | €23.49 month to month, **$26.54**. €19.96 on 12 months, $22.55 | 24 GB | ~36% | Most memory in this range, with no term. Tests run at about half the speed of netcup's VPS 2000 |
| ~$20-25 | Hetzner CPX22 | €19.99, $22.59 | 4 GB | 24% | Faster cores, **same 4 GB**: still one agent |
| $40-50 | netcup VPS 4000 G12.5: 12 vCores, 512 GB | €38.12 on 12 months, **$43.08**. €43.83 monthly, $49.53 | 32 GB | ~78% | **Comfortable**: everyone tests with a browser at once |
| $40-50 | netcup RS 2000 G12.5: 8 dedicated | €34.20 on 12 months, $38.65 | 16 GB | ~71%, steady | The earlier recommendation: the target's memory with steady cores |
| $40-50 | Hetzner CPX32 / CCX13 | €35.99, $40.67 / €43.49, $49.14 | 8 GB | 46% / 17% | Hetzner's cheapest 8 GB today. Poor value next to netcup |

Price sources:

- netcup: the [VPS](https://www.netcup.com/en/server/vps) and [root server](https://www.netcup.com/en/server/root-server) pages, read 2026-10-02 [doc]. The pages show prices with 19% VAT. We divided them by 1.19 here.
- OVHcloud: its public order catalogue, `vps-2027-model{2,3,4}`, read 2026-10-02 [api].
- Hetzner: the price feed as the sizing file tabulates it. We re-read the specs on 2026-10-02 [doc].

The terms, the money-back guarantee and the steps to switch are in [vps-providers.md](vps-providers.md).

### $10-15 against about $25: what the extra $12 buys

| | netcup VPS 1000 ($13.76) | netcup VPS 2000 ($25.56) |
|---|---|---|
| RAM | 8 GB | **16 GB, 2x** |
| What fits at once | 5 agents with 1 test run at a time, or 1-2 agents with a test run and a browser | 5 agents with **3** test runs and 2 browsers |
| CPU | 4 vCores, ~36% of the Mac | 8 vCores, ~61% of the Mac, **1.7x** |
| A 1-minute Mac suite, alone | ~2.8 min | ~1.7 min |
| The same suite, with 3 running at once | can't: no room for 3 | ~5 min each (worst case) |
| Disk | 128 GB | 256 GB |
| Same provider, location and latency | yes | yes |

The $13.76 plan makes **one agent work properly** and lets five exist. The $25.56 plan lets **five work at once**. The goal is five in parallel, so **16 GB is the minimum that meets it**. Both plans are in the same product line. netcup lets you upgrade within a line and generation from its control panel [doc]. So you can start at VPS 1000 and move up later.

## 6. Two things that help at any size

- **zram and a swap file.** A compressed-RAM device (zram) plus a 4-8 GB swap file turn out-of-memory kills into slowdowns. The Mac's compressor does the same today. Idle agent sessions compress well. This is a config change on the server, so it needs the go-ahead. Do it on the new machine as part of set-up.
- **Cap test workers.** By default, Node test runners start about one worker per core. A shared server runs several agents. There, a cap keeps three overlapping suites from fighting over the same cores. Examples are Vitest's `--maxWorkers`, Jest's `--maxWorkers` and Playwright's `--workers`. We haven't checked which runners these repos use.

## 7. Recommendation

- **Within the $20ish stretch: netcup VPS 2000 G12.5, $25.56 a month on 12 months** ($29.40 month to month).
  - The x86 VPS has **no** money-back guarantee. netcup gives one only on Root Server and ARM plans [doc]. So the month-to-month term is the trial.
  - It is the cheapest plan that fits the target row (16 GB). It has about 7x today's CPU, and each of its cores is 2.3x faster.
- **If $15 is the ceiling: netcup VPS 1000 G12.5, $13.76.** Accept that tests take turns. Move up to VPS 2000 later from the control panel.
- **Not:** Hetzner CPX12 (less RAM than today) or CPX22 (same RAM, three times the price). Today Hetzner has no plan under $40 that adds memory.
- **Later, for comfort:** netcup VPS 4000 (32 GB, $43.08), when five agents often test at the same moment.

- **Update, later on 2026-10-02:** the maintainer moved the goal to 3 agents and a monthly trial (no 12-month term). The plan is now **netcup VPS 1000 G12.5 on the 1-month term, $15.84**. If memory runs short, upgrade in place to VPS 2000. If shared cores slow the tests (high steal), rebuild on RS 1000. Section 8 has the full comparison. D4 stays undecided until the maintainer orders.

## 8. Every option against today

We added this section on 2026-10-02. The maintainer had made three changes:

- moved the goal to **3 agents in parallel**;
- asked for **monthly terms with no long contract**;
- asked to see each option as an upgrade multiplier over the current CX23.

How to read the table:

- **Baseline (1x):** Hetzner CX23, $6.77, 4 GB, GB6 714 single-core / 1,253 multi-core [bench].
- **Prices:** the shortest term each provider sells, net of VAT, in USD at €1 = $1.13. netcup shows this maintainer "incl. 0% VAT", so the net price is what they pay.
- **RAM ×** decides how many agents and test runs fit at once.
- **1-core ×** decides how fast each serial step runs (a type-check, one test file, a page render).
- **Total CPU ×** decides how fast parallel test runs finish.
- **Today's 10-min suite** is 10 ÷ total-CPU ×. This is a worst case for a suite that spreads over all cores.
- **3 agents** uses section 3. 8 GB is the floor (tests take turns). 12 GB is the target (two test runs overlap). 16 GB or more is comfortable.
- **~** marks an estimate scaled from a measured sibling plan. The other figures are published Geekbench 6 results (sources under the table).

| Band | Plan | $/mo | +$/mo | RAM | **RAM ×** | **1-core ×** | **Total CPU ×** | Today's 10-min suite | 3 agents | Terms |
|---|---|---|---|---|---|---|---|---|---|---|
| **Today** | Hetzner CX23 | 6.77 | — | 4 GB | **1x** | **1x** | **1x** | 10 min | ✗ | Hourly |
| $10 | ⭐ netcup Lite 2 | 9.02 | +2.25 | 8 GB | **2x** | 1.6x | 3.0x | 3.3 min | Floor | 3-month minimum |
| $10 | OVHcloud VPS-2 | 9.59 | +2.82 | 8 GB | **2x** | ~1.3x | ~2.1x | ~4.8 min | Floor | Month to month |
| $10 | netcup VPS 500 | 9.02 | +2.25 | 4 GB | 1x | 2.3x | 2.4x | 4.2 min | ✗ | Month to month |
| $15 | ⭐ **netcup VPS 1000** | 15.84 | +9.07 | 8 GB | **2x** | ~2.3x | ~4.2x | ~2.4 min | Floor | Month to month |
| $15 | netcup Lite 3 | 15.82 | +9.05 | 16 GB | **4x** | 1.6x | 4.2x | 2.4 min | Comfortable | 2-month minimum |
| $15 | OVHcloud VPS-3 | 13.83 | +7.06 | 12 GB | **3x** | ~1.3x | ~3.0x | ~3.3 min | Target | Month to month |
| $15 | netcup RS 500 | 14.11 | +7.34 | 4 GB | 1x | ~2.8x | ~2.4x | ~4.2 min | ✗ | Month to month, refund |
| $15 | Hetzner CPX12 | 13.55 | +6.78 | 2 GB | **0.5x** | 2.7x | 1.5x | 6.6 min | ✗ | Hourly |
| $20 | ⭐ netcup RS 1000 | 23.74 | +16.97 | 8 GB | **2x** | ~2.8x | ~5.6x | ~1.8 min | Floor | Month to month, refund |
| $20 | UpCloud Starter 8 GB / 4 cores | 22.60 | +15.83 | 8 GB | **2x** | not published | not published | not published | Floor | Hourly |
| $20 | Hetzner CPX22 | 22.59 | +15.82 | 4 GB | 1x | 2.6x | 2.7x | 3.7 min | ✗ | Hourly |
| $20 | Vultr / DigitalOcean basic | 20-24 | +13-17 | 4 GB | 1x | ~1-1.3x | ~1x | ~10 min | ✗ | Hourly |
| $25-30 | ⭐ netcup VPS 2000 | 29.40 | +22.63 | 16 GB | **4x** | ~2.3x | ~6.8x | ~1.5 min | Comfortable | Month to month |
| $25-30 | OVHcloud VPS-4 | 26.54 | +19.77 | 24 GB | **6x** | ~1.3x | ~4.0x | ~2.5 min | Comfortable | Month to month |
| $25-30 | netcup Lite 4 | 29.30 | +22.53 | 32 GB | **8x** | ~1.5x | ~6.7x | ~1.5 min | Comfortable | Month to month |
| $25-30 | UpCloud Starter 16 GB / 2 cores | 27.12 | +20.35 | 16 GB | **4x** | not published | not published | not published | Comfortable | Hourly |
| *Reference* | *the Mac, M3 Pro* | — | — | 18 GB | *4.5x* | *4.3x* | *11.2x* | *0.9 min* | — | — |

⭐ = the pick in each band.

What it shows:

- **The $15 pick, netcup VPS 1000, gives 2x the memory, 2.3x per core and 4.2x total CPU for about +$9 a month.** A suite that takes 10 minutes today should take about 2.4.
- **Lite 3 costs the same with 4x the memory** and the same 4.2x total CPU. But its cores are only 1.6x today's, so every serial step stays slow. The maintainer ranks CPU speed first, so it isn't the pick.
- **Each band up roughly doubles one dimension.** RS 1000 (+$8 over VPS 1000) adds per-core speed and steadiness. VPS 2000 (+$14 over VPS 1000) adds memory and total CPU.
- **Even the best plan here is about half the Mac:** 6.8x today's CPU against the Mac's 11.2x.
- **The ✗ rows add no memory** (CPX12 even halves it). So the out-of-memory kills that the maintainer saw would continue, however fast the cores are.

Sources beyond sections 4 and 5:

- netcup VPS Lite 2 G12s: 1,144 / 3,761 [bench: [VPSBenchmarks yabs, 2026-01-28](https://www.vpsbenchmarks.com/yabs/netcup-4c-8gb-20260128-90c0cc)]. Lite 3 G12s: 1,110 / 5,254, shown as "QEMU Virtual CPU" at 2.0 GHz, Nuremberg [bench: [VPSBenchmarks yabs, 2026-08-12](https://www.vpsbenchmarks.com/yabs/netcup-8c-16gb-20260812-139cba)]. These runs used the G12s generation. We assume the G12.5s plans now on sale are similar (unverified).
- netcup VPS 1000 G12: 1,615-1,641 / 5,045-5,412 across three published runs. This confirms section 4's estimate (~5,000) [bench: [netcupvoucher.com, citing VPSBenchmarks](https://netcupvoucher.com/blog/netcup-vps-g12-is-out); [LowEndTalk thread](https://lowendtalk.com/discussion/212781/netcup-g12-rootserver-underperforming)].
- netcup root servers G12: on the 8-core size, buyers report 1,817-2,100 single-core and about 10,900-11,000 multi-core. That is a little above section 4's ~10,000 estimate for RS 2000. The same thread reports one root server that arrived at 328 / 1,408, and the buyer returned it for a refund. So benchmark a new server in its first week [bench: [LowEndTalk thread](https://lowendtalk.com/discussion/212781/netcup-g12-rootserver-underperforming)].
- RS 500 and RS 1000 multi-core: estimates (2 and 4 dedicated cores, scaled from those results). Lite 4: Lite 3's per-core result × 16 cores, discounted for scaling (estimate).
- Lite prices: [netcup vServer Lite](https://www.netcup.com/en/server/vps-lite), 2026-10-02 (€5.86, €9.50, €16.66 and €30.86 including 19% VAT, for Lite 1-4) [doc]. 1-month prices for VPS 500 (€7.98) and RS 500 (€12.49), net: the maintainer read them on [netcup deals](https://www.netcup.com/en/deals) [user].
- UpCloud Starter, Vultr and DigitalOcean: [vps-providers.md](vps-providers.md#2-the-providers-at-8-gb-and-16-gb) (prices of 2026-09-30). The Vultr and DigitalOcean CPU figures are for 2-core plans from the [benchmark gist](https://gist.github.com/derhuerst/4ef9a832e031bf82d6e640e2dd6b2d24).
- Left out:
  - Contabo, Hostinger and IONOS publish only long-term or upfront prices, with no plain monthly rate.
  - Scaleway costs more than $28 for 8 GB before storage and IPv4.
  - Hetzner's CX line is still unavailable.

## 9. netcup's four lines

netcup sells its servers in four lines. The lines differ in four ways:

- what CPU you get;
- whether the CPU is shared;
- how long you commit;
- whether you can return the server.

The row "Each core vs today's" uses section 8's 1-core × figures.

| | **vServer Lite** | **vServer VPS** | **vServer ARM64** | **Root Server** |
|---|---|---|---|---|
| **In one line** | Cheapest RAM, older hardware | Standard VPS, current hardware | Same as VPS, on Arm chips | Your cores are reserved for you |
| **Built for** | Light, steady workloads (websites, small services) | General use | Power-efficient Arm workloads | CPU-heavy work that needs steady speed |
| **CPU** | Unnamed older chip, about 2.0 GHz | AMD EPYC (current generation) | Ampere Altra Max (Arm) | AMD EPYC 9645 (newest) |
| **Shared or dedicated** | Shared | Shared | Shared | **Dedicated** |
| **Each core vs today's** | ~1.6x | ~2.3x | ~1.3x | ~2.8x |
| **RAM per $** | **Most** (16 GB for $15.82) | Medium (8 GB for $15.84) | Same as VPS | **Least** (8 GB for $23.74) |
| **Monthly term** | Fixed minimum per plan: 6, 3, 2 or 1 months | 1, 12 or 24 months | 12 or 24 months | 1, 12 or 24 months |
| **30-day refund** | No | No | Yes | **Yes**, plus a 99.9% uptime guarantee |
| **Upgrade path** | Only within Lite | Within VPS (1000 → 2000 → 4000) | Within ARM | Within Root Server |
| **Network** | 1 Gbps. netcup throttles it to 100 Mbps if the 24-hour average exceeds 100 Mbps | 2.5 Gbps, throttled above 2 TB a day | 2.5 Gbps, throttled above 2 TB a day | 2.5 Gbps, throttled above 3 TB a day |
| **Location** | No choice | You choose | You choose | You choose |
| **Software** | x86: everything runs | x86: everything runs | Arm: some x86-only tools and Docker images won't run | x86: everything runs |

The network limits don't matter for agents, because agents move very little data.

The trade, in short:

- **Lite** gives the most memory for the money, but each step runs slower. It is good when you need room more than speed.
- **VPS** is the balance: fast shared cores at a fair price, with no refund.
- **ARM64** costs the same as the VPS, with slower cores and some compatibility risk. It has no advantage for this use.
- **Root Server** is the fastest and most predictable per dollar of CPU. It is the only x86 option with a refund. But it gives the least memory per dollar.

This maintainer wants CPU speed first and a cheap monthly start. So the **VPS** line fits, starting at VPS 1000. Lite would fit if memory mattered more than speed. A Root Server is worth it if the trial shows shared cores slowing tests. **Each line upgrades only within itself.** A move between lines is a new order and a rebuild.

Sources:

- The plan detail pages for [VPS Lite 3](https://www.netcup.com/en/server/vps/vps-lite-3-g12.5s-iv-2m), [VPS 2000](https://www.netcup.com/en/server/vps/vps-2000-g12.5-iv-24m-eu), [VPS 2000 ARM](https://www.netcup.com/en/server/arm-server/vps-2000-arm-g12.5-iv-24m-eu) and [RS 2000](https://www.netcup.com/en/server/root-server/rs-2000-g12.5-iv-24m-eu), read 2026-10-02 [doc]. They give the network, throttling, location and guarantee.
- The VPS page says the VPS doesn't include "the dedicated CPU cores, the satisfaction guarantee and the very high guaranteed minimum availability of 99.9%" [doc: [netcup VPS](https://www.netcup.com/en/server/vps)].
- The ARM page names "Ampere Altra Max CPUs" [doc: [netcup ARM](https://www.netcup.com/en/server/arm-server)].
- The Lite page says switching "between tariff groups (e.g. from VPS Lite G12.5s to VPS 1000 G12.5) is not possible via an upgrade" [doc].
- ARM per-core speed: the VPS 1000 ARM G11 measured 907 / 3,990 [bench: gist]. The ARM page is the source for the claim that G12.5 ARM uses the same Altra Max chip.

## Open questions

- TODO (proposed experiment): run Geekbench 6 or one of the repos' test suites on the CX23 and the new machine. This needs the go-ahead, because it runs on the VPS. Time it against the Mac. The results replace the estimated rows in section 4 with measurements.
- TODO: measure the peak RSS of one real test run and one Playwright run on Linux (`/usr/bin/time -v`). The results replace the 2 GB and 1 GB units.
- Unverified: the GB6 scores of netcup's G12.5 VPS and of OVHcloud's 2027 range. We found only the 2-core G12 VPS 500. Also unverified: whether either provider shares hosts as heavily as Hetzner's CX.
- Unverified: the maintainer's VAT status. EU buyers add VAT to every net price here.

## Exploration log

We ran everything on 2026-10-02. We ordered nothing, and we changed or ran nothing on the VPS. There were no log-ins.

| # | Where | Action | Changed |
|---|---|---|---|
| 1 | Mac, this worktree | Read the sizing, providers and guide files | nothing |
| 2 | Mac | `sysctl` (CPU, RAM, cores), `memory_pressure`, `vm_stat`, `sysctl vm.swapusage`, `ps` and `top -l 1 -stats pid,command,mem,cmprs,cpu`, grouped by process kind | nothing |
| 3 | Web | `curl` of Hetzner's price feed and its three cloud plan pages (specs and `not-available` marks) | scratch files outside the repo |
| 4 | Web | Exa search for Hetzner and M3 Pro Geekbench 6 results. GitHub API read of the benchmark gist and its comments | scratch files outside the repo |
| 5 | Web | `curl` of netcup's VPS and root-server pages, OVHcloud's public VPS catalogue and the ECB reference-rate file | scratch files outside the repo |
| 6 | Web | `curl` of netcup's vServer Lite and ARM pages, and of the detail pages of VPS Lite 3, VPS 2000, VPS 2000 ARM and RS 2000 (network, throttling, location, guarantee). Exa search for netcup Lite and G12 benchmarks | scratch files outside the repo |
