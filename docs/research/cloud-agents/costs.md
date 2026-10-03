# What hosted coding agents cost, and which tickets to send where

This page gives facts and estimates for [Research: cost efficiency of hosted agent providers (#87)](https://github.com/yahyabedirhan/skills/issues/87), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). It answers the money side of decision [D7](README.md#d7-which-hosted-agent-if-any-for-single-ticket-delegation). Other pages say what each service can do, and this page doesn't repeat them:

- [other-providers.md](other-providers.md): Codex, Cursor, Copilot, Jules, Devin, Amp, Factory, OpenHands.
- [claude-code.md](claude-code.md): Claude Code's cloud.
- [managed-agents.md](managed-agents.md): Managed Agents.
- [vps-sizing.md](vps-sizing.md): machine prices.

This research read every price on **2026-09-30** from the vendor's own pricing or docs page, linked inline. It signed up for nothing, paid for nothing and ran nothing in any provider's cloud. Prices are in USD before tax unless marked. Hetzner prices are in EUR net of VAT.

Words this page uses:

- A **delegate** is an agent that takes a ticket and hands back a PR.
- An **effort** is a set of tickets that an orchestrator agent runs together.

Evidence tags:

- **[doc]** the vendor's official docs, pricing page or help center.
- **[post]** the vendor's official announcement on social media.
- **[press]** a news report or third-party write-up. This page uses one only where it found no primary source, and always marks it **unverified**.
- **Estimate** a figure worked out here from the above, with the working shown in [section 2](#2-cost-per-unit-of-work).

## Short answer

- **The model work costs about the same everywhere.** Every metered vendor passes Claude Opus 5.5 through at Anthropic's list price: Anthropic, Cursor, Copilot and Amp alike. That price is $4 input, $0.20 cache read, $5 cache write and $20 output per million tokens. So an Opus-class ticket costs roughly **$1 (small fix), $4 (medium feature) and $28 (a five-ticket effort)** in model usage anywhere (estimate). The difference is who carries the cost: a flat subscription with limits, or a meter.
- **Compute costs little.** A Copilot session on a private repo costs a few cents of Actions minutes. On public repos, those minutes are free. An Amp orb costs $0.33 an hour at the default size. The VPS costs €5.99 a month. None of these changes the total much next to the model cost.
- **The Claude plan is the cheapest place for this maintainer.** The plan's limits already pay for the work, and the maintainer's skills run there. Until the promo credit expires (reported as 4 November), cloud sessions spend that credit first. So they cost nothing against the plan.
- **Worth holding:** the Claude plan. **Worth trying, cheaply:** Copilot Pro ($10) as a second delegate for small, well-specified tickets on public repos, and Jules's free tier. **Not worth holding now:** Cursor, Codex, Devin, Factory, Amp or OpenHands subscriptions. Each one either meters the same model at list price or needs its own setup without the skills.
- **What to try first, while the credit lasts:** send small and medium tickets on public repos to Claude Code cloud sessions. Then run one whole effort in a single cloud session, once the setup script that carries the skills works (E16). Measure how much of the plan one ticket uses before the credit runs out.

---

## 1. How each service bills

### Summary table

| Service | Entry price for this use | Billing unit | What one task draws | Caps | Past the cap | Source |
|---|---|---|---|---|---|---|
| **Claude Code cloud sessions** | Pro $20/month ($17 annual); Max 5x $100; Max 20x $200 | Plan usage (tokens, unpublished allowance) | Tokens, like a local session. No VM charge | Five-hour session window and weekly limit, shared with chat and local Claude Code | Usage credits at API rates, or wait | [pricing](https://claude.com/pricing), [cloud docs](https://code.claude.com/docs/en/claude-code-on-the-web) |
| **Claude Code routines** | Same plans | Plan usage | Tokens | Hourly start caps (below). Routine threads stop at the plan limit | Usage credits, or the service rejects runs | [routines](https://code.claude.com/docs/en/routines) |
| **Claude Code on the VPS** | Plan + VPS €5.99/month (CX23) | Plan usage + fixed server | Tokens | Plan windows; VPS RAM | Usage credits | [vps-sizing](vps-sizing.md) |
| **Codex cloud** | ChatGPT Plus $20/month; Pro $100, $200 or $500 | Plan allowance, then ChatGPT credits | Tokens, converted at credit rates | Five-hour and weekly limits (Pro: no five-hour limit) | Buy credits | [Codex pricing](https://learn.chatgpt.com/docs/pricing) |
| **Cursor Cloud Agents** | Pro $20/month; Pro Plus $60; Ultra $200 | Model API price | Tokens at the chosen model's list price | A spend limit you set at first use | On-demand usage at the same rates | [Cloud Agents billing](https://cursor.com/docs/cloud-agent), [models and pricing](https://cursor.com/docs/models-and-pricing) |
| **Copilot cloud agent** | Copilot Pro $10/month (1,500 AI credits); Pro+ $39 (7,000); Max $100 (20,000) | AI credits (1 credit = $0.01) + Actions minutes | Tokens at model list price, plus runner minutes | 59 minutes per session. Monthly credit allowance | A dollar budget for extra credits | [plans](https://docs.github.com/en/copilot/get-started/plans), [individual billing](https://docs.github.com/en/copilot/concepts/billing-and-usage/individuals/billing) |
| **Jules** | Free. Paid tiers come through a Google AI plan | Tasks per rolling 24 h | One task | Free 15/day, 3 at once; Pro 100 and 15; Ultra 300 and 60 | Wait or upgrade | [Jules limits](https://jules.google/docs/usage-limits/) |
| **Devin** | Free (limited); Pro $20/month; Max $200 | Daily and weekly quota, then on-demand credits (dollars) | Quota share, not published per session | Pro daily and weekly; Max weekly only | Prepaid on-demand credits | [Devin self-serve plans](https://docs.devin.ai/admin/billing/self-serve) |
| **Amp orbs** | Pay as you go; Individual tier $20/month | Orb minutes + model tokens | Minutes by orb size + tokens at API price, no markup | Idle pause after 5 or 20 minutes | Paid credits | [Amp pricing](https://ampcode.com/docs/pricing), [sizes and costs](https://ampcode.com/docs/orbs/sizes-and-costs) |
| **Factory** | Pro $20/month; Plus $100 (managed Droid Computers); Max $200 | Rolling rate limits (5 h, 7 d, 30 d) | Standard credits for model use plus Droid Computer compute | Three rolling windows | Prepaid extra usage, $10 minimum | [Factory individual plans](https://docs.factory.ai/pricing/individuals) |
| **OpenHands Cloud** | Free individual tier | Your own API key, or models at cost | Tokens | 10 conversations a day ([op §6.5](other-providers.md#65-openhands-cloud)) | — | [OpenHands pricing](https://openhands.dev/pricing) |
| *Managed Agents (reference)* | API account, separate from the plan | API tokens + $0.08 per running session-hour | Tokens + runtime | Per-session budget | — | [ma §5](managed-agents.md#5-fit-for-this-maintainer) |

### Claude Code: cloud sessions, routines, projects

- **Plans.** Pro costs $20 a month, or $17 a month billed annually ($200 up front). Max is "From $100", in two tiers: "Max 5x: $100 per month" and "Max 20x: $200 per month". Max is monthly only [doc [claude.com/pricing](https://claude.com/pricing); [What is the Max plan?](https://support.claude.com/en/articles/11049741-what-is-the-max-plan)].
- **Limits.**
  - Pro: "Your session-based usage limit will reset every five hours. Pro plans also have a weekly usage limit that applies across all models". The weekly limit resets "at a fixed time each week that is assigned to your account" [doc [What is the Pro plan?](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan)].
  - Max 5x "includes five times the Pro plan's per-session usage allowance", and Max 20x twenty times. Max has a weekly limit too. Anthropic "may limit your usage in other ways, such as weekly and monthly caps" [doc Max plan].
  - No page states the allowance in tokens or dollars.
  - All surfaces share one limit. Usage "of all different Claude product surfaces (claude.ai, Claude Code, Claude Desktop) counts towards the same usage limit" [doc [How do usage and length limits work?](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work)].
- **Cloud sessions add no compute charge.** They "share rate limits with all other Claude and Claude Code usage within your account. Running multiple tasks in parallel consumes more rate limits proportionately. There is no separate compute charge for the cloud VM" [doc [cloud docs, "Limitations"](https://code.claude.com/docs/en/claude-code-on-the-web)].
- **Routines** "draw down subscription usage the same way interactive sessions do". The docs now give the run caps per hour. The #69 research, a day earlier, found only a daily cap with no stated number. The caps [doc [routines, "Usage and limits"](https://code.claude.com/docs/en/routines)]:
  - Scheduled and one-off runs: 100 an hour per account. Extra runs wait.
  - **Run now**, API fires and re-running a one-off: 30 an hour per routine and 100 an hour per account. Extra actions fail.
  - "None of these hourly limits has overage".
  - At the plan limit: "Without usage credits, additional runs are rejected until your usage window resets".
- **Projects** (parallel threads) use the same limits [doc [projects, "Usage and cost"](https://code.claude.com/docs/en/claude-projects)]:
  - The docs warn: "on a Pro plan in particular you should expect to reach your limit sooner on days you run one".
  - All projects together allow 200 new threads a day.
  - A thread at the limit "waits and continues on its own when the limit resets". So it spends the next window unattended.
  - Threads that a routine started are the exception: they stop.
- **Past the limit.** Usage credits are "billed at standard API pricing rates", with an optional monthly spend cap. Anthropic charges them separately from the subscription [doc [Manage usage credits](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans)]. Prepaid bundles cut that price by 10% ($50 for $45), 20% ($250 for $200) or 30% ($1,000 for $700). Pro and Max accounts can buy up to $2,000 a month [doc [Buy usage bundles](https://support.claude.com/en/articles/14246112-buy-usage-bundles)]. Occasional free "limit resets" set the five-hour or weekly limit back to full [doc [What is a limit reset?](https://support.claude.com/en/articles/17007452-what-is-a-limit-reset)].
- **API list prices.** Usage credits, Cursor, Copilot and Amp all charge these for the same model. Per million tokens [doc [claude.com/pricing](https://claude.com/pricing)]:
  - Opus 5.5: $4 input, $5 cache write, $0.20 cache read, $20 output.
  - Sonnet 5.5: $2, $2.50, $0.20, $10.
  - Haiku 4.5: $1, $1.25, $0.10, $5.
  - Fable 5.1: $10, $12.50, $0.25, $50.
- **A published yardstick.** "Across enterprise deployments, the average cost is around $13 per developer per active day and $150-250 per developer per month, with costs remaining below $30 per active day for 90% of users" [doc [Claude Code costs](https://code.claude.com/docs/en/costs)]. That is spend at API rates. So a daily Claude Code user who pays per token spends more than the $100-200 of a Max plan.
- **Ultrareview.** Each Pro or Max account gets three free runs, and they never refresh. After that, a review costs "typically $5 to $25 in usage credits" [doc [ultrareview, "Pricing and free runs"](https://code.claude.com/docs/en/ultrareview)].

**The promo credit.** In Anthropic's own words, cloud sessions are out of research preview, and "Existing subscribers get a one-time credit to try them: $100 on Pro, $250 on Max". The credit is "an optional one-time credit that your cloud sessions spend first, before falling back onto your normal plan usage" [post [1](https://x.com/ClaudeDevs/status/2102871550974427462), [2](https://x.com/ClaudeDevs/status/2102940480736821610)]. On 2026-09-30, this research found no docs or help-center page with the terms. The Claude Code docs pages above don't mention it.

The rest is **unverified** and comes from press reports only [press [BleepingComputer, 2026-09-25](https://www.bleepingcomputer.com/news/artificial-intelligence/anthropic-rolls-out-up-to-250-in-free-claude-code-credits-but-only-for-cloud-sessions/); [MadRobot](https://madrobot.blog/2026/09/24/claude-code-cloud-sessions-free-credit-how-to-claim/)]:

- Eligibility: individual Pro and Max subscribers who were active when the promotion began on 23 September.
- Claim: by 11:59 PM PT on 7 October, with `/claim-credit` or the banner at claude.ai/code.
- Expiry: 11:59 PM PT on 4 November.
- One credit per account.
- The account needs a GitHub connection.
- In some reports, the credit is **not usable for projects or routines**.

First-hand, #78's cloud session drew on a promotional rate-limit pool. The window of that pool resets on 5 November at 08:00 UTC, which lines up with the reported expiry ([cc §11](claude-code.md#11-cost-and-limits)). No source states how fast the credit burns: at API list rates or at some other rate.

### OpenAI Codex cloud

- **Plans with cloud tasks:** Plus $20/month; Pro "Plans at $100, $200, or $500 USD per month"; Business $20/user/month annual ($25 monthly, 2+ users); Enterprise/Edu. Free ($0) and Go ($8) get only the desktop app's local model. An API key gets "No cloud-based features" [doc [Codex pricing](https://learn.chatgpt.com/docs/pricing)].
- **Allowance.**
  - "Local messages and cloud chats share your plan's usage allowance. Weekly limits may also apply."
  - Plus gets an estimated 15-150 local GPT-6 Sol messages per five hours (15-160 on GPT-6.1 Sol).
  - "Pro plans currently have no five-hour limit". "Cloud tasks may use more of your allowance than local messages". These are "not fixed message limits" [doc Codex pricing].
  - The day before, the same page said that cloud chats on ChatGPT plans use GPT-5.6 Sol ([op §1](other-providers.md#1-openai-codex-cloud)). That sentence is gone, and the page no longer names the cloud model.
- **Credits** pay for use past the allowance: "ChatGPT Plus and Pro users who reach their usage limit can purchase additional credits". Rates per million tokens: GPT-5.6 Sol 100 input, 10 cached, 500 output credits. GPT-6 Sol: 50, 5, 250. GPT-6.1 Sol: 50, 2.5, 250. GPT-6 Luna: 2.5, 0.25, 12.5. There is no cache-write charge. "A typical GPT-5.6 Sol task may use 5-30 credits." Fast mode draws included usage at 2.5x [doc Codex pricing]. The dollar price of a credit on Plus and Pro is on a help-center page that refused automated fetches (HTTP 403). Press reported launch pricing as $40 per 1,000 credits, **unverified** [press [search results](https://www.morphllm.com/codex-pricing)].
- **Best-of-N** (`--attempts 1-4`, [op §1](other-providers.md#1-openai-codex-cloud)) multiplies usage by the number of attempts.

### Cursor Cloud Agents

- **Plans:** Pro $20/month, Pro Plus $60, Ultra $200. Teams cost $40 or $120 per user. Every paid individual plan has two monthly pools:
  - "Cursor Models": Grok 4.5-4.7 and Composer 2.5.
  - "Other Models": third-party models, "charged at the model's API price".

  Unused usage doesn't roll over [doc [models and pricing](https://cursor.com/docs/models-and-pricing); [usage and limits](https://cursor.com/help/models-and-usage/usage-limits)]. Cursor doesn't publish the dollar size of each plan's included pool.
- **Cloud agents bill at API price.** "Cloud Agents are charged at API pricing for the selected model. You can select the context window size, and a larger context window can increase token usage and costs. You'll be asked to set a spend limit when you first start using them" [doc [Cloud Agents, "Billing"](https://cursor.com/docs/cloud-agent)]. The page mentions no separate VM charge.
- **Model prices** match the vendors' prices [doc models and pricing]:
  - Claude Opus 5.5: $4 / $5 / $0.20 / $20.
  - Sonnet 5.5: $2 / $2.50 / $0.20 / $10.
  - GPT-5.6 Sol: $4 / $5 / $0.40 / $20 (promotional through 21 November).
  - Composer 2.5: $0.50 input, $0.20 cache read, $2.50 output.
- **Max Mode** no longer exists on current plans: "Current usage-based plans don't include Max Mode. On legacy request-based plans, Max Mode is billed at the model's API rate plus 20%" [doc usage and limits].
- **Cursor's own yardstick:** "Daily Agent users: Typically $60–$100/mo total usage" and "Power users (multiple agents/automation): Often $200+/mo" [doc models and pricing].
- Long-running agents (hours or days) need Ultra, Teams or Enterprise ([op §2](other-providers.md#2-cursor-cloud-agents-and-the-agent-cli)).

### GitHub Copilot cloud agent

- **Plans and credits:** Pro $10/month (1,000 base + 500 flex = 1,500 AI credits). Pro+ $39 (3,900 + 3,100 = 7,000). Max $100 (10,000 + 10,000 = 20,000). "1 AI credit = $0.01 USD". The flex part "is designed to adapt as the economics of AI evolve", so it can change. Credits reset at 00:00 UTC on the first of each month and don't carry over [doc [usage-based billing for individuals](https://docs.github.com/en/copilot/concepts/billing-and-usage/individuals/billing)].
- **What a session costs.**
  - "Copilot cloud agent uses GitHub Actions minutes and AI credits. The AI credits consumed depend on the model used and the number of tokens processed during the session" [doc [about cloud agent, "usage costs"](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent)].
  - Token prices match the vendors' prices. Claude Opus 5.5: $4 / $0.20 cached / $5 cache write / $20. Sonnet 5.5: $2 / $0.20 / $2.50 / $10 [doc [models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)].
  - Auto model selection takes 10% off model costs on paid plans, also in the cloud agent [doc individual billing].
  - Steering messages cost credits too ([op §3](other-providers.md#3-github-copilot-cloud-agent-formerly-coding-agent)).
- **Past the allowance:** upgrade and pay the difference, or set a dollar budget for additional usage. "a $10 budget covers 1,000 AI credits" [doc individual billing].
- **Actions minutes.**
  - Public repositories on standard runners: free.
  - Private repositories: the account's free minutes come first (GitHub Free 2,000 a month, GitHub Pro 3,000). After that, a Linux 2-core runner costs $0.006 a minute.
  - GitHub always charges for larger runners [doc [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)].
  - Private repos get a 2-CPU / 8 GB runner, and public ones get 4 CPU / 16 GB ([op §3](other-providers.md#3-github-copilot-cloud-agent-formerly-coding-agent)).
- **Cap:** "Each Copilot cloud agent session has a maximum execution time of 59 minutes … If a task exceeds this limit, the session will time out and stop" [doc about cloud agent].

### Jules, Devin, Amp, Factory, OpenHands

- **Jules** counts tasks, not tokens [doc [Jules limits and plans](https://jules.google/docs/usage-limits/)]:
  - Free: 15 tasks a day (rolling 24 h) and 3 at once. Google AI Pro: 100 and 15. Google AI Ultra: 300 and 60.
  - Paid tiers are only for personal `@gmail.com` accounts.
  - "When you are at your limit … you will not be able to trigger new tasks until the limit resets".
  - This research didn't read the Google AI plan prices, because the plans page served a localized, non-USD version. **Unverified.**
- **Devin** has replaced ACUs with quotas and dollar credits [doc [Devin self-serve plans](https://docs.devin.ai/admin/billing/self-serve)]:
  - The free tier has limits.
  - Pro costs $20/month, with "a daily and weekly usage quota". Cloud sessions, the Devin CLI and Devin Desktop share that quota.
  - Max costs $200, with a weekly quota and no daily cap. Teams starts at $80/month.
  - Past the quota, you pay with prepaid on-demand credits that never expire. "On-demand credits are the same dollar value as the ACUs you're used to".
  - Admins can set default session spending limits. A ChatGPT Plus or Pro plan can pay for GPT model use.
  - Devin doesn't publish what one session costs. A review of a public PR at devinreview.com is free [doc same].
- **Amp** bills orbs "by the minute. A paused orb costs nothing" [doc [sizes and costs](https://ampcode.com/docs/orbs/sizes-and-costs)]:
  - Sizes: `a1.tiny` $0.08/h, `a1.small` $0.17, `a1.medium` $0.33, `a1.large` $0.66, `a1.xxlarge` $1.32, `a1.3xlarge` $2.13.
  - An orb pauses 5 minutes after the agent stops or 20 minutes after your last interaction, whichever is later.
  - Opening a thread wakes it. Turn on Orb Saver Mode to stop that.
  - Amp charges model use at providers' API prices: "Amp does not add a markup" [doc [Amp pricing](https://ampcode.com/docs/pricing)].
  - Free (Hobby) is pay as you go. The Individual tier costs $20/month and includes "45,000 minutes of orbin' time" plus some agent usage. The tier can also use a ChatGPT subscription or your own keys.
  - Purchased credits expire after twelve months [doc Amp pricing].
  - Amp doesn't explain what unit the 45,000 minutes count in.
- **Factory** [doc [Factory individual plans](https://docs.factory.ai/pricing/individuals)]:
  - Pro costs $20/month. Plus costs $100 ("~5x Pro usage", managed Droid Computers). Max costs $200 ("~10x").
  - Usage has three rolling windows (5 h, 7 d, 30 d). A session needs room in all three.
  - Sessions draw credits "based on model usage, along with compute usage for Droid Computers".
  - After standard usage, a free open-weight "Droid Core" pool is available.
  - Prepaid extra usage starts at $10 and doesn't expire. Missions pause at a limit.
  - So a hosted Droid Computer needs the $100 tier.
- **OpenHands Cloud**: the individual SaaS tier is free. "Bring your own key or use our providers at-cost" [doc [OpenHands pricing](https://openhands.dev/pricing)]. So the cost is the model tokens alone.

---

## 2. Cost per unit of work

**Everything in this section is an estimate.** No vendor publishes tokens per ticket for its cloud agent. This public repo doesn't record personal usage. So the sizes below are assumptions. They come from the published yardsticks, and this research checked them against each other.

### Assumptions

Three ticket sizes, in tokens of one agent loop. Agent loops resend the conversation each turn, so most input is cache reads.

| Size | What it is | Cache reads | Uncached input + cache writes | Output | Wall time |
|---|---|---|---|---|---|
| **Small fix** | One file or two, a clear spec, tests run once or twice | 1.0 M | 0.1 M | 15 k | 10-20 min |
| **Medium feature** | One ticket from a spec: several files, tests, a PR | 4.0 M | 0.4 M | 60 k | 30-60 min |
| **Effort (~5 tickets)** | Five medium tickets + an orchestrator (3 M / 0.3 M / 40 k) + one small fix-up round per ticket | 28 M | 2.8 M | 415 k | 3-6 h |

Where the sizes come from:

- The Managed Agents research priced one sub-agent ticket on Opus 5.5 at 3 M cached reads, 0.3 M writes and 60 k output. That came to about $3.30, and a six-ticket effort to "plausibly $20-40" ([ma §5](managed-agents.md#5-fit-for-this-maintainer)). The medium size here is slightly larger.
- Anthropic's average is $13 per active day, and under $30 for 90% of developers [doc costs]. That fits three medium tickets a day at about $4 each.
- Cursor's "Daily Agent users: Typically $60–$100/mo" [doc Cursor models and pricing] fits a small or medium ticket most working days.
- Codex's "A typical GPT-5.6 Sol task may use 5-30 credits" [doc Codex pricing] is below this page's small fix (about 28 credits, below). So either Codex's own typical task is smaller than these sizes, or GPT models use fewer tokens for the same work.
- Ultrareview's $5-25 per review [doc ultrareview] pays for a review by many agents. So it sits between a medium ticket and an effort.

Model rates: Opus-class uses Opus 5.5 ($4 / $5 / $0.20 / $20). Sonnet-class uses Sonnet 5.5 ($2 / $2.50 / $0.20 / $10) [doc claude.com/pricing]. The working for Opus:

- Small = 1.0 × 0.20 + 0.1 × 5 + 0.015 × 20 = $1.00.
- Medium = 0.80 + 2.00 + 1.20 = $4.00.
- Effort = 5 × $4.00 + $2.90 orchestrator + 5 × $1.00 = $27.90.

For Sonnet: $0.60, $2.40, $16.75.

### The table

"Cash per unit" is what the unit adds to the bill beyond the subscription. "Usage value" is the same work at list rates. That is what the work costs after you pass a plan's limit, and what it takes out of a credit or allowance.

| Where | Cash per unit (small / medium / effort) | Usage value, Opus-class | Usage value, cheaper model | Fixed monthly cost | Notes |
|---|---|---|---|---|---|
| **Claude Code cloud session** | $0 / $0 / $0 inside the plan's windows | $1 / $4 / $28 | Sonnet: $0.60 / $2.40 / $17 | Pro $20, Max $100-200 | Sessions spend the promo credit first. If it burns at list price (unverified), $250 is about 60 medium tickets or 9 efforts, $100 about 25 or 3.5 |
| **Claude Code routine** | $0 inside the windows | same | same | same | Promo credit reportedly not usable (unverified). A routine thread stops at the limit |
| **Claude Code on the VPS** | $0 inside the windows, plus about €0.30 of server per ticket at 20 tickets a month | same | same | Plan + €5.99 (CX23) | No promo credit (cloud sessions only). Same plan use per ticket as a cloud session |
| **Codex cloud** | $0 inside the allowance | GPT-5.6 Sol credit rates: about 28 / 110 / 700 credits. At a reported $0.04 a credit (unverified): $1.10 / $4.40 / $28 | GPT-6.1 Sol about half | Plus $20 | No hosted orchestrator: the effort's orchestration stays local. Best-of-N multiplies usage |
| **Cursor Cloud Agents** | Opus 5.5 at list: $1 / $4 / $28 | $1 / $4 / $28 | Composer 2.5: $0.29 / $1.15 / $8 | Pro $20 | Cursor doesn't say whether cloud runs use the plan's included pool first. Sub-agents make one cloud agent an orchestrator |
| **Copilot cloud agent** | AI credits: 100 / 400 / 2,500 on Opus 5.5 (inside Pro's 1,500 for about 3 medium tickets a month) | $1 / $4 / $25 (no orchestrator) | Sonnet 5.5: 60 / 240 / 1,500 credits. 10% off with Auto | Pro $10 | Actions: $0 on public repos. Private: about $0.12 / $0.36 / $1.80 at $0.006 a minute, within the free minutes. 59-minute cap per ticket |
| **Jules** | $0 inside 15 tasks a day | not metered | — | $0 (free tier) | Gemini models. Paid tiers come through a Google AI plan (price unverified) |
| **Devin** | $0 inside the quota | not published | — | Pro $20 | Per-session cost unverified |
| **Amp orbs** | Orb `a1.medium`: about $0.14 / $0.36 / $1.80 (including the 5-minute idle tail), plus tokens | $1 / $4 / $28 at list, no markup | cheaper models at their list | $0 (Hobby) or $20 | Tokens dominate. The orb is under 10% |
| **Factory** | $0 inside the rate limits | not published | Droid Core pool free | Pro $20; Plus $100 for hosted computers | Per-session cost unverified |
| **OpenHands Cloud** | Tokens only, own key or at cost: $1 / $4 / $28 | same | any model | $0 | 10 conversations a day |
| *Managed Agents* | $1.03 / $4.08 / $28.40 (tokens + $0.08 a running hour) | — | — | API account | For reference ([ma](managed-agents.md)) |

### What the table says

- **For the same model, the per-ticket cost is the same within a few percent.** Every metered vendor charges Anthropic's list price for Opus 5.5. Cursor, Copilot and Amp say so on their pricing pages. A service is cheaper only if it uses a cheaper model (Composer, Sonnet, GPT-6 Luna) or folds the work into a flat subscription.
- **The Claude plan turns the table's usage value into $0 cash** until a window runs out. Anthropic doesn't publish how many tickets fit in a window. It states limits only as multiples of Pro. That is the one number worth measuring (open question 2).
- **Copilot Pro's $10 buys about $15 of model use** (1,500 credits). That is about three Opus medium tickets or six Sonnet ones a month, or many more small fixes. It is the cheapest paid second delegate, as long as each ticket finishes inside 59 minutes.
- **Compute costs are tiny:** Actions minutes, orb minutes and the VPS together come to a few dollars a month at this volume.

---

## 3. Beyond the price

| | Setup effort | Do the maintainer's skills carry over? | Review burden | Caps and failure modes that waste spend | Private repos |
|---|---|---|---|---|---|
| **Claude Code cloud** | Low: already used (#78). The setup script that installs the skills (E16) is the remaining step ([wf §2](session-workflow.md#2-carrying-the-skills-and-global-instructions-into-cloud-sessions)) | Yes, once the setup script installs them. Skills in the VM's home load | Lowest: same harness, same skills and conventions as local work | Idle reclaim kills background sub-agents and shell work. The tokens are spent, and the work is lost unless pushed [doc cloud, "Environment expired"]. A permission prompt stalls an unattended run ([wf](session-workflow.md)). Parallel sessions draw proportionately. Project threads resume into the next window on their own | Same vendor as the plan. The Claude GitHub App needs access to the repo |
| **Claude Code on the VPS** | Medium: Herdr, skills, worktree tool, notifications (D2, D3) | Yes, unchanged | Lowest | No swap on CX23: running out of RAM kills agents ([siz](vps-sizing.md)). Plan windows as above | Code stays on a machine the maintainer controls |
| **Codex cloud** | Medium: a web-made environment per repo, internet off by default | Unverified. `AGENTS.md` yes ([op §1](other-providers.md#1-openai-codex-cloud)) | Medium: no skills, so conventions only from `AGENTS.md` | Internet off by default makes dependency installs fail. Best-of-N multiplies usage. Fast mode costs 2.5x. No follow-up from a shell | Grants the ChatGPT GitHub connector repo access |
| **Cursor Cloud Agents** | Medium: GitHub app, environment, spend limit, skills copied into `~/.cursor/skills` | Partly: `~/.cursor/skills` and account User Rules sync ([op §2](other-providers.md#2-cursor-cloud-agents-and-the-agent-cli)) | Medium | Metered from the first token. Larger context windows cost more. Sub-agents can run a named third-party model at list price [doc usage and limits] | Privacy Mode blocks Fable models without a data-retention approval [doc models and pricing] |
| **Copilot cloud agent** | Low: assign an issue. Put `copilot-setup-steps.yml` on the default branch for tools | No personal skills. `AGENTS.md` and `CLAUDE.md` yes ([op §3](other-providers.md#3-github-copilot-cloud-agent-formerly-coding-agent)) | Medium: a draft PR per task, steering only on the web | **59-minute hard cap**: a timed-out session has spent its credits. Steering messages cost credits. A failed setup step still starts the agent without its tools | Actions minutes count (small). Private runners are half the size of public ones |
| **Jules** | Low: Google sign-in and GitHub app | Unverified. `AGENTS.md` yes | Medium: plan approval step | Task count, not spend: a failed task still uses one of 15 | Grants Google repo access |
| **Devin** | Medium | Only `SKILL.md` files in connected repos | Medium | Daily and weekly quotas | Grants Cognition repo access |
| **Amp orbs** | Medium | Yes: Amp hosts personal skills and a global `AGENTS.md` | Medium | Amp bills the idle tail of 5-20 minutes. Opening a thread wakes the orb. **Ship** pushes to the base branch by default | Grants Amp repo access |
| **Factory** | Medium. Hosted computers need the $100 tier | Only on a persistent Droid Computer | Medium | Three rolling windows. Missions pause at a limit | Grants Factory repo access |
| **OpenHands Cloud** | Medium. Good models need an API key | Skills from a Git repo via `/launch` | Medium | 10 conversations a day | Grants All Hands repo access |

Three points matter more than price:

- **The skills make the biggest difference.** This repo's workflow (orchestrate, implement, to-pr, code-review) turns a ticket into a reviewable PR in the maintainer's format. A delegate without it hands back work that needs more review and more rework. Rework rounds cost as much as the first pass. Claude Code (cloud or VPS) is the only place where the skills run unchanged.
- **Caps decide which tickets fit, not just what they cost.** A Copilot ticket must finish in 59 minutes. A Claude cloud session must not stay idle long enough for the service to reclaim it while sub-agents work. A routine thread stops at the plan limit instead of waiting.
- **Every extra vendor is another GitHub App with repo access.** For public repos, that costs little. For private repos, each one is another company that holds the code. Claude Code on the VPS keeps the code on the maintainer's machine. Claude Code cloud keeps it with the vendor that the maintainer already pays.

---

## 4. Delegation guide

### Which ticket goes where

| Ticket kind | Send it to | Why |
|---|---|---|
| Small, well-specified fix on a public repo | Claude Code cloud session now (promo credit). Copilot if held | $0 cash. Copilot's Actions minutes are free on public repos, and a small fix fits 59 minutes |
| Medium feature that needs the repo's skills | Claude Code cloud session (after E16), else the VPS | Only place the skills run unchanged. No cash cost inside the plan |
| Whole effort (orchestrator + ~5 tickets) | The VPS (or the Mac). One cloud session once E16 and E17 pass | Idle reclaim and one level of sub-agents make cloud orchestration fragile today ([D1](README.md#d1-where-does-an-orchestrated-effort-run)) |
| Long unattended work (over an hour) | The VPS | No idle reclaim and no 59-minute cap. Cursor's long-running agents need Ultra ($200) |
| Private-repo tickets | The VPS or Claude Code cloud | No new vendor gets the code |
| Recurring chores (nightly checks, dependency bumps) | Claude Code routines | Plan usage. Hourly start caps are far above need |
| Browser or UI checks | Claude Code cloud (headless Chromium, allowlisted hosts) | Already there ([sp §1](session-probe.md#1-headless-browser)) |
| A second opinion from another model family | Jules free tier, or Copilot with a GPT model | $0 or inside Copilot's credits. Don't subscribe for this alone |

### Which subscriptions to hold

- **Hold: the Claude plan.** Everything above depends on it. Pro or a Max tier: the right choice depends on how many tickets fit in a window, and only measurement can tell (open question 2). A rule of thumb from the table: if usage credits past Pro's limit would cost more than $80 a month, Max 5x is cheaper. $80 is about 20 medium tickets at list price.
- **Keep: the VPS at €5.99.** It is the cheapest place to run whole efforts and private-repo work once the promo credit is gone.
- **Try, only if you want a second delegate: Copilot Pro at $10.** It is the cheapest paid option, it lives in GitHub, and minutes are free on public repos. Use it for small, self-contained tickets. Cancel it if the PRs need heavy rework.
- **Try for free: Jules.** 15 tasks a day at no cost is enough to see whether its PRs are usable on small public-repo tickets. It needs a sign-up.
- **Don't hold now:**
  - **Cursor Pro.** It meters the same models at list price on top of $20. Its advantages (a follow-up API, skill sync, a desktop for computer use) matter only if a script must steer a delegate.
  - **ChatGPT Plus for Codex.** It is a reasonable $20 if the maintainer wants ChatGPT anyway. But cloud chats take no follow-ups from a shell, and the skills don't load.
  - **Devin, Factory and Amp.** Each is another $20+ subscription or meter, for features that the Claude plan and the VPS already give.
  - **OpenHands.** It is free, but good models need a paid API key, and that is list-price metering again.
  - **Managed Agents.** API billing comes on top of the plan, and the skills don't run there ([ma](managed-agents.md)).

### What to try first while the promo credit lasts

Press reports say that the maintainer must claim the credit by 7 October and spend it by 4 November (unverified). The maintainer has already seen #78's session paid from it, per [D12](README.md#d12-the-promo-credit-and-the-one-unused-cloud-session).

1. **Measure.** Before and after one medium cloud ticket, read claude.ai/settings/usage (credit balance). Also read `/usage` in a local session (plan windows). This gives the credit burn per ticket. After the credit ends, it gives the share of a window per ticket. Keep the figures private.
2. **Send small and medium tickets on public repos** as cloud sessions with self-contained briefs. Check the PR quality and the review time.
3. **Make E16 work**: the environment setup script that installs the skills. Then run one medium ticket that uses them.
4. **Run one whole effort in a single cloud session** once E16 works. Watch it to see whether idle reclaim or permission prompts waste it (E17).
5. **Don't spend it on projects or routines** until it's clear whether the credit covers them. Press reports say it doesn't.

---

## Open questions

| Question | Why open | How to settle it |
|---|---|---|
| 1. Does the promo credit burn at API list rates, and does it cover projects and routines? | Only social posts and press reports. No terms page found | Run one cloud session, compare its list-price cost in the Session block of `/usage` (after `--teleport`) with the credit's drop at claude.ai/settings/usage |
| 2. How much of a Pro or Max window does one medium ticket use? | Anthropic publishes limits only as multiples of Pro | `/usage` before and after one ticket, once the credit is gone. Keep the result private |
| 3. What does a Codex credit cost on Plus and Pro? | The help-center page returned HTTP 403. $40 per 1,000 is from press | The maintainer reads the page in a browser |
| 4. Which model do Codex cloud chats use on Plus now? | The pricing page dropped the "GPT-5.6 Sol" sentence between 2026-09-29 and 2026-09-30 | Recheck the docs, or look at a cloud chat's model label |
| 5. Do Cursor cloud runs draw on the plan's included pool before on-demand spend? | The Cloud Agents page says "API pricing" and a spend limit, not which pool | Cursor support, or the Spending dashboard after one run |
| 6. What does one Devin or Factory session cost? | The vendors don't publish quotas in units per session | Only by using them. Not worth a sign-up now |
| 7. What unit are Amp's "45,000 minutes of orbin' time" in? | The pricing page doesn't explain it | Amp's pricing FAQ in a browser |
| 8. What do Google AI Pro and Ultra cost? | The plans page served a localized, non-USD version | Read the page with a US locale in a browser |
| 9. Does a Copilot session that hits 59 minutes keep its commits? | The docs say it "will time out and stop", not what happens to pushed work | One deliberately long task on a throwaway branch, if Copilot is held |

## Exploration log

All steps ran on 2026-09-30, on the Mac, in this ticket's worktree or the agent's scratch folder. No sign-ups, payments or cloud runs.

| # | Where | Action | What it changed |
|---|---|---|---|
| 1 | Mac (worktree) | `gh issue view 87`. Read `other-providers.md`, `claude-code.md` §11, `managed-agents.md`, `vps-sizing.md`, and D7, D12 and the maintainer's answers in `README.md` | Nothing |
| 2 | Mac (scratch) | `curl` of the Markdown form of Claude Code's costs, cloud, routines, projects and ultrareview pages; `platform.claude.com` pricing; Codex pricing, cloud and `llms-full.txt`; Cursor Cloud Agents, models and pricing, usage limits, help pricing, `llms.txt`; Devin self-serve plans; Factory individual plans | Copies in the scratch folder only |
| 3 | Mac (scratch) | `curl` and text extraction of claude.com/pricing and the Claude help-center articles on the Pro and Max plans, usage limits, usage credits, bundles, limit resets and Claude Code with Pro or Max. Two old article URLs returned 404. The pages' links gave their current URLs | Scratch folder only |
| 4 | Mac (scratch) | `curl` of GitHub docs article bodies: Copilot plans, individual billing, models and pricing, optimizing usage, about cloud agent, Actions billing | Scratch folder only |
| 5 | Mac (scratch) | `curl --compressed` and text extraction of Jules limits, Amp sizes and costs and pricing, OpenHands pricing, and the Google AI plans page (served in a non-US locale, so not used) | Scratch folder only |
| 6 | Web | WebSearch for the promo credit's terms (two queries) and Codex credit prices; WebFetch of two press reports on the credit; WebFetch of OpenAI's credits help article (HTTP 403) | Nothing |
| 7 | Mac (worktree) | Wrote this file. No commit | This file only |
