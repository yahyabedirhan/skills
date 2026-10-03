# VPS sizing, and cheaper or better places to run agents

Facts for [Research: VPS sizing and cheaper or better places to run agents (#72)](https://github.com/yahyabedirhan/skills/issues/72), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45) (user stories 20 and 21). The research and the price reads are from **2026-09-29**. Ticket #71 covers what an agent on the VPS can do compared with the Mac. [herdr-vps.md](herdr-vps.md) covers how Herdr reaches the VPS, and this page doesn't repeat it. Tickets #69 and #70 cover hosted cloud agents (Claude Code on the web, Codex, Cursor, Copilot). This page only sizes machines.

Evidence tags:

- **[doc]** vendor documentation or an official pricing page, linked inline.
- **[api]** a vendor's own public data feed or API, read without an account. These are Hetzner's price feed `https://www.hetzner.com/_resources/app/data/app/live_data_prices.json` (its pricing pages render from this file) and Vultr's `https://api.vultr.com/v2/plans` (public, no key).
- **[vps]** a read-only command on the VPS on 2026-09-29 (see the Exploration log). **[mac]** the same on the Mac.
- **Estimate** a figure derived from the above, with the working shown. **Unverified** has no primary source.

Currency:

- Hetzner prices are in EUR, **excluding VAT**. Its site shows net prices. It adds the buyer's country VAT when the buyer chooses a country, for example 19% for Germany.
- Hetzner prices are **including one primary IPv4** at €0.50/month. The pages say "Price incl. IPv4" [doc]. The feed prices the IPv4 separately as `CLOUD_21` [api].
- netcup prices are in EUR **including 19% VAT**.
- DigitalOcean, Vultr, Fly.io and GitHub prices are in USD, excluding tax.

> **Corrected 2026-10-02, see [cloud-agents-vps-math.md](cloud-agents-vps-math.md).** The maintainer's rescale dialog doesn't offer CX33. So "the cheapest real step up is CX33" no longer holds. The dialog offers CPX12 (2 GB) and up, and CCX13 for dedicated cores. The maintainer also found that CX23 can't run one agent with tests, a browser test or anything in parallel. This overrides this page's "carries one Claude Code session comfortably". The math file does the sizing again for five parallel agents. It measures the speed of each core against the Mac.

## Summary

- **Today's VPS is Hetzner's smallest shared x86 tier, CX23** (2 vCPU, 4 GB, 40 GB), €5.99/month [vps, api]. It carries one Claude Code session comfortably. 2.4 GB of RAM is still available, and the CPU was idle 97% on average over six weeks [vps].
- **RAM, not CPU, is the limit.** A Claude Code session holds about 0.15-0.5 GB [vps, mac]. Agents mostly wait on the model, so CPU only matters for builds, tests and browsers. The VPS has **no swap**. So when RAM runs out, the system kills processes instead of slowing them [vps].
- **The cheapest real step up is CX33** (4 vCPU, 8 GB, 80 GB) at €8.99/month, +€3.00 [api]. It fits two or three parallel agents, or one with a headless browser and builds. A rescale with "CPU and RAM only" lets it go back down. The rescale needs the server powered off [doc].
- **Hetzner's shared x86 line is still the cheapest per GB** of everything compared. DigitalOcean and Vultr ask $20-24 for the 2 vCPU / 4 GB size that costs €5.99 at Hetzner [doc, api]. netcup is close (€8.26 incl. VAT for 2 vCores / 4 GB). But netcup sells terms of 1-24 months, not hourly [doc].
- **On-demand machines pay off only for bursts.** Every VPS provider here bills a stopped server until you delete it [doc]. Fly.io bills a stopped Machine for its disk only, and GitHub bills a stopped Codespace for storage only [doc]. Take a big Hetzner server made from a snapshot, use it for a few hours, and then delete it. This costs cents (CX53, 16 vCPU / 32 GB: €0.0481/hour [api]).
- **One caveat: CX and CAX are hard to get right now.** On 2026-09-29 Hetzner's Cost-Optimized page marks all eight CX and CAX tiers "not available". The Create button's tooltip says "This product is currently unavailable. Please check back later." [doc]. This is a stock shortage, not a withdrawal:
  - Hetzner's status page has an open notice (since 2026-06-26). It restricts the creation of new cloud servers "for both new customers and some of our existing customers", chosen at random.
  - Its Cloud FAQ says an affected customer can't create **or rescale** servers at that location. Existing servers keep running [doc].

  So today's CX23 is safe. But Hetzner may refuse the CX23 → CX33 step until stock returns (details in [section 3](#availability-what-not-available-means)).

## 1. What resources an agent uses

### The VPS today [vps]

| | Value |
|---|---|
| Hardware | Hetzner "vServer", KVM guest, Intel Xeon (Skylake), x86_64, 2 vCPU |
| OS | Ubuntu 26.04 LTS |
| RAM | 3.8 GB total. 1.4 GB used, 2.5 GB buff/cache, **2.4 GB available** with one Claude Code session running |
| Swap | **none** |
| Disk | 38 GB root, 11 GB used (30%) |
| `/dev/shm` | 1.9 GB tmpfs (Chromium's shared memory). Docker's 64 MB default is the usual browser trap. It is not a problem here |
| CPU load | load average 0.06 / 0.16 / 0.17. Cumulative `/proc/stat` since boot (six weeks): about 3.3% busy, 0% steal |
| Memory pressure | `/proc/pressure/memory` all averages 0.00 now. A small cumulative stall total since boot shows that the box was short of memory at some point |
| Processes | one `claude` (Claude Code 2.1.283) at **369 MB RSS, 511 MB peak** (`VmHWM`). Herdr 22 MB. Everything else on the box (system services and a few containers and web services) about 0.5 GB. Sum of all RSS 0.9 GB |
| Browser | Playwright's `chromium_headless_shell` is already in the user's cache, but it can't start. 15 system libraries are missing. To try it needs an install as root or the Playwright Docker image (see [the VPS research](cloud-agents-vps.md)) |

The machine doesn't print its server type. But 2 x86 vCPU, 4 GB and a 40 GB disk on a Hetzner vServer is exactly CX23 [api].

### Per-process footprints

| Workload | Memory | CPU | Source |
|---|---|---|---|
| Claude Code, machine minimum | "4 GB+ RAM, x64 or ARM64" for the machine | not stated | [doc] [Claude Code setup](https://code.claude.com/docs/en/setup#system-requirements) |
| Claude Code, one session | VPS: 369 MB, peak 511 MB. Mac: 18 CLI processes, 119-480 MB each, 200 MB average | 1-2% when idle, about 16% of a core while working | [vps], [mac] |
| Codex CLI, machine minimum | "4-GB minimum (8-GB recommended)" | not stated | [doc] [Codex install](https://github.com/openai/codex/blob/main/docs/install.md) |
| opencode, one session | about 145-150 MB | under 1% idle | [mac] |
| Headless Chromium | Mac Chrome renderers 125-370 MB per tab, about 140 MB average over 19 processes. So **about 0.5-1 GB for one browser with a few pages** | spiky. One busy page can fill a core | [mac], estimate (headed Chrome on macOS. No vendor figure exists) |
| A typical CI build or test run | GitHub sizes its standard Linux runners at 2 CPU / 8 GB (private repos) and 4 CPU / 16 GB (public repos) | the whole machine while it runs | [doc] [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners). A reference size, not a measurement of these repos |

Notes:

- The tool processes that an agent starts (tests, `node`, `swift build`, a dev server) count on top of the session. They cause the peaks. This ticket ran no build on the VPS, because a build writes files. It is a proposed experiment below.
- macOS RSS undercounts compressed memory, so the Mac figures are a floor. The Linux VPS figure is the better guide for Linux.

### Sizing rule (estimate)

RAM ≈ the sum of:

- **1 GB** for the OS, Herdr and the box's other services.
- **0.5 GB per agent session** (its peak).
- **1 GB per headless browser**.
- **2 GB headroom per build or test run at the same time**.

With no swap, keep the sum under the machine's RAM. CPU: 1 vCPU per concurrent build or browser. Idle agents need almost none.

Check against today [vps]: 1 GB + one 0.5 GB session leaves about 2.3 GB on CX23. This matches the measured 2.4 GB `available`.

## 2. Workload to smallest tier

The table uses Hetzner shared x86 (CX) tiers, and the dedicated-core CCX line where sustained CPU matters. The RAM figures use the rule above.

| Workload | RAM needed (estimate) | Smallest tier that fits | Comfortable tier | Sources |
|---|---|---|---|---|
| 1 agent, no browser | about 1.5 GB, plus 2 GB when it builds | **CX23** (2 vCPU / 4 GB), today's tier | CX23 | [vps] measured. Claude Code needs 4 GB+ [doc] |
| 1 agent + headless browser | about 2.5 GB, 4.5 GB while building | CX23, with no build running alongside | **CX33** (4 vCPU / 8 GB) | [vps], [mac], estimate |
| 1 Codex agent | vendor says 4 GB min, 8 GB recommended | CX23 | **CX33** | [doc] Codex install |
| 2-3 agents, no browser | about 2.5 GB, 4.5-6.5 GB with builds | CX23 if they don't build at once | **CX33** | estimate |
| 2-3 agents, each with a browser | about 5.5 GB, 7.5 GB+ with builds | CX33 | **CX43** (8 vCPU / 16 GB) | estimate |
| 4-6 agents, some browsers, parallel builds | about 8-12 GB | CX43 | CX43. **CCX23** (4 dedicated vCPU / 16 GB) if builds run all day | estimate. CCX is dedicated vCPU [doc] |
| 8-10 agents with browsers and builds | about 16-25 GB | **CX53** (16 vCPU / 32 GB) | CX53, or CCX33 (8 dedicated / 32 GB) | estimate |

Shared vCPUs are fine for agents that mostly wait. Hetzner itself positions its dedicated General Purpose line (CCX) "for workloads with consistently high utilization" [doc]. For this use, that only means builds that run most of the day.

## 3. Hetzner's tiers

The prices come from Hetzner's price feed [api]. They match the plan tables on [Cost-Optimized](https://www.hetzner.com/cloud/cost-optimized/), [Regular Performance](https://www.hetzner.com/cloud/regular-performance/) and [General Purpose](https://www.hetzner.com/cloud/general-purpose/) [doc]. They are in EUR, net of VAT, incl. IPv4, per month (hourly in brackets). EU = Nuremberg, Falkenstein and Helsinki. The CX line lists NBG1 and HEL1 on its page. The feed also prices FSN1.

### Cost-Optimized: shared vCPU, Intel/AMD (CX) or Ampere Arm (CAX), EU only

| Tier | vCPU | RAM | Disk | EU price |
|---|---|---|---|---|
| **CX23** (today) | 2 | 4 GB | 40 GB | €5.99 (€0.0096/h) |
| CAX11 (Arm) | 2 | 4 GB | 40 GB | €6.49 (€0.0104/h) |
| **CX33** | 4 | 8 GB | 80 GB | €8.99 (€0.0144/h) |
| CAX21 (Arm) | 4 | 8 GB | 80 GB | €10.99 (€0.0176/h) |
| **CX43** | 8 | 16 GB | 160 GB | €16.49 (€0.0264/h) |
| CAX31 (Arm) | 8 | 16 GB | 160 GB | €21.49 (€0.0344/h) |
| **CX53** | 16 | 32 GB | 320 GB | €29.99 (€0.0481/h) |
| CAX41 (Arm) | 16 | 32 GB | 320 GB | €41.49 (€0.0665/h) |

On 2026-09-29 the page's static HTML marks every one of these rows "not available" [doc]. The Regular Performance and General Purpose pages mark none. The price includes 20 TB of traffic in the EU [doc]. [Availability](#availability-what-not-available-means) below explains what the mark means.

### Regular Performance: shared vCPU, AMD (CPX)

| Tier | vCPU | RAM | Disk | EU | Singapore |
|---|---|---|---|---|---|
| CPX12 | 1 | 2 GB | 40 GB | €11.99 | €15.99 |
| CPX22 | 2 | 4 GB | 80 GB | €19.99 | €26.99 |
| CPX32 | 4 | 8 GB | 160 GB | €35.99 | €49.49 |
| CPX42 | 8 | 16 GB | 320 GB | €69.99 | €93.99 |
| CPX52 | 12 | 24 GB | 480 GB | €100.99 | €134.99 |
| CPX62 | 16 | 32 GB | 640 GB | €130.49 | €172.49 |

US locations (Ashburn, Hillsboro) sell the older CPX11-51 [api]. The prices are CPX11 2 vCPU / 2 GB €17.99, CPX21 3 / 4 GB €32.49, CPX31 4 / 8 GB €62.99. The US price includes 1 TB of traffic, and Singapore 0.5-1 TB [doc].

### General Purpose: dedicated vCPU, AMD (CCX), EU, US and Singapore

| Tier | vCPU | RAM | Disk | EU | US |
|---|---|---|---|---|---|
| CCX13 | 2 | 8 GB | 80 GB | €43.49 | €43.99 |
| CCX23 | 4 | 16 GB | 160 GB | €86.49 | €87.99 |
| CCX33 | 8 | 32 GB | 240 GB | €138.99 | €141.49 |
| CCX43 | 16 | 64 GB | 360 GB | €276.49 | €279.99 |
| CCX53 | 32 | 128 GB | 600 GB | €533.99 | €538.99 |
| CCX63 | 48 | 192 GB | 960 GB | €853.99 | €860.49 |

So for this workload the CX line is 3-5x cheaper than CPX or CCX for the same RAM. Nothing in section 2 needs dedicated cores.

### Billing

"Your server's bill will never exceed its monthly price cap. If you delete your cloud server before the end of the billing month, we will only bill you for the hourly rate. We will bill you for each cloud server until you choose to delete them." [doc, each plan page]. **Hetzner still bills a powered-off server.** Only a delete stops the bill.

### What resizing involves

From the Cloud API reference for `POST /servers/{id}/actions/change_type` [doc] ([API spec](https://docs.hetzner.cloud/cloud.spec.json)):

- **Downtime:** "Server must be powered off for this command to succeed. This copies the content of its disk, and starts it again." Herdr panes and agents on the VPS stop with it. The docs don't say how long the copy takes (unverified. A proposed experiment).
- **Only up, or same-size disks:** "You can only migrate to Server types with the same `storage_type` and equal or bigger disks. Shrinking disks is not possible as it might destroy data."
- **Keeping the way back open:** "If the disk gets upgraded, the Server type can not be downgraded any more. If you plan to downgrade the Server type, set `upgrade_disk` to `false`." In the console this is the "CPU and RAM only" choice. CX23 → CX33 with `upgrade_disk: false` keeps the 40 GB disk (11 GB used today [vps]). So the server can return to CX23.
- **Errors:** `invalid_server_type` ("does not fit for the given server or is deprecated") and `server_not_stopped`.
- **Arm:** the docs don't describe a move between x86 (CX) and Arm (CAX). The installed x86 binaries would not run on Arm anyway. Treat it as a rebuild, not a rescale (unverified).
- **Billing:** the hourly rate of the new type applies from the change. The docs read here don't confirm this (unverified). It follows from hourly billing. Hetzner's June 2026 price adjustment "took effect for new orders and cloud instance rescales". Also, "certain changes to servers with legacy pricing may trigger a switch to the current pricing" [doc: [Price Adjustment 15 June 2026](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/)]. So Hetzner bills a rescale at current prices, which are the ones in the tables above.

### Availability: what "not available" means

These checks used Hetzner's own sources, on 2026-09-29:

- **The page mark is a stock mark on the whole product, not a deprecation.** Each CX/CAX row carries a `not-available` label. Its Create button has the tooltip "This product is currently unavailable. Please check back later." The intro of the page already warns that Cost-Optimized reuses "proven hardware generations". So "the number of available servers is limited" [doc: [Cost-Optimized](https://www.hetzner.com/cloud/cost-optimized/)]. The page gives no detail per location. The Create link of each row just pre-selects one location.
- **Why:** Hetzner's status page has an open incident, "Limited availability of cloud instances" (Cloud Server, since 2026-06-26 06:00 UTC, status Identified). It says: "Due to the continuing high demand and the limited availability of required hardware components, the provisioning of cloud servers at our locations is currently only possible to a limited extent … we are currently required to restrict the creation of new cloud servers for both new customers and some of our existing customers. The selection of affected existing customers is made at random" [doc: [status.hetzner.com incident](https://status.hetzner.com/incident/0a75c7ae-3377-41dc-aabe-601063724d24)]. An earlier notice for "some plans" started on 2024-06-17. Hetzner resolved it on 2025-11-15 [doc: [earlier incident](https://status.hetzner.com/incident/aa5ce33b-faa5-4fd0-9782-fde43cd270cf)].
- **What it blocks, per location and per customer:** the Cloud FAQ answers this under two questions: "Why can Cloud instances occasionally not be ordered?" / "Why are locations being deactivated?". It lists two causes. These are "no free resources available at a specific location" and "a specific location has been temporarily deactivated for some customers". For affected customers at that location it is "not possible: creating new cloud servers, rescaling existing cloud servers, moving existing cloud servers to other accounts. You can try again the following day." The restrictions "are temporary and will be automatically lifted". They may come back. And "existing cloud servers at the respective location are not impacted" [doc: [Cloud FAQ](https://docs.hetzner.com/cloud/general/faq#why-can-cloud-instances-occasionally-not-be-ordered)].
- **What the API says:**
  - Each server type has a `locations[]` list with two fields. `available` says "whether the Server Type is temporarily unavailable in this Location". `deprecation` has `announced` and `unavailable_after`. After that date the type "can not be used to create new resources" [doc: [API spec](https://docs.hetzner.cloud/cloud.spec.json)].
  - Since 1 April 2026 `server_types.locations.available` replaces the Data Center fields `available` and `available_for_migration`. Hetzner drops those from 1 October 2026. The new field "remains only an indicator whether resources are currently available and is no guarantee" [doc: [API changelog](https://docs.hetzner.cloud/changelog)].
  - An order for something unavailable fails with `412 resource_unavailable` ("e.g. not available for order"). A rescale to a deprecated type fails with `422 invalid_server_type` [doc: API spec].
  - The endpoint needs a project token (an unauthenticated `GET /v1/server_types` returns 401). So this research didn't read the values per location for this account.
- **So, for this VPS:**
  - The running CX23 is unaffected.
  - A CX23 → CX33 rescale needs CX33 stock at the server's own location. It fails if this account is among those restricted there. The cost is a failed attempt, not a lost server. The server is already off for the rescale and can start again.
  - Nothing says that Hetzner is withdrawing CX or CAX. The sources read here announce no `deprecation`, and the status notice speaks of expanding capacity.
  - The pages don't mark the CPX (Regular Performance) and CCX (General Purpose) lines. So they are the fallback, at 3-5x the price.

## 4. Alternatives

Comparable sizes: **2 vCPU / 4 GB** (today) and **4 vCPU / 8 GB** (the next step). The table shows the monthly price, and the hourly price where the provider bills by the hour.

| Provider and line | 2 vCPU / 4 GB | 4 vCPU / 8 GB | Billing model | Regions | Source |
|---|---|---|---|---|---|
| **Hetzner** Cost-Optimized CX | CX23 **€5.99** (€0.0096/h) | CX33 **€8.99** (€0.0144/h) | hourly, capped at the monthly price. Billed until deleted | Nuremberg, Falkenstein, Helsinki | [api], [doc] |
| Hetzner Regular Performance CPX | CPX22 €19.99 (80 GB) | CPX32 €35.99 (160 GB) | same | EU, Singapore. Older CPX in US | [api] |
| **netcup** VPS G12.5 | VPS 500: 2 vCores / 4 GB / 64 GB, **€8.26 incl. VAT** (about €6.94 net) | VPS 1000: 4 vCores / 8 GB / 128 GB, **€14.50 incl. VAT** (about €12.18 net) | contract of 1, 12 or 24 months (the price shown is the 12-month term). No hourly billing. Unlimited traffic. No money-back guarantee on the VPS (only Root Server and ARM. Corrected 2026-10-02) | Vienna, Nuremberg, Amsterdam, Manassas (US), Singapore | [doc] [netcup VPS](https://www.netcup.com/en/server/vps) |
| **DigitalOcean** Basic (shared) | **$24** ($0.03571/h), 80 GB | **$48** ($0.07143/h), 160 GB | per second, 60 s minimum, capped at 672 hours a month. Billed while powered off. Destroy to stop | many (incl. Frankfurt, Amsterdam, London) | [doc] [Droplet pricing](https://www.digitalocean.com/pricing/droplets), [billing details](https://docs.digitalocean.com/products/droplets/details/pricing/) |
| DigitalOcean General Purpose (dedicated) | 2 vCPU / 8 GB $63 | 4 vCPU / 16 GB $126 | same | same | [doc] |
| **Vultr** Cloud Compute Regular (`vc2`) | **$20** ($0.027/h), 80 GB, 3 TB | **$40** ($0.055/h), 160 GB, 4 TB | hourly, capped at 672 hours a month. Stopped instances billed. Destroy to stop | 30 locations incl. Frankfurt and Amsterdam | [api] `api.vultr.com/v2/plans`; [doc] [stopped instances](https://docs.vultr.com/support/platform/billing/are-stopped-instances-still-billed-on-vultr), [how billing works](https://docs.vultr.com/support/platform/billing/how-am-i-billed-for-my-servers) |
| Vultr High Performance (`vhp`, AMD or Intel) | $24 ($0.033/h), 100 GB | $48 ($0.066/h), 180 GB | same | 30-32 locations | [api] |
| **Fly.io** Machines, shared CPU | `shared-cpu-2x` 4 GB: **$21.40** (Ashburn), $24.69 (Frankfurt, $0.0343/h) | `shared-cpu-4x` 8 GB: **$42.79** (Ashburn), $49.38 (Frankfurt) | per second while running. **A stopped Machine pays only its root filesystem, $0.15 per GB per 30 days**. Volumes $0.15/GB-month | 17 regions, priced 1.0x (Ashburn) to 1.6x (São Paulo). Amsterdam 1.04x, Frankfurt 1.15x | [doc] [Fly pricing](https://docs.fly.io/about/pricing/) (figures computed from the page's own formula: $0.0000075 per shared vCPU-second, 0.25 GB included per shared vCPU, $0.00000193 per extra GB-second, 30 days) |
| Fly.io Machines, performance CPU | `performance-2x` 4 GB: $62.00 (Ashburn) | `performance-4x` 8 GB: $124.00 (Ashburn) | same | same | [doc], same formula |
| **GitHub Codespaces** | 2-core: **$0.18/hour** | 4-core: **$0.36/hour** | per hour while running. A stopped codespace pays storage only, $0.07/GB-month. It stops after 30 minutes of inactivity by default. Each month, personal accounts get 120 core-hours (60 hours of 2-core) and 15 GB-month free on GitHub Free, and 180 and 20 GB on Pro | EastUs, SouthEastAsia, WestEurope, WestUs2 | [doc] [Codespaces billing](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces), [lifecycle](https://docs.github.com/en/codespaces/about-codespaces/understanding-the-codespace-lifecycle). Regions from `gh codespace create --help` [mac]. The billing doc doesn't give the RAM per machine type (unverified) |

What this shows:

- **Always-on, per GB of RAM:** Hetzner CX (€0.94-1.50/GB) < netcup (€1.52-1.74/GB net) < Vultr ($5/GB) < Fly ($5.35/GB) ≈ DigitalOcean ($6/GB). DigitalOcean, Vultr and Fly are not cheaper or better for an always-on box. Their attraction is regions and features, not price.
- **Hetzner CPX is a poor buy here.** The same 4 GB costs €19.99 against CX23's €5.99, for AMD cores that the agent barely uses.
- **Pay only while working:** Fly.io and Codespaces are the two that stop the compute bill when stopped. Hetzner, DigitalOcean and Vultr bill a stopped server. So "on demand" there means: create from a snapshot, then delete.

## 5. On-demand and ephemeral machines

The table shows how each option would start and stop around a handover (a move of work to a new session). This research set up or tried none of them. Every one needs an account, an API token or a payment method, so these are proposals.

| Option | Start | Stop | Cost for a 4-hour burst at 16 GB | What persists | Fit |
|---|---|---|---|---|---|
| **Hetzner server from a snapshot** | `hcloud server create --name <n> --type cx43 --image <snapshot> --ssh-key <k>` ([hcloud manual](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_server_create.md)), then add it as a Herdr saved machine | `hcloud server delete <n>` (Hetzner still bills a stopped server) | CX43 4 h × €0.0264 = **€0.11** | only the snapshot (billed per GB, price not read. Unverified) | same OS image and tools as the VPS. Herdr works as today. Needs a Hetzner API token on the Mac |
| **Fly.io Machine** | Machines API `POST /v1/apps/{app}/machines` then `.../start` ([Machines API](https://docs.fly.io/machines/api/machines-resource/)) | `POST .../stop` (disk-only billing) or `DELETE`. `auto_destroy` removes it when its process exits | `shared-cpu-8x` 16 GB in Frankfurt, 4 h × $0.137 = **$0.55** | root filesystem while stopped. Volumes | container image, not a VM image. The image must include the tools, Herdr and SSH. Needs a Fly account |
| **GitHub Codespace** | `gh codespace create -R <owner/repo> -b <branch> -m <machine> --idle-timeout <d>` [mac] | `gh codespace stop`. Auto-stop after the idle timeout. Auto-delete after the retention period (default 30 days) [doc] | 8-core 4 h × $0.72 = **$2.88** (or free inside the monthly quota at 2-core) | the codespace's disk until deleted | already has GitHub auth and the repo checked out. The free quota covers small runs. Unverified: does an agent that works with no user input count as "activity" for the idle timeout? |
| Hosted cloud agents (Claude Code on the web, Codex, Cursor, Copilot) | per product | per product | usage or subscription based | per product | tickets #69 and #70 |

## 6. Recommendation per workload

An effort is one body of work with its own spec, tickets and pull request.

| Workload | Recommendation | Trade-offs |
|---|---|---|
| **One agent at a time, no browser** (today's use) | **Stay on CX23**, €5.99/month. | Fits with 2.4 GB spare [vps]. No swap, so the system could kill a big build next to the agent. Codex would sit at its 4 GB floor. |
| **One agent with a headless browser, or Codex** | **Rescale to CX33**, €8.99/month (+€3.00), "CPU and RAM only" so it can come back down. | A few minutes of downtime, with everything on the VPS stopped (length unverified). Keeps the 40 GB disk. While Hetzner's capacity restriction lasts, Hetzner can refuse the rescale (no CX33 stock at the location, or this account restricted there). Try again another day. The CX23 keeps running meanwhile. |
| **2-3 parallel agents, with or without browsers** | **CX33**, or **CX43** (€16.49) once each agent drives its own browser or builds at the same time. | Shared vCPUs slow down under long builds. They are fine for agents that mostly wait. |
| **A whole effort with many sub-agents, now and then** | Keep the small VPS. For the burst, **create a CX43/CX53 from a snapshot and delete it after** (cents per run). | Needs a current snapshot, an API token, and Herdr pointed at a new host each time. The IP changes unless you keep a Primary IP (€0.50/month [api]). |
| **Always-on, heavy parallel builds all day** | **CCX23** (4 dedicated vCPU / 16 GB, €86.49) only if CX43's shared cores measurably slow builds. | Five times CX43's price for the same RAM. |
| **Occasional repo-scoped jobs that need no Herdr** | **GitHub Codespaces**, inside the free 60 hours of 2-core a month. | No Herdr or saved-machine flow. The idle timeout may stop an unattended agent. US/EU/Asia regions only. |
| **Moving provider** | **Not worth it** for cost. Hetzner CX stays cheapest per GB. netcup is the only close one, and it needs a term of a month or longer. | A move means a manual rebuild of the box (#71's setup question). |

## Open questions

- Settled 2026-09-29: "not available" is a stock and customer restriction, per location. It can block rescales as well as new orders. It doesn't affect existing servers (see [Availability](#availability-what-not-available-means)). Still open: is CX33 available **to this account at this server's location** on the day of a rescale? Read it from the rescale dialog in the Hetzner console (read-only). Or use `GET /v1/server_types` with a read-only project token (`locations[].available`).
- TODO (proposed experiment, needs the go-ahead because it changes the machine):
  1. Rescale CX23 → CX33 with `upgrade_disk: false`, and time the downtime.
  2. Run the same workload.
  3. Rescale back, and confirm that the way down works.
- TODO (proposed experiment, writes files): on the VPS, run one Claude Code session that builds and tests one repo while it drives a headless Chromium. First install the browser's system libraries, or use the Playwright Docker image. Record the peak RSS of each process (`/usr/bin/time -v`, or `VmHWM` in `/proc/<pid>/status`) and `/proc/pressure/memory`. The measurements replace the section 2 estimates.
- TODO: Measure the RSS of a Codex CLI session once Codex is on the VPS (#71). Only the vendor minimum is known.
- TODO: 2-4 GB of swap on the VPS would turn out-of-memory kills into slowdowns at no cost. It is a config change, so it needs the go-ahead.
- TODO: Find the snapshot storage price and restore time on Hetzner, for the create-and-delete burst pattern. The pages read here don't give them.
- TODO: Does a Codespace that runs an agent with no user input stay up past the idle timeout? Try with `--idle-timeout` on a throwaway codespace. This needs the go-ahead, because it spends quota.
- Unverified: a Claude Code orchestrator with many in-process sub-agents may hold more than the 0.5 GB per session used above. The largest Mac session seen was 480 MB [mac].

## Exploration log

The table lists everything that this ticket ran, on 2026-09-29. The research installed, changed, resized, created or deleted nothing on any machine or account. No sign-ups, logins or payments.

| # | Where | Command or action | Changed |
|---|---|---|---|
| 1 | Mac, this worktree | `gh issue view 72`, `gh issue view 45`. Read the effort handoff and `docs/research/herdr-vps.md`, `harness-capabilities.md` | nothing |
| 2 | Mac, this worktree | `git merge --ff-only skills/cloud-agents` so the worktree branch starts from the effort branch (it had started from an older `main` commit) | worktree branch fast-forwarded. No other branch touched |
| 3 | Mac | `herdr machine list --json`. Wrote the target only to a scratch file outside the repo | a scratch file outside the repo |
| 4 | Mac → VPS | `ssh -o BatchMode=yes <target> "bash -lc '…'"` running `nproc; free -m; df -h /; lsb_release -ds; uname -m; grep "model name" /proc/cpuinfo; grep hypervisor /proc/cpuinfo; cat /proc/loadavg; swapon --show; cat /sys/class/dmi/id/{product_name,sys_vendor}; uptime -p` | nothing |
| 5 | Mac → VPS | same wrapper: `ps -eo rss,vsz,pcpu,etimes,comm --sort=-rss`, sum of RSS, `claude --version`, `node --version`, `cat /proc/pressure/memory`, `grep MemTotal\|MemAvailable /proc/meminfo` | nothing |
| 6 | Mac → VPS | same wrapper: `command -v chromium chromium-browser google-chrome`, `ls` of the Playwright browser cache, `df -h /dev/shm`, `/proc/stat` CPU line, `VmHWM`/`VmRSS` of the oldest `claude` process | nothing |
| 7 | Mac | `ps -axo rss,pcpu,etime,comm` filtered to agents and browsers, and a summary by kind. `sysctl -n hw.memsize hw.ncpu machdep.cpu.brand_string` | nothing |
| 8 | Mac | `gh codespace create --help`, `gh --version`, `which hcloud fly flyctl` (none installed) | nothing |
| 9 | Web | `curl` of Hetzner's Cost-Optimized, Regular Performance, General Purpose and Cloud pages, their JS bundles, and the price feed `live_data_prices.json`. Parsed locally in a scratch folder | scratch files outside the repo |
| 10 | Web | `curl` of Hetzner's Cloud API spec `docs.hetzner.cloud/cloud.spec.json`. Read `change_type`, `poweroff`, `shutdown`, `POST /servers` | scratch file outside the repo |
| 11 | Web | `curl https://api.vultr.com/v2/plans` (public, no key). Vultr's pricing page returned 403 | scratch file outside the repo |
| 12 | Web | read: Claude Code setup, Codex `docs/install.md`, GitHub-hosted runners, DigitalOcean Droplet pricing and billing docs, Vultr billing docs (via search), Fly.io pricing (page source) and Machines API, GitHub Codespaces billing and lifecycle docs, netcup VPS page, hcloud CLI manual | nothing |
| 13 | Mac | tried the Chrome extension to render Hetzner's pricing page. It was not connected, so the research used the price feed instead | nothing |
| 14 | Web (follow-up) | `curl` of the Cost-Optimized page again (labels and Create tooltips), the Regular Performance and General Purpose pages (`not-available` count: 0 each), the Cloud FAQ on docs.hetzner.com, two status.hetzner.com incidents, the Cloud API changelog and spec (`server_types.locations`, `deprecation`, error codes), and the June 2026 price-adjustment page. One web search to find the status notices. An unauthenticated `GET https://api.hetzner.cloud/v1/server_types` (401) | scratch files outside the repo |
