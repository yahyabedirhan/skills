# VPS providers to switch to

Facts for [Research: VPS options to switch to (#86)](https://github.com/yahyabedirhan/skills/issues/86), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45) and decision [D4](cloud-agents.md#d4-resize-the-vps). Prices read and latency measured on **2026-09-30**. How much RAM each workload needs, Hetzner's own tiers and billing, and why Hetzner's CX line can't be ordered are in [cloud-agents-vps-sizing.md](cloud-agents-vps-sizing.md) and not repeated here. The target: a machine for remote Claude Code agents in Herdr, **with a headless browser from day zero**, in Europe, up to about **$50 a month (≈ €45)**.

Evidence tags, as in the sizing file:

- **[doc]** a provider's own pricing page or documentation, linked inline.
- **[api]** a provider's own public catalogue or API, read without an account: Hetzner's price feed and server-auction feed, OVHcloud's order catalogue (`eu.api.ovh.com/v1/order/catalog/public/{vps,cloud}?ovhSubsidiary=DE`), Scaleway's product and availability endpoints (`api.scaleway.com/instance/v1/zones/fr-par-1/products/servers[/availability]`), Vultr's `api.vultr.com/v2/plans`, Akamai/Linode's `api.linode.com/v4/linode/types` and `/regions`.
- **[mac]** a read-only command on the Mac (ping, `curl` timing, `dig`).
- **Unverified** has no primary source.

Currency and tax are stated per row, because providers differ: most European providers show EUR net of VAT, netcup and IONOS (German site) show EUR **including 19% German VAT**, the US-based ones show USD net of tax. Where a page showed a VAT-inclusive price for a country other than Germany, only the net figure is used here.

## Short answer

- **Shared vs dedicated, in one line:** a shared vCPU is a slice of a core that other customers' servers also use, so it's cheap and fine while agents wait on the model, but a long build or a busy browser page can run slower when neighbours are busy; a dedicated vCPU is a CPU thread reserved for you, so builds and browsers run at the same speed every time. For this workload **RAM decides the size, CPU type decides how smooth the bursts are**.
- **Hetzner's cheap line stays shut.** On 2026-09-30 all eight CX and CAX tiers are still marked "currently unavailable", CX is sold only in Nuremberg, Falkenstein and Helsinki (no other location to try), and Hetzner's capacity notice (open since 2026-06-26) is still unresolved [doc, api]. What Hetzner will sell today at 16 GB costs €69.99 (CPX42, shared) or €86.49 (CCX23, dedicated): over budget.
- **Best value inside the budget: netcup.** Its **Root Server RS 2000 G12.5** gives **8 dedicated AMD EPYC 9645 cores, 16 GB DDR5 ECC, 256 GB NVMe** for **€34.20 net (€40.70 incl. 19% VAT) a month on a 12-month term**, or €39.34 net (€46.81 incl. VAT) month to month, with a 30-day money-back guarantee [doc]. Nothing else in the budget offers dedicated cores at 16 GB.
- **Cheaper fallbacks:** netcup **VPS 2000 G12.5** (8 shared vCores, 16 GB, 256 GB) at €22.62 net on 12 months [doc]; **OVHcloud VPS-4** (8 vCores, 24 GB, 200 GB) at €23.49 net month to month, no commitment [api]; **UpCloud Starter** 4 cores / 16 GB at €28 net, billed hourly [doc]. And if Hetzner reopens CX, **CX43** (8 shared vCPU / 16 GB, €16.49, hourly) is still the cheapest of all [api].
- **Out of budget at 16 GB:** DigitalOcean, Vultr and Akamai/Linode all ask **$80-96 a month** for 16 GB shared [doc, api]; Scaleway €50-86 net plus storage and IPv4 [doc, api].
- **Latency barely separates them.** Median ping from the Mac to each provider's nearest EU site is **54-102 ms**; all but Hetzner Helsinki fall within **54-84 ms**, and netcup (68 ms) matches Hetzner Nuremberg/Falkenstein (70-77 ms), today's region [mac]. A 10-20 ms difference is not worth choosing on, next to model calls that take seconds.
- **Switching is a rebuild, not a copy.** Plan it as: order the new machine, set it up (by hand now, with set-up-machine once PR #66 merges), save it in Herdr as a second machine, run both side by side for two to four weeks, then delete the old one. The overlap costs €5.99 a month for the CX23.

## 1. Shared vs dedicated vCPU, and what else separates offers

### In plain words

A **vCPU** is what the virtual machine sees as one processor. The host decides how much real CPU is behind it:

- **Shared** (Hetzner CX/CPX/CAX, netcup VPS, OVHcloud VPS, most "Basic" or "Starter" plans): the host sells more vCPUs than it has cores and lets them take turns. When your neighbours are idle you get a whole core; when they are busy you wait. Linux shows the waiting as **steal time** (`st` in `top`, the 8th number of the `cpu` line in `/proc/stat`). Scaleway puts it as "a context-switching mechanism allows a physical core to be shared between multiple vCPUs" [doc: [Scaleway, choosing an Instance type](https://www.scaleway.com/en/docs/instances/reference-content/choosing-instance-type/)].
- **Dedicated** (Hetzner CCX, netcup Root Server, OVHcloud Public Cloud, DigitalOcean General Purpose, Linode Dedicated, Vultr Optimized): "1 vCPU = 1 CPU thread dedicated to that Instance" [doc: Scaleway, same page]; netcup's version is "CPU performance is provided exclusively to the customer … While CPU performance cannot be guaranteed with a VPS, a root server … has guaranteed CPU performance" [doc: [netcup root server](https://www.netcup.com/en/server/root-server)]. Usually about twice the price per vCPU.
- **Burstable** (not offered by the providers compared here in the budget range): a baseline share plus credits you spend on bursts. Mentioned only because some benchmarks mix it up with shared.

### What it means for agents

| Part of the work | CPU pattern | Shared vCPU is fine? | Source |
|---|---|---|---|
| Agent waiting on the model, reading files, running `git` | almost idle: 1-2% of a core, about 16% while working | yes | [siz §1](cloud-agents-vps-sizing.md#per-process-footprints) |
| Builds and test runs (`node`, `swift build`, `pytest`) | a few cores flat out for seconds to minutes | yes, but they take longer when neighbours are busy; dedicated gives the same time every run | estimate |
| Headless Chromium (Playwright) | spiky; one busy page can fill a core; 0.5-1 GB RAM | yes for a page at a time; several browsers plus a build want 4+ cores | [siz §1](cloud-agents-vps-sizing.md#per-process-footprints) |
| Several agents at once | RAM adds up per agent; CPU only when they build at the same moment | RAM is the limit, not CPU | [siz §2](cloud-agents-vps-sizing.md#2-workload-to-smallest-tier) |

So a shared 16 GB machine does the job; a dedicated one makes builds and browser runs predictable. Six weeks of the current VPS showed 0% steal and CPU idle 97% of the time [siz](cloud-agents-vps-sizing.md#the-vps-today-vps), so neighbours have not been a problem at Hetzner so far.

### The other differences

| Thing | Why it matters here | What to look for |
|---|---|---|
| **RAM** | Decides how many agents and browsers fit; with no swap, running out kills processes | 16 GB for 2-3 agents each with a browser [siz §2](cloud-agents-vps-sizing.md#2-workload-to-smallest-tier) |
| **CPU generation** | Newer cores finish builds and page renders sooner, per core | Published: netcup RS AMD EPYC 9645 (Zen 5), Scaleway BASIC3 AMD EPYC 7543 (Zen 3), BASIC2 Ampere; UpCloud Starter says only "previous-gen AMD CPUs"; many VPS lines don't say |
| **Arm vs x86** | Arm (Hetzner CAX, netcup VPS ARM, Scaleway BASIC2, Oracle A1) runs Claude Code and Playwright's Chromium, but any x86-only binary or Docker image won't run; a move from today's x86 box is a rebuild either way | Prefer x86 unless the price gap is large |
| **Disk** | Repos, `node_modules`, Docker images (the Playwright image is several GB) | 100 GB+ NVMe; Scaleway and UpCloud Cloud Native sell storage separately |
| **Traffic** | Agents move little data; a cap only matters for big downloads | All here include 1 TB+ or "unlimited" with a fair-use clause |
| **IPv4** | Needed to SSH in from most networks | Included everywhere here except Scaleway (extra) |
| **Billing** | Hourly lets you try and delete; terms lower the price but tie you in | Hetzner, UpCloud, Scaleway, OVHcloud Public Cloud, DigitalOcean, Vultr, Linode: hourly. netcup, OVHcloud VPS, IONOS, Contabo, Hostinger: monthly or longer terms |

## 2. The providers at 8 GB and 16 GB

All prices read 2026-09-30. "Orderable" means the provider's page or API offers it for order today; it can't prove stock without an account.

### Hetzner

| Offer | vCPU | RAM | Disk | Traffic | Price (EUR, net, incl. IPv4) | Billing | EU locations | Orderable today |
|---|---|---|---|---|---|---|---|---|
| CX33 | 4 shared (Intel/AMD) | 8 GB | 80 GB | 20 TB | €8.99 | hourly, monthly cap | NBG1, FSN1, HEL1 | **No**: "This product is currently unavailable" on all 8 CX/CAX rows [doc] |
| CX43 | 8 shared | 16 GB | 160 GB | 20 TB | €16.49 | same | same | **No** |
| CAX21 / CAX31 (Arm) | 4 / 8 shared Ampere | 8 / 16 GB | 80 / 160 GB | 20 TB | €10.99 / €21.49 | same | same | **No** |
| CPX32 | 4 shared AMD | 8 GB | 160 GB | 20 TB | €35.99 | same | NBG1, FSN1, HEL1 | Yes (no mark on the page) |
| CPX42 | 8 shared AMD | 16 GB | 320 GB | 20 TB | €69.99 | same | same | Yes |
| CCX13 | 2 dedicated AMD | 8 GB | 80 GB | 20 TB | €43.49 | same | same | Yes |
| CCX23 | 4 dedicated AMD | 16 GB | 160 GB | 20 TB | €86.49 | same | same | Yes |
| Server Auction (dedicated hardware) | e.g. Intel Core i7-6700/7700, 4 cores | 32-64 GB | 2x 512 GB SSD or HDD | unlimited | from **€62 + €1.70 IPv4** (cheapest of 179 listed) | monthly, no setup fee | FSN1, NBG1, HEL1 | Yes, but over budget [api] |

Sources: [Cost-Optimized](https://www.hetzner.com/cloud/cost-optimized/), [Regular Performance](https://www.hetzner.com/cloud/regular-performance/), [General Purpose](https://www.hetzner.com/cloud/general-purpose/) [doc] (not-available marks: 16 on Cost-Optimized, i.e. 8 rows × label and tooltip; 0 on the other two), prices from the price feed as tabulated in [siz §3](cloud-agents-vps-sizing.md#3-hetzners-tiers); auction from `https://www.hetzner.com/_resources/app/data/app/live_data_sb.json` [api]. Hetzner's status notice "Limited availability of cloud instances" still has no end time (last updated 2026-09-11) [doc: [status.hetzner.com](https://status.hetzner.com/incident/0a75c7ae-3377-41dc-aabe-601063724d24)].

**Is CX orderable anywhere?** No. The Cost-Optimized line exists only in the three EU locations, and the page marks every CX and CAX row unavailable, with no per-location exception [doc]. Whether this account could create one at a given location on a given day is only visible in the console or through the API with a token (see [siz, Availability](cloud-agents-vps-sizing.md#availability-what-not-available-means)).

### netcup

Prices as shown on netcup's German-VAT default: **EUR incl. 19% VAT**; net = ÷1.19. The page's two figures per plan are the 12-month price and the 1-month price; 24 months is 26% below the 1-month price [doc].

| Offer | vCPU | RAM | Disk | Traffic | 12-month term | 1-month term | EU locations | Orderable |
|---|---|---|---|---|---|---|---|---|
| VPS 1000 G12.5 | 4 shared vCores (x86) | 8 GB ECC | 128 GB SSD | "traffic included": throttled to 200 Mbit/s only if the 24-hour average exceeds 2 TB; 2.5 Gbit/s port | €14.50 (€12.18 net) | €16.68 (€14.02 net) | Nuremberg, Vienna, Amsterdam, or "no preference Europe" | Yes |
| VPS 2000 G12.5 | 8 shared vCores (x86) | 16 GB ECC | 256 GB SSD | same | **€26.92 (€22.62 net)** | €30.96 (€26.02 net) | same | Yes |
| VPS 1000 / 2000 ARM G12.5 | 4 / 8 vCores Ampere Altra Max | 8 / 16 GB | 128 / 256 GB NVMe | same | €14.50 / €26.92 | €16.68 / €30.96 | not read | Yes |
| RS 1000 G12.5 | **4 dedicated** AMD EPYC 9645 | 8 GB DDR5 ECC | 128 GB NVMe | not read (unverified; netcup root servers are sold with a traffic flat rate) | €21.73 (€18.26 net) | €25.00 (€21.01 net) | Nuremberg, Vienna, or "no preference Europe" | Yes |
| RS 2000 G12.5 | **8 dedicated** AMD EPYC 9645 | 16 GB DDR5 ECC | 256 GB NVMe | same | **€40.70 (€34.20 net)** | €46.81 (€39.34 net) | same | Yes |

Sources: [netcup VPS](https://www.netcup.com/en/server/vps), [VPS ARM](https://www.netcup.com/en/server/arm-server), [Root Server](https://www.netcup.com/en/server/root-server) [doc]. Terms: 1, 12 or 24 months, no hourly billing; 30-day money-back on the basic fee; snapshots, image import and export, remote console; the location "cannot be changed later"; upgrades only to a bigger plan of the same generation and product type [doc]. The VPS page itself says the VPS lacks the root server's "dedicated CPU cores" [doc]. The VPS's CPU model is not published (unverified).

### OVHcloud

EUR, **net of VAT** (the catalogue states `taxRate: 19` separately; the Irish page shows the same figure "ex. VAT") [api, doc].

| Offer | vCPU | RAM | Disk | Traffic | Price | Billing | EU locations | Orderable |
|---|---|---|---|---|---|---|---|---|
| VPS-2 (2027 range) | 4 vCores (shared, unverified: not stated) | 8 GB | 75 GB NVMe | unlimited, 1 Gbit/s | **€8.49** month to month; €7.21 on 12 months | monthly; 6- and 12-month upfront options | Gravelines, Roubaix, Strasbourg, Germany ("DE"), London, Warsaw, Milan | Yes, in the public catalogue |
| VPS-3 (2027) | 6 vCores | 12 GB | 100 GB NVMe | unlimited, 2 Gbit/s | €12.24; €10.40 on 12 months | same | same | Yes |
| VPS-4 (2027) | 8 vCores | **24 GB** | 200 GB NVMe | unlimited, 3 Gbit/s | **€23.49**; €19.96 on 12 months | same | same | Yes |
| Public Cloud d2-8 (Discovery) | 4 vCores | 8 GB | 50 GB NVMe | 500 Mbit/s | €0.0372/h or €20.60/month | hourly or monthly | per region (not read) | Yes |
| Public Cloud b3-8 (General Purpose) | 2 vCores, 2.3 GHz, "guaranteed resources" | 8 GB | 50 GB NVMe | 500 Mbit/s | €0.0512/h (≈ €37.38 for 730 h) | hourly | per region | Yes |
| Public Cloud r3-16 (RAM) | 2 vCores, guaranteed | 16 GB | 50 GB NVMe | 500 Mbit/s | €0.0663/h (≈ €48.40) | hourly | per region | Yes |
| Public Cloud b3-16 | 4 vCores, guaranteed | 16 GB | 100 GB NVMe | 1 Gbit/s | €0.1023/h (≈ €74.68) | hourly | per region | Yes |

Sources: [OVHcloud VPS](https://www.ovhcloud.com/en-ie/vps/) [doc]; plan codes `vps-2027-model{2,3,4}` and flavours `b3-8`, `b3-16`, `r3-16`, `d2-8` in the order catalogue [api]. There is no 16 GB VPS in the 2027 range: it jumps from 12 GB to 24 GB. The catalogue files every Public Cloud flavour, Discovery included, under "guaranteed-resources" [api]; the VPS range makes no dedicated-CPU claim.

### Scaleway

EUR, **net of VAT**; "List prices include egress and IPv6 addresses. Storage (local, block) and attached public IPv4 addresses are excluded" [doc: [Scaleway Instances pricing](https://www.scaleway.com/en/pricing/virtual-instances/)]. Hourly billing; the monthly figure is the provider's own estimate.

| Offer | vCPU | RAM | CPU | Bandwidth | Price | EU zones | Orderable |
|---|---|---|---|---|---|---|---|
| BASIC2-A2C-8G | 2 (Arm) | 8 GB | Ampere M128-30 | 200 Mbit/s | €0.0345/h, ~€25.18 | PAR-1, PAR-2, AMS-1 | "available" in fr-par-1 [api] |
| BASIC2-A4C-8G | 4 (Arm) | 8 GB | Ampere M128-30 | 400 Mbit/s | €0.0517/h, ~€37.74 | same | available |
| DEV1-L | 4 (x86, shared) | 8 GB | not stated | 400 Mbit/s | €0.04284/h, ~€31.27 | PAR | available |
| PLAY2-MICRO | 4 (x86, shared) | 8 GB | not stated | 400 Mbit/s | €0.05508/h, ~€40.20 | on the page; not in the fr-par-1 API list | unverified |
| BASIC3-X2C-8G | 2 (x86) | 8 GB | AMD EPYC 7543 | 350 Mbit/s | €0.05923/h, ~€43.23 | PAR-1, PAR-2, MIL-1, AMS-1, AMS-2 | available |
| BASIC2-A4C-16G | 4 (Arm) | 16 GB | Ampere M128-30 | 400 Mbit/s | €0.0689/h, ~€50.30 | PAR, AMS | available |
| BASIC3-X4C-16G | 4 (x86) | 16 GB | AMD EPYC 7543 | 700 Mbit/s | €0.11845/h, ~€86.46 | PAR, MIL, AMS | available |

Sources: pricing page [doc], [Instances datasheet](https://www.scaleway.com/en/docs/instances/reference-content/instances-datasheet/) (CPU models and zones) [doc], product and availability API [api]. Scaleway's table calls Development instances shared and General Purpose "shared vCPU or dedicated vCPU" without saying which the BASIC2/BASIC3 types are (unverified). Add block storage and an IPv4 to every row.

### IONOS

EUR, **incl. 19% German VAT** (ionos.de), regular monthly price; the page advertises a lower price for the first 3 months and a €10 setup fee; "offers … partly depend on minimum contract terms" (the US page says "with a 1-year term") [doc: [IONOS VPS](https://www.ionos.de/server/vps)].

| Offer | vCPU | RAM | Disk | Traffic | Price | EU locations | Orderable |
|---|---|---|---|---|---|---|---|
| VPS L+ | 4 vCores ("latest generation AMD and Intel", model not stated) | 8 GB | 240 GB NVMe | unlimited, up to 1 Gbit/s | €22 (€18.49 net); €7 for the first 3 months | "EU, USA and UK" (sites not named) | Yes |
| VPS XL+ | 8 vCores | 16 GB | 480 GB NVMe | same | €41 (€34.45 net); €12 for the first 3 months | same | Yes |

Whether the vCores are shared is not stated (unverified; the VPS line is marketed like the other shared VPS lines). The exact minimum term for the German offer wasn't on the page (unverified).

### Contabo

EUR, **net of VAT**, "the effective monthly rate for a 24-month subscription"; minimum initial term 1 month, at a price the page doesn't show (unverified). Outgoing traffic "unlimited – fair usage policy applies" [doc: [Contabo Cloud VPS](https://contabo.com/en/vps/)].

| Offer | vCPU | RAM | Disk | Port | Price (24-month rate) | EU locations | Orderable |
|---|---|---|---|---|---|---|---|
| Cloud VPS 4 | 4 vCPU ("proven infrastructure across multiple CPU generations") | 8 GB | 100 GB SSD | 200 Mbit/s | €4.40 | "European Union" region (sites not named on the page) | Yes |
| Cloud VPS 6 | 6 vCPU | 12 GB | 200 GB SSD | 300 Mbit/s | €6.00 | same | Yes |
| Cloud VPS 8 | 8 vCPU | 24 GB | 300 GB SSD | 600 Mbit/s | €11.20 | same | Yes |

No 16 GB step: 12 GB then 24 GB. Contabo also sells "Performance VPS" (newer AMD EPYC) and "Max Performance VPS" ("virtual dedicated servers"), not priced here (the Performance VPS page URL tried returned 404). Contabo is the cheapest per GB by far, and the page itself positions Core VPS for workloads "where CPU is rarely the bottleneck" [doc]; builds and browsers are exactly where it is.

### UpCloud

EUR, **net of tax**, billed "by the starting hour, maximum of 28 days per month"; zero-cost egress with a fair-transfer policy [doc: [UpCloud pricing](https://upcloud.com/pricing/), read in the browser because the page blocks `curl`]. Starter plans replaced the Developer plans on 2026-04-15; Developer, General Purpose, High CPU and High Memory plans can no longer be deployed [doc: [changelog](https://upcloud.com/docs/changelog/)].

| Offer | Cores | RAM | Storage | Bandwidth | Price | EU locations | Orderable |
|---|---|---|---|---|---|---|---|
| Starter 8 GB / 2 | 2 | 8 GB | 40 GB Standard SSD | 500 Mbit/s | €18/mo | Amsterdam, Copenhagen, Frankfurt, Helsinki (2), London, Madrid, Stavanger, Stockholm, Warsaw | Yes |
| Starter 8 GB / 4 | 4 | 8 GB | 40 GB | 500 Mbit/s | €20/mo | same | Yes |
| Starter 16 GB / 2 | 2 | 16 GB | 50 GB | 500 Mbit/s | €24/mo | same | Yes |
| Starter 16 GB / 4 | 4 | 16 GB | 50 GB | 500 Mbit/s | **€28/mo** | same | Yes |

Starter uses "previous-gen AMD CPUs" and includes IPv4 [doc]; whether its cores are shared is not stated (unverified). The Premium (newer AMD EPYC, MaxIOPS) and Cloud Native tabs weren't read. Locations from [UpCloud locations](https://upcloud.com/docs/getting-started/locations/) [doc]. 50 GB is tight for Docker images; extra Standard storage is €0.085/GB-month [doc].

### DigitalOcean, Vultr, Akamai/Linode

USD, **net of tax**, hourly with a monthly cap; a stopped server is billed until destroyed (see [siz §4](cloud-agents-vps-sizing.md#4-alternatives)).

| Provider and offer | vCPU | RAM | Disk | Transfer | Price | EU locations | Source |
|---|---|---|---|---|---|---|---|
| DigitalOcean Basic (shared) | 4 | 8 GiB | 160 GiB | 5,000 GiB | $48 ($0.07143/h) | Frankfurt, Amsterdam, London | [doc] [Droplet pricing](https://www.digitalocean.com/pricing/droplets) |
| DigitalOcean Basic (shared) | 8 | 16 GiB | 320 GiB | 6,000 GiB | $96 | same | [doc] |
| DigitalOcean General Purpose (dedicated) | 2 / 4 | 8 / 16 GiB | 25 / 50 GiB | 4,000 / 5,000 GiB | $63 / $126 | same | [doc] |
| Vultr Regular `vc2` (shared) | 4 / 6 | 8 / 16 GB | 160 / 320 GB | 4 / 5 TB | $40 / $80 | Amsterdam, Paris, Frankfurt, London, Madrid, Manchester, Stockholm, Warsaw | [api] |
| Vultr High Performance `vhp` (shared, AMD or Intel) | 4 / 8 | 8 / 16 GB | 180 / 350 GB | 6 / 8 TB | $48 / $96 | same | [api] |
| Vultr Optimized `voc-g` (dedicated) | 2 / 4 | 8 / 16 GB | 50 / 80 GB | 5 / 6 TB | $60 / $120 | same | [api] |
| Linode Shared | 4 / 6 | 8 / 16 GB | 160 / 320 GB | 5 / 8 TB | $48 / $96 | Frankfurt (2), London (2), Amsterdam, Paris (2), Milan, Madrid, Stockholm | [api] |
| Linode Dedicated | 4 / 8 | 8 / 16 GB | 160 / 320 GB | 5 / 6 TB | $72 / $144 | same | [api] |

All orderable in the EU per their APIs and pages. At 8 GB they fit the budget, at 16 GB none does.

### Others worth knowing

| Offer | What | Price | Caveat | Source |
|---|---|---|---|---|
| **Hostinger** KVM 2 / KVM 4 | 2 vCPU / 8 GB / 100 GB NVMe / 8 TB; 4 vCPU / 16 GB / 200 GB / 16 TB; "AMD EPYC processors" | USD net of VAT: **$8.99 / $12.99** a month for 24 months paid upfront, then "renews at $14.99 / $28.99"; $24.49 / $42.99 is the undiscounted rate | Paid upfront; "data centers across … Europe" without naming them on the page (unverified which); shared vs dedicated not stated | [doc] [Hostinger VPS](https://www.hostinger.com/vps-hosting) |
| **Oracle Cloud** Always Free, Ampere A1 | Arm, now **"equivalent to 2 OCPUs and 12 GB of memory"** a month for Always Free tenancies | free | Only in the tenancy's home region; "out of host capacity" errors are common and documented; **idle instances "may be reclaimed"** when 95th-percentile CPU, network and memory are all under 20% over 7 days, which an agent box waiting on the model can easily be. Not a base for a daily-use machine | [doc] [Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm) |

## 3. Latency from the Mac

Measured 2026-09-30 from the Mac, one run, 7 samples per host: `ping -c 7` (ICMP round trip) and 7 × `curl -w '%{time_connect}'` (the TCP handshake, about one round trip plus a little) [mac]. Medians in milliseconds. Hosts are the providers' own published speed-test or looking-glass hosts where one exists; where none was found, a regional endpoint the provider runs in that location (object storage), marked as such. The Mac's location and network are deliberately not given.

| Provider | Location | Host measured | Kind | Ping (ms) | TCP connect (ms) |
|---|---|---|---|---|---|
| Hetzner | Falkenstein | `fsn1-speed.hetzner.com` | speed test | 70 | 80 |
| Hetzner | Nuremberg | `nbg1-speed.hetzner.com` | speed test | 77 | 78 |
| Hetzner | Helsinki | `hel1-speed.hetzner.com` | speed test | 102 | 103 |
| netcup | (not stated by the host) | `speedtest.netcup.de` | speed test | 68 | 75 |
| netcup | (not stated) | `lg.netcup.net` | looking glass | 68 | 72 |
| OVHcloud | Strasbourg | `sbg.proof.ovh.net` | speed test | **63** | 73 |
| OVHcloud | Roubaix | `rbx.proof.ovh.net` | speed test | 75 | 81 |
| OVHcloud | Gravelines | `gra.proof.ovh.net` | speed test | 76 | 81 |
| OVHcloud | Germany ("DE") | `s3.de.io.cloud.ovh.net` | object storage | 69 | 75 |
| OVHcloud | Warsaw / London | `s3.waw…`, `s3.uk.io.cloud.ovh.net` | object storage | 84 / 82 | 83 / 90 |
| Scaleway | Paris | `ping.online.net` | ping host (Scaleway Dedibox) | 72 | 77 |
| Scaleway | Paris / Amsterdam / Warsaw | `s3.{fr-par,nl-ams,pl-waw}.scw.cloud` | object storage | 69 / 71 / 73 | 76 / 81 / 80 |
| IONOS | Frankfurt / Berlin | `s3.eu-central-{1,2}.ionoscloud.com` | IONOS Cloud object storage (not the VPS data centres, which aren't named) | 64 / 66 | 70 / 74 |
| Contabo | EU | `eu2.contabostorage.com` | object storage | 76 | 77 |
| UpCloud | unknown | `api.upcloud.com` | API endpoint (no public speed-test host found; ICMP blocked; location unverified) | blocked | 124 |
| DigitalOcean | Frankfurt / Amsterdam / London | `{fra1,ams3,lon1}.digitaloceanspaces.com` | Spaces object storage (the old `speedtest-<region>` hosts no longer resolve) | **54** / 64 / 67 | 63 / 69 / 79 |
| Vultr | Frankfurt / Amsterdam / Paris | `{fra-de,ams-nl,par-fr}-ping.vultr.com` | ping host | **55** / 62 / 64 | 59 / 68 / 68 |
| Vultr | London / Warsaw / Stockholm | `{lon-gb,waw-pl,sto-se}-ping.vultr.com` | ping host | 67 / 71 / 78 | 73 / 75 / 82 |
| Akamai/Linode | Milan / Amsterdam / Frankfurt | `speedtest.{milan,amsterdam,frankfurt}.linode.com` | speed test | 60 / 66 / 67 | 71 / 78 / 75 |
| Akamai/Linode | London / Paris / Stockholm / Madrid | `speedtest.{london,paris,stockholm,madrid}.linode.com` | speed test | 73 / 78 / 81 / 81 | 77 / 80 / 86 / 89 |
| Hostinger | — | no published host found | — | not measured | — |

What it shows:

- **Spread:** 54 ms (DigitalOcean and Vultr Frankfurt) to 102 ms (Hetzner Helsinki); everything in Germany, France, the Netherlands, Italy and Poland sits between 54 and 84 ms.
- **Today's region** (Hetzner Nuremberg/Falkenstein) is 70-77 ms; netcup 68 ms; OVHcloud Strasbourg 63 ms. A switch within Germany changes nothing noticeable.
- **Avoid Helsinki** (Hetzner HEL1, UpCloud fi-hel) from this Mac: 25-30 ms slower than central Europe.
- Caveats: one run at one time of day; object-storage endpoints may sit on load balancers in the same site but not on the compute network; UpCloud's figure is for its API, not a compute zone.

## 4. Switching

### What moves, and how

| Step | What it takes | Notes |
|---|---|---|
| **Order** | One order at the chosen provider (an account, payment, and an SSH key on the order form) | Needs the maintainer: sign-up and payment are outside this research |
| **Rebuild, not copy** | A fresh Ubuntu LTS image, then the environment | Recommended. The current box is Ubuntu 26.04 with a hand-made setup ([cloud-agents-vps.md](cloud-agents-vps.md)); rebuilding is the moment to make it reproducible |
| **Snapshot import** | Not a practical route off Hetzner | Hetzner Cloud's snapshot docs describe no way to download or export a snapshot (unverified: no statement either way was found in [the snapshot FAQ](https://docs.hetzner.com/cloud/servers/backups-snapshots/faq/)). netcup and OVHcloud do import images [doc], so a raw disk copy (`dd` from Hetzner's rescue system over SSH) is possible in theory, but it carries the old hand-made setup, network config and cloud-init quirks with it. Not worth it for a 40 GB box with 11 GB used |
| **Environment** | set-up-machine, once [PR #66](https://github.com/yahyabedirhan/skills/pull/66) merges (still **open** on 2026-09-30); until then by hand | set-up-machine "runs on macOS and Linux" with Python 3.9+ and installs the skills, rule table, hook and memory-off ([cloud-agents-vps.md](cloud-agents-vps.md), section "The environment"). Before it: `nvm`/Node, Claude Code, `gh`, Herdr at the same version as the Mac, `jq`, Go and Treehouse (E8) |
| **Headless browser, day zero** | On a fresh box with root, `npx playwright install --with-deps chromium`, or the Playwright Docker image (D5, E7) | On the new machine installing system libraries as root is part of building it, not a change to a running box |
| **Log-ins** | `claude` login, `gh auth login`, a new SSH key for GitHub | Re-authenticate on the new box rather than copying credential files |
| **Data** | `git clone` the repos; `rsync` anything uncommitted from the old box | The old box also runs "a few containers and web services" [siz](cloud-agents-vps-sizing.md#the-vps-today-vps): list them and move each on purpose |
| **Herdr** | `herdr machine add` a **second** saved machine on the Mac with a new label; keep the old profile | A saved machine is only a connection profile; each machine runs its own Herdr server, so panes and sessions don't move, they are started anew ([herdr-vps.md](herdr-vps.md)). Skills that read the target from `herdr machine list --json` pick up the new label with no code change |

### Side by side

- Keep the CX23 running for **two to four weeks** after the new machine takes over. It costs €5.99 a month and is billed hourly, so deleting it any day stops the bill [siz](cloud-agents-vps-sizing.md#billing). Don't delete it to "make room": Hetzner is restricting new orders, so a deleted CX23 can't be ordered again.
- During the overlap, point new efforts at the new machine's Herdr label and let running ones finish on the old one.
- Delete only after: the repos have no unpushed branches on the old box, its services have moved, and the Mac's Herdr profile for it is removed.

### What switching costs

| Item | Cost |
|---|---|
| The new machine (recommended) | €34.20 net a month on 12 months (€40.70 incl. German VAT), or €39.34 net month to month |
| Overlap with the old VPS | €5.99 a month while both run |
| Setup fees | none at netcup (none shown on the root-server page); IONOS €10; Hetzner none |
| Time | A few hours by hand; less once set-up-machine exists (estimate) |
| Risk | Low: the old box keeps running until the new one is proven; netcup's 30-day money-back covers a bad fit |

## 5. Ranked shortlist

Scored on: fits a headless browser plus 2-3 agents (16 GB), CPU steadiness for builds, price inside €45, EU latency, and billing flexibility.

| Rank | Offer | Size | Monthly | Why | Against |
|---|---|---|---|---|---|
| **1** | **netcup RS 2000 G12.5** | 8 dedicated EPYC 9645 (Zen 5) / 16 GB DDR5 ECC / 256 GB NVMe | **€34.20 net** on 12 months (€40.70 incl. 19% VAT); €39.34 net (€46.81) month to month | Only 16 GB dedicated-core offer inside the budget; newest CPU in the list; 68 ms; image import and snapshots; 30-day money-back | No hourly billing; best price needs a 12-month term; the location can't be changed later; resize only within the same generation |
| 2 | netcup VPS 2000 G12.5 | 8 shared vCores / 16 GB / 256 GB | €22.62 net on 12 months (€26.92 incl. VAT); €26.02 net month to month | Same provider and latency at two-thirds the price | Shared cores; CPU model not published |
| 3 | OVHcloud VPS-4 (2027) | 8 vCores / 24 GB / 200 GB NVMe | **€23.49 net month to month**, no commitment; €19.96 on 12 months | Most RAM for the money without a term; Strasbourg at 63 ms; daily backup included | Shared cores (unverified); monthly, not hourly |
| 4 | UpCloud Starter 16 GB / 4 | 4 cores / 16 GB / 50 GB | €28 net, **hourly** | Hourly billing, try and delete; many EU sites | "Previous-gen AMD"; 50 GB disk; latency not measured on a compute zone |
| 5 | Hetzner CX43, **when orderable** | 8 shared / 16 GB / 160 GB | €16.49 net, hourly | Cheapest of all; same provider, tools and API | Not orderable today, no date given |
| — | Hetzner CCX13 | 2 dedicated / 8 GB | €43.49 net | Orderable today at Hetzner | Only 8 GB for nearly the same money as rank 1 |

Not shortlisted: DigitalOcean, Vultr and Linode (16 GB at $80-96); Scaleway (16 GB x86 at €86 plus storage and IPv4; 16 GB Arm at €50); IONOS XL+ (€34.45 net for 16 GB shared, with a term and setup fee, so worse than netcup's shared VPS); Contabo (cheapest, but noisy-neighbour hardware, 24-month pricing and a slow port); Hostinger (upfront multi-year payment, renewal price doubles); Oracle Always Free (idle reclamation).

### Recommendation

**Move to netcup RS 2000 G12.5 in Nuremberg, on a 12-month term, and keep the CX23 alongside it for a few weeks.** It is the only offer inside about €45 that gives 16 GB and dedicated cores, so a headless browser, a build and two or three agents can run at once without the machine or the neighbours deciding how fast. Order it on 12 months: the 30-day money-back guarantee is the trial period, and the saving over month to month (€5.14 net a month) pays for the CX23 overlap. If the maintainer would rather not commit to a term, the same plan month to month is €39.34 net.

**Cheaper fallback: netcup VPS 2000 G12.5** (8 shared vCores, 16 GB) at €22.62 net on 12 months, or **OVHcloud VPS-4** (24 GB) at €23.49 net with no commitment. Either carries the same workload; builds and browsers are just less predictable. If Hetzner reopens CX before the move, **CX43 at €16.49** remains the cheapest way to reach 16 GB and keeps everything at one provider.

## Open questions

- TODO (needs the maintainer: an account and a payment): order the recommended machine; the 30-day money-back window starts on order.
- TODO (proposed experiment, after the order): on the new machine, run one Claude Code session that builds a repo while driving a headless Chromium, and record steal time (`/proc/stat`), peak RSS and build time; repeat the same run on the CX23 for comparison. Replaces this page's "dedicated is steadier" with numbers.
- Unverified: whether netcup's VPS and IONOS's, OVHcloud's, UpCloud Starter's and Hostinger's vCPUs are shared (none say, except netcup saying its VPS lacks dedicated cores); Scaleway BASIC2/BASIC3's sharing mode; netcup root servers' exact traffic terms; Contabo's month-to-month price and setup fee; IONOS's minimum term on ionos.de; the EU sites of IONOS VPS, Contabo and Hostinger.
- Unverified: Hetzner Cloud has no snapshot export. Settles whether a disk copy is even possible; not needed for the rebuild route.
- Not measured: UpCloud compute-zone latency (no public speed-test host found) and Hostinger (none found). A read-only `curl` against a server the maintainer creates during a trial would settle both.
- Open: which of the current VPS's "containers and web services" must move, and whether anything outside depends on its IP address (DNS names, allow-lists). Read-only inventory on the VPS before the move.
- Watch: Hetzner's [capacity notice](https://status.hetzner.com/incident/0a75c7ae-3377-41dc-aabe-601063724d24); if it closes, CX43 undercuts every option here.

## Exploration log

Everything run for this ticket on 2026-09-30. Nothing was ordered, created, changed or deleted on any machine or account; no sign-ups, log-ins or payments. Nothing was run on the VPS.

| # | Where | Action | What it changed |
|---|---|---|---|
| 1 | Mac, this worktree | `gh issue view 86`; read `docs/research/cloud-agents-vps-sizing.md`, D4 in `docs/research/cloud-agents.md`, `cloud-agents-vps.md` and `herdr-vps.md` excerpts; `gh pr view 66` (open) | nothing |
| 2 | Web | `curl` of Hetzner's price feed, Cost-Optimized, Regular Performance and General Purpose pages (counted `not-available` labels and "currently unavailable" tooltips), the status incident, the server-auction feed `live_data_sb.json`, the dedicated-server page (prices render in JS, not read) | scratch files outside the repo |
| 3 | Web | `curl` of netcup's VPS, VPS ARM and Root Server pages; parsed plan cards and the embedded plan details (traffic, locations) | scratch files outside the repo |
| 4 | Web | `curl` of OVHcloud's public order catalogue for `vps` and `cloud` (`ovhSubsidiary=DE`) and its Irish VPS page | scratch files outside the repo |
| 5 | Web | `curl` of Scaleway's Instances pricing page, the products and availability API for fr-par-1, the Instance-type guide and the datasheet | scratch files outside the repo |
| 6 | Web | `curl` of IONOS's German and US VPS pages, Contabo's VPS page (its Performance VPS URL returned 404), Hostinger's VPS page, DigitalOcean's Droplet pricing | scratch files outside the repo |
| 7 | Web | `curl` of Vultr `v2/plans` and `v2/regions`, Linode `v4/linode/types` and `v4/regions` (public, no key) | scratch files outside the repo |
| 8 | Web | UpCloud: pricing page and blog return 403 to `curl`; the public API needs an account (401); read the docs changelog, plans and locations pages with `curl`; web searches to find the Starter-plan change; read the pricing page's text in Chrome through the browser extension (one tab, closed after) | a Chrome tab opened and closed |
| 9 | Web | `curl` of Oracle's Always Free resources doc; WebFetch of Hetzner's snapshot FAQ (no export statement found) | nothing |
| 10 | Mac | `dig +short` on about 70 candidate speed-test and looking-glass hostnames to find which exist | nothing |
| 11 | Mac | for 35 hosts: `ping -c 7 -i 0.3` and 7 × `curl -s -o /dev/null -w '%{time_connect}'`, medians computed locally | nothing (outbound probes only) |
