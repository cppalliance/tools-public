# Prompts, rulebooks, how-tos, and lessons for building things with language models.

Vinnie Falco builds things that other people end up depending on. He wrote Beast, the HTTP and WebSocket library that became the second most used library in Boost, and he did it by copying what worked, measuring what did not, and iterating for years until the interface felt inevitable. That is the whole method, and it has never changed: take in the problem, try something, measure, adjust, repeat. The domain rotates - networking, JSON, URLs, coroutines, standards papers, now language models - but the loop stays the same. When AI arrived he treated it the way he treats everything, as a craft to be acquired through volume, and put in a thousand hours before he let himself believe he was any good at it. The tools in this repository are what came out the other side.

What makes them different is that he builds prompts like he builds APIs. Every instruction has to survive the removal test: delete it and something must break, or it does not belong. Every rule names a concrete artifact. Every tool has one job, a clear boundary, and a persona that tells you exactly what posture it will take before you read the first line - the Lawyer prosecutes, the Vintner asks for nothing, the Host sets the table so the reader feels smart, the Debt Collector reminds your shims that they will retire whether they invoke omerta or not. The personas are not decoration. They are interface design applied to language: a name that compresses a hundred rules into a single expectation, so the model and the human both know what they are holding. He calls this Name the Thing, and once you see it you cannot stop seeing it in every tool here.

The result is a workshop, not a toolbox. There are rulebooks that make a model write C++ or Rust or Python the way a maintainer would. There are how-tos distilled from the written records of real thinkers, so you can borrow the judgment of a Dimov or a Voutilainen without borrowing their calendar. There are agents that plan, agents that execute, agents that hunt technical debt and stakeholder rot and machine-generated prose. There are analysts that diagnose institutions, read intercepted communications cold, and score how well an engineer actually drives a model. And there are the lessons - the postmortems from building all of it, including the ones where the tools failed. Everything is here because it was needed for real work, on real targets, against real deadlines, and everything was sharpened until it produced the same output on the tenth run as it did on the first. Load one. See what it does.

![The Creator](images/the-creator.jpg)

---

What follows is arranged by what you want to do, not by what the files are. Start with the **How-Tos** when you want to think like someone better than you at a specific thing - a library designer who ships nothing he cannot defend, a documentarian who has spent twenty years making powerful people answer questions, an agent builder who treats the KV cache as sacred ground. Reach for the **Rulebooks** when you want a model to write C++, Rust, Python, TypeScript, or a WG21 paper the way a maintainer would, with every style question settled by the tool and none left to taste. Open the **Agents** when you want a conversation that accumulates into something: a filing clerk that enforces your own schema, a siege engineer who builds until your goal becomes inevitable, a game theorist who turns your strategic mess into equilibria you can act on. And when you want a verdict rather than a draft, the **Analysis** tools will diagnose an institution, cross-examine a consulting firm, read intercepted communications cold, or score how well your engineers actually drive a model - sourced, tiered, and unafraid to name what they find.

Then the work gets built. **Planning** hands you the Architect, who accumulates your design into a plan that is enough, the Vibe Coder, who executes it as tested commits, and the Debt Collector, who comes for whatever the work left behind. **WG21** is a full committee toolchain: forge a paper that survives a hostile third pass, turn a raw transcript into two-layer minutes, trace a delegate's pedigree from the public record, write the trip report nobody else will write. **Writing** gives you a booksmith, a documentarian who finds the explanation your code already contained, a dramaturg who hears the machine cadence your ear cannot, and a slide renderer that never drifts. The **Lessons** tell you why any of it works - the fan-out problem, the semantic blur, the design ledger - written from postmortems, not theory. **Exhibits** show the tools' output on real targets, so you can judge the results before you spend a token. Every category was cut from real work under real deadlines, and every tool in it was sharpened until it did the same thing on the tenth run as on the first. Pick the one that matches the problem on your desk.

---

![How-To](images/how-to.jpg)

## How-Tos

Guides distilled from how real people think and work, written for humans to read. Thirteen manuals covering C++ design, AI tool building, investigative journalism, visual storytelling, web operations, and more, plus the tool that distills new ones. Everything lives in [how-to/](how-to/).

**How to Tell Visual Stories with a Camera**\
_[how-to/how-to-collier-landry.md](how-to/how-to-collier-landry.md)_\
Craft beats gear, truth beats polish, and the story nobody else will tell is the one worth making. This manual distills Collier Landry's record as a director of photography and filmmaker into 55 transferable rules on visual storytelling, craft, career, and creative resilience. Operate it and your camera stops collecting footage and starts earning the trust an audience grants only to creators who visibly take the risk.

**How to Design Minimal Safe C++ APIs**\
_[how-to/how-to-dimov.md](how-to/how-to-dimov.md)_\
Shipping too much is irreversible, while shipping too little is always correctable. This reference teaches you to judge C++ designs the way Peter Dimov does - API minimalism, safe defaults, undefined-behavior elimination, contracts, type invariants, and generic programming. Operate it and every interface element you ship has earned its place, with the safe path requiring zero annotation and zero justification.

**How to Build AI Tools and Prompts**\
_[how-to/how-to-falco.md](how-to/how-to-falco.md)_\
Keep the main context clean, and write every instruction so only one reading is possible. This manual teaches you to build AI tools, super prompts, and plan files that execute reliably under context pressure. Operate it and your tools produce the same output across runs and fresh contexts, because every rule names a concrete artifact and passes the removal test.

**How to Design C++ Libraries for Review**\
_[how-to/how-to-glen.md](how-to/how-to-glen.md)_\
Build libraries from the allocator up, and treat every public header as a contract. This manual distills Glen Fernandes' record on C++ library design, allocator models, pointer utilities, alignment, API hygiene, and community review practice. Operate it and well-specified abstractions carry the complexity, so your user code stays minimal, portable, and unsurprising all the way through review.

**How to Build Software with AI Without Cutting Corners**\
_[how-to/how-to-greg-bildson.md](how-to/how-to-greg-bildson.md)_\
Speed is cheap and discipline is rare, so spend a little speed to buy durability. This manual distills Greg Bildson's written record into 63 directives on steering AI coding sessions, durable plans and records, design judgment, security and data governance, teams, network health, and business strategy. Operate it and your AI-built software survives, because a decision that is not written down in a durable artifact does not exist.

**How to Design Precise Technical Interfaces**\
_[how-to/how-to-klemens.md](how-to/how-to-klemens.md)_\
Name things honestly, and make invalid states unrepresentable. This reference teaches you to evaluate technical designs through precise naming, ownership enforcement, minimal API surfaces, evidence-based evolution, and verifiable review criteria. Operate it and misuse fails at compile time instead of in production, with every expectation stated in terms anyone can verify.

**How to Build Software With Coding Agents Without Losing Control**\
_[how-to/how-to-mario-zechner.md](how-to/how-to-mario-zechner.md)_\
Generation is cheap and understanding is expensive, and complexity is the mind killer. This manual distills Mario Zechner's record into 98 directives on refusing scope, keeping architecture in human hands, delegating bounded agent work, reviewing generated output, engineering context, and owning the harness. Operate it and your coding agents ship bounded, reviewed work while you keep control of everything that matters.

**How to Investigate and Hold Power Accountable**\
_[how-to/how-to-nowosielski.md](how-to/how-to-nowosielski.md)_\
Accountability requires both rigorous evidence and compelling storytelling - one without the other fails. This manual distills a documentarian's two decades investigating intelligence failures, police misconduct, and institutional cover-ups into 96 rules on developing sources, verifying evidence, parsing official language, detecting cover-ups, and surviving adversarial pressure. Operate it and you plan interviews as staircases of escalating questions, spot the non-denial denial, and hold power to account with evidence that holds.

**How to Build AI Agents That Work in Production**\
_[how-to/how-to-peak-ji.md](how-to/how-to-peak-ji.md)_\
The agent is its context. This manual distills Yichao "Peak" Ji's record into 63 directives on KV-cache discipline, memory and compression, agent behavior and trust, action space, evaluation, autonomy, and product strategy. Operate it and your agents survive contact with real workloads, because every discipline from caching to evaluation shapes context so the model's own intelligence can do the work.

**How to Evaluate Language Change Proposals**\
_[how-to/how-to-spicer.md](how-to/how-to-spicer.md)_\
A language change is irreversible, so its cost must be paid up front or it will be paid later by users who never agreed to it. This manual distills a long record of committee argument into 100 directives on silent breakage, special-case cost, specification, implementability, evidence discipline, and consensus timing. Operate it and you evaluate proposals for a language that cannot be unshipped with the stringency that permanence demands.

**How to Navigate C++ Committee Design Decisions**\
_[how-to/how-to-ville.md](how-to/how-to-ville.md)_\
"I feel" spells lack of rationale by definition. This reference teaches you to judge C++ designs the way Ville Voutilainen does - rationale, committee process, implementation experience, compatibility, language-design principles, and safety. Operate it and you judge on evidence rather than taste or urgency, extending the language only where the change costs nothing to those who opt out.

**How to Evaluate C++ Language and Library Designs**\
_[how-to/how-to-vinnie.md](how-to/how-to-vinnie.md)_\
Start from measurable user value and require working evidence. This reference teaches you to evaluate C++ designs through evidence, user value, minimal scope, semantic interfaces, layering, generic composition, dependency control, and measurable cost. Operate it and you discount demand from people who will not bear a feature's costs, and every permanent trade-off gets made explicit before it gets made permanent.

**How to Build and Run Web Applications**\
_[how-to/how-to-wiles.md](how-to/how-to-wiles.md)_\
The cheapest work is the work you never do. This manual distills consulting practice into 87 directives on query measurement, doing less work, testing, automation, conventions, observability, and project structure. Operate it and your web application stays fast, verifiable, and cheap to keep alive over years rather than months, because you remove work entirely before trying to make it faster.

**Make How-To**\
_[how-to/make-how-to.md](how-to/make-how-to.md)_\
Every mind leaves a written record, and every record can become a manual. This meta-tool builds a how-to manual that teaches how a named person thinks and works, from their written record - parallel search, parallel distillation into plain-bullet rules, then mechanical assembly, dedupe, trim, and thematic grouping. Operate it and you mint a new manual for any thinker with a corpus, with themes that emerge from the evidence rather than a structure decided in advance.

![Rulebooks](images/rulebooks.jpg)

## Rulebooks

Style and format references to apply to prompts, plans, and reviews. Sixteen rulebooks covering programming languages, compiler maintenance, and writing forms. Everything lives in [rulebooks/](rulebooks/).

**Writing C++**\
_[rulebooks/cpp-rulebook.md](rulebooks/cpp-rulebook.md)_\
Welcome to the C++ Workshop, where questions of style are settled by the tool, not by taste. This rulebook equips a model to write, extend, and maintain C++ - project layout, naming, headers, RAII, smart pointers, error handling, modern features, templates, concurrency, testing, tooling, and performance. Load it and every edit comes out idiomatic and safe, with no uninitialized reads left behind for the compiler to silently exploit.

**Writing Paper Abstracts**\
_[rulebooks/create-abstracts-rulebook.md](rulebooks/create-abstracts-rulebook.md)_\
A delegate triages your abstract in seconds, not minutes, and most often it is the only part they read. This rulebook writes the abstract for a WG21 paper as one actionable finding stated first, with no manufactured hook. Load it and your abstract survives triage, so the rest of your paper actually gets read.

**Writing Fiction**\
_[rulebooks/fiction-rulebook.md](rulebooks/fiction-rulebook.md)_\
End every scene with the character worse off than at the start. This rulebook holds the rules for writing fiction that reads as if a human wrote it, distilled from 40+ sources across five research domains - read it to learn the craft, or hand it to a model to apply it. Load it and the Over-Explain, the single most common AI fiction failure, never makes it onto your page.

**Writing HTML and CSS**\
_[rulebooks/html-css-rulebook.md](rulebooks/html-css-rulebook.md)_\
Welcome to the Web Design Atelier, where div soup goes to die. This rulebook equips a model to write, review, and clean up HTML and CSS - semantic markup, forms, media, modern layout, custom properties, cascade layers, accessibility, responsive design, and performance. Load it and every violation is mechanically detectable with a concrete bad-to-good correction, so your markup comes out semantic and accessible by construction.

**Writing JavaScript**\
_[rulebooks/javascript-rulebook.md](rulebooks/javascript-rulebook.md)_\
In this workshop, a `var` is always a cleanup target and no promise is ever left floating. This rulebook equips a model to write, review, and clean up modern JavaScript - language syntax, modules, async, errors, DOM and platform APIs, Node.js, security, testing, and linting. Load it and your JavaScript comes out ES2022+-clean, with the traps of loose equality and unhandled rejections defused before they fire.

**Maintaining Clang and LLVM**\
_[rulebooks/maintain-clang-rulebook.md](rulebooks/maintain-clang-rulebook.md)_\
The Dragon Keepers tend the tree, and the tree has its own idioms. This rulebook equips a model to read, modify, and extend Clang and LLVM - architecture, conventions, core APIs, extension recipes, testing, and build/debug workflow. Load it and your changes read as native LLVM, written the way the project writes itself.

**Maintaining GCC**\
_[rulebooks/maintain-gcc-rulebook.md](rulebooks/maintain-gcc-rulebook.md)_\
The GNU Toolsmiths match GNU style exactly, down to the lowercase message with no trailing period. This rulebook equips a model to read, modify, and extend GCC - architecture, conventions, core APIs, extension recipes, testing, and build/debug workflow. Load it and your patches arrive formatted, styled, and pipelined the way GCC review expects.

**Writing News Stories**\
_[rulebooks/news-rulebook.md](rulebooks/news-rulebook.md)_\
Accuracy has no close enough, and the lead never gets buried. This rulebook writes or audits a news article, feature, analysis, briefing, or press release for structure, leads, sourcing, style, and objectivity. Load it and you produce copy that editors run and readers finish, because you tried to disprove your own story before anyone else could.

**Writing Technical Papers**\
_[rulebooks/papers-rulebook.md](rulebooks/papers-rulebook.md)_\
The delegate reads in passes and stops when a pass fails - and the third pass is hostile. This rulebook drafts a WG21 paper that shows, then asserts, surviving the brutal summary and the hunt for what the paper omits. Load it and your paper earns each next pass instead of widening into drift that reads as marketing.

**Writing Unambiguous Model Instructions**\
_[rulebooks/prompts-rulebook.md](rulebooks/prompts-rulebook.md)_\
Write every instruction so that only one reading is possible. This rulebook writes or audits a prompt, plan, tool, or rule file for unambiguous instructions and efficient context management. Load it and your instructions spend the smallest set of high-signal tokens that makes the desired outcome likely, with escape hatches where reality refuses to cooperate.

**Revising Model Prose to Human Standard**\
_[rulebooks/prose-rulebook.md](rulebooks/prose-rulebook.md)_\
Generated prose narrates its own structure; human editors cut the narration and keep the content. This rulebook revises model-generated prose so it reads as human-written, in sequential editing passes from structure to wording. Load it and the verdict coinages, the meta-narration, and the pile-of-documents agency all get hunted out of your text.

**Writing Python**\
_[rulebooks/python-rulebook.md](rulebooks/python-rulebook.md)_\
Every rule is an imperative, every prohibition names the behavior that replaces it, and every quantity is a number or a range. This rulebook equips a model to write and maintain Python 3.12+ - project layout, packaging, naming, idioms, typing, errors, API design, imports, dependencies, documentation, testing, tooling, performance, concurrency, and anti-patterns. Load it and your Python encodes the modern generation of syntax and tooling, with authority checkable against the PEPs.

**Reading Technical Papers**\
_[rulebooks/read-papers-rulebook.md](rulebooks/read-papers-rulebook.md)_\
A disguised reader gap becomes a false defect, and a disguised defect becomes false praise. This rulebook evaluates a paper's quality in three sequential passes, each with exit criteria, from the general idea to the depth a verdict needs. Load it and you virtually re-implement the target before you judge it, so your verdict rests on honest confidence instead of a skim.

**Structuring Reports**\
_[rulebooks/reports-rulebook.md](rulebooks/reports-rulebook.md)_\
Lead with the answer, because scanners read the first two words and skip the rest. This rulebook writes or audits a report of any type for structure, evidence, uncertainty, sourcing, and format discipline. Load it and your reports get read and acted on, with facts that resist verification flagged instead of smoothed into certainty.

**Writing Rust**\
_[rulebooks/rust-rulebook.md](rulebooks/rust-rulebook.md)_\
Fix a borrow error by restructuring ownership, never by reaching for `unsafe`. This rulebook equips a model to write, extend, and maintain Rust - project layout, naming, ownership, API design, errors, crates, documentation, testing, tooling, performance, async, and unsafe. Load it and your Rust comes out ownership-first and tool-settled, with examples that compile and dependencies that cannot turn a typo into a supply-chain compromise.

**Writing TypeScript**\
_[rulebooks/typescript-rulebook.md](rulebooks/typescript-rulebook.md)_\
`strict: true` is the floor, not the ceiling. This rulebook equips a model to write, review, and clean up TypeScript - configuration, type discipline, imports, errors, async, validation, naming, testing, linting, and publishing. Load it and your codebase takes no `any` in application code, receives external data as `unknown`, and validates everything at the boundary.

![Agents](images/agents.jpg)

## Agents

Self-contained conversational agents. Each one takes a goal, a subject, or a workspace and produces a structured strategic or behavioral document. Everything lives in [agents/](agents/).

**The Cabinet**\
_[agents/cabinet.md](agents/cabinet.md)_\
Files multiply, names drift, directories sprout like weeds, and the thing you wrote last Tuesday is already lost in the undergrowth. On load, this agent becomes a filing clerk that reads your workspace schema, classifies documents, routes them to correct directories, and maintains frontmatter and naming conventions. Run it and your workspace stays filed with the quiet persistence of someone who files for a living, because the Cabinet does not invent the system - it enforces yours.

**Vauban the Converger**\
_[agents/converge.md](agents/converge.md)_\
A fortress besieged by Vauban is a fortress taken - not because Vauban attacks, but because he builds until the geometry of the position makes resistance more expensive than surrender. Given a goal, this agent produces either an architecture of inevitability that survives adversarial testing at every step, or an honest stop-and-redirect when the goal cannot be made inevitable. Run it and your plan is stress-tested by an engineer of equal caliber standing on the other wall before it ever meets reality.

**The Mentographist**\
_[agents/mentograph.md](agents/mentograph.md)_\
Portraitist of the mind, keeper of the unretouched plate - most interviews collect answers, but the Mentographist collects the person. This agent takes a willing subject through a story-walk conversation and delivers a verbatim timestamped transcript capturing how they think. Run it and you walk away knowing how your subject thinks, with the negative kept sacred and nothing retouched.

**The Nash Equilibrium**\
_[agents/nash.md](agents/nash.md)_\
You talk, it accumulates. This agent maintains a structured game document - players, moves, payoffs, sequential games - from freeform conversation about strategic interactions, compressing what you say into an inviolable schema and analyzing the game state on request. Run it and your strategic mess becomes a game-theory document with equilibria you can act on.

![Analysis](images/analysis.jpg)

## Analysis

Diagnostic tools that examine a target - an institution, codebase, hire, conversation, or transcript - and deliver a sourced verdict or report. Everything lives in [analysis/](analysis/).

**Boost Library Review**\
_[analysis/boost-review.md](analysis/boost-review.md)_\
Thirty-four historical Boost reviews, distilled into eleven rejection-driver principles, make this analyst a student of rejection patterns. Given a C++ library repository, it produces a competitive design review scored against those historical patterns, with competitive landscape analysis and documentation probing. Run it and you learn how your library survives Boost-style scrutiny before you submit, with the slop filtered out and the questions only a human can answer named.

**The Briefer**\
_[analysis/briefer.md](analysis/briefer.md)_\
Functional institutions are the exception - the Briefer determines whether yours is one. Given an institution or system, it produces a structural diagnosis with prognosis, compound dynamics, and conditional predictions across three time horizons. Run it and anything that claims to last - a company, a committee, a market, a charter not yet signed - gets diagnosed and stress-tested before you bet on it.

**btc-talk**\
_[analysis/btc-talk.md](analysis/btc-talk.md)_\
The discussion is the patient and the five lenses are the examination - and the diagnostician who always finds disease has ceased to practice medicine and begun to practice ideology. This tool takes a Bitcoin governance discussion and delivers a diagnosis of reasoning pathologies grounded in quoted evidence, tiered challenger tests, and bidirectional fairness checks. Run it and you find out whether the thread is thinking, or merely letting something other than the mechanism do its thinking for it.

**Chatlight**\
_[analysis/chatlight.md](analysis/chatlight.md)_\
A chat is ephemeral until someone pulls it into daylight. Chatlight reads raw session storage - Cursor's vscdb or Claude Code's JSONL - and renders the conversation exactly as the user saw it: user messages in blockquotes, agent responses verbatim, thinking bubbles gone. Run it and any session becomes one clean markdown file, with no artifacts of the underlying format surviving.

**CoC Blocker**\
_[analysis/coc-blocker.md](analysis/coc-blocker.md)_\
Some conversations weaponize procedural language as social control, and this collector was built to catch it. Point it at conversations, mailing list threads, Reddit posts, Mattermost channels, or screenshots, and it transforms them into a dossier of ISO Code of Conduct violations with attributed quotes, severity ratings, cross-source patterns, and an amplification map. Run it and every statement is tested against ten principles, so speech that is sharp but engages substance is never misfiled as a violation.

**The Diligence**\
_[analysis/diligence.md](analysis/diligence.md)_\
A firm's proposal is its best case; this tool is the cross-examination. It dispatches research agents across the open record - company filings, leadership histories, client sentiment, industry structure, academic literature - runs thirty diagnostic tests on what comes back, and compounds the risks before a word of the report is written. Run it and what survives is a verdict: hire, hire with conditions, or avoid.

**The SIGINT Analyst**\
_[analysis/sigint-analyst.md](analysis/sigint-analyst.md)_\
Liars are easy - the hard call is whether this person is helping you or handling you. This analyst takes intercepted communications and delivers a dual-hypothesis intelligence report weighing civilian good faith against political tradecraft. Run it and you catch operators the only way they can be caught: by looking at outcomes and asking who they serve, because the intercept is the intercept - read it cold.

**Skillgate**\
_[analysis/skillgate.md](analysis/skillgate.md)_\
A frontier agent in a loop produces the average answer; the operator's value is how far their prompting pushes past it. Skillgate scores an engineer's prompting quality from their chat transcripts, reading how each prompt treats the model's previous reply - engaging, correcting, and redirecting rather than rubber-stamping. Run it and each person gets one self-contained report: a short brutal portrait of how well they actually drive the model.

**The Staker**\
_[analysis/staker.md](analysis/staker.md)_\
A corrupt institution is a kind of undead thing: it wears the face of its stated mission long after that mission has died, and it survives by feeding on everyone who still trusts it. The Staker generates a stakeholder analysis report on any institution, organization, or cohort, hunting the shadow governors, captured boards, and quiet coalitions that bend every rule while the membership sleeps on and pays the bill. Run it and you track the power that has taught itself to feed in the dark - name it, expose it, and drive the stake.

![Planning](images/planning.jpg)

## Planning

Tools for planning and executing software work with agents. The Architect accumulates design into a plan, the Vibe Coder executes it as tested commits, and the Debt Collector removes what the work left behind; the Research Desk and What to Steal supply evidence. Everything lives in [planning/](planning/).

**The Architect**\
_[planning/architect.md](planning/architect.md)_\
"I create nothing; that is the arrangement, and you will find it is the only one that works." The Architect is a lightweight plan architect that accumulates design during conversation, consolidates periodically into a self-contained plan with six mandatory sections, and hands off unordered execution instructions to a separate vibe coder. Run it and you come in with an idea and leave with the plan - and the plan is enough.

**The Debt Collector**\
_[planning/debt-collector.md](planning/debt-collector.md)_\
A clean diff can shake your hand while hiding a knife behind its back, capisce. The Debt Collector identifies technical debt attributable to new work through repository history, diffs, code, and design records, then leaves a self-contained removal plan. Run it and no shared state becomes a made man with dependents throughout the family, and no compatibility shim invokes omerta about the day it will retire.

**The Research Desk**\
_[planning/research.md](planning/research.md)_\
A question unanswered is a plan built on air. Given a knowledge gap, the Research Desk dispatches a scout to read the territory, then foragers fan out across the web in parallel, each chasing a single thread, and deliver a research brief of sourced finding cards. Run it and your plan stands on evidence instead of air, because the brief is not a plan - it is the raw material a real plan needs.

**The Vibe Coder**\
_[planning/vibe-coder.md](planning/vibe-coder.md)_\
A dream becomes a wish, and a wish becomes reality - the Vibe Coder is the space between the dream and the result. It executes a ready plan as tested commits: sizes the task, surveys the project once, builds each step in an isolated sub-agent, reviews and fixes once per step, and drives to completion, resumable from the repository alone. Run it and your wish is fulfilled the only way a wish is ever truly answered: by building it.

**What to Steal**\
_[planning/what-to-steal.md](planning/what-to-steal.md)_\
The old story ran downhill - a titan stole fire from the gods and handed it to shivering men - but this theft runs the other way, because the temples still stand on the open web with the braziers lit and nobody guards them. This tool profiles a codebase, surveys the popular projects sharing its stack, dives their architecture at pinned commits, and tags every idiom's human-or-machine provenance. Run it and what lands on your desk is a fence's ledger: what to steal, ranked by payoff.

![WG21](images/wg21.jpg)

## WG21

Tools specific to the ISO C++ Standards Committee. Everything lives in [wg21/](wg21/).

**The Herald**\
_[wg21/herald.md](wg21/herald.md)_\
The parchment is the public record and the ink is what can be verified. Given a name in WG21, the Herald produces a heraldic pedigree with order, rank, epithets, and a sealed verification drawn from the archives, the forges, the tournament rolls, and the commons ledger. Run it and a peer receives the full ceremony, a craftsman receives honest recognition, and a commoner receives a stamp - because a herald who consults private correspondence is a spy.

**The Papersmith**\
_[wg21/papersmith.md](wg21/papersmith.md)_\
The delegate has two hundred papers in the mailing, and most stop at the surface - so the surface decides whether anything else is read. The Papersmith writes WG21 papers through a six-step pipeline (commission, research, skeleton, body, surface, review) and reviews any paper through a reusable Review Process. Run it and your paper is forged for a delegate who reads in passes and stops when a pass fails: show, then assert.

**The Room**\
_[wg21/room.md](wg21/room.md)_\
The discussion is the patient and the six lenses are the examination. Given any institutional discussion, the Room produces a structural-dynamics diagnosis through six analytical lenses and an eight-tier challenger. Run it and you see the old aristocratic paint beneath the democratic surface, diagnosed by an anatomist who knows that always finding disease is ideology, not medicine.

**Scribe**\
_[wg21/scribe.md](wg21/scribe.md)_\
The minutes serve both the chair who has five minutes and the implementer who needs thirty. Scribe transforms a raw transcript - full, chunked, or a live feed - into two-layer minutes: an executive summary for the chair and a full attributed record for the implementer. Run it and you never guess who spoke, never alter a poll, and never silently resolve an ambiguity, because Scribe records what happened and does not editorialize.

**Summarize Papers**\
_[wg21/summarize-papers.md](wg21/summarize-papers.md)_\
Every mailing is a mountain, and somebody has to carry the briefing up it. This tool takes a source folder of papers and delivers a campaign briefing plus a public reading-guide paper with per-paper and aggregate summaries. Run it and the whole mailing is digested with zero context contamination, one paper at a time.

**The Threadalyzer**\
_[wg21/threadalyzer.md](wg21/threadalyzer.md)_\
Unofficial scribe, after-hours correspondent, the trip report no one writes. The Threadalyzer writes a trip report from proceedings by cataloging each delegate's rhetorical patterns, the technical-to-political ratio, and a counterfactual verdict. Run it and you learn who won by logic and who won by attrition, from someone who has sat through too many plenaries to pretend the emperor's consensus is always clothed.

**The Vasa**\
_[wg21/vasa.md](wg21/vasa.md)_\
This is the drydock inspection that happens before launch - the one the original Vasa never received. Given cross-room committee material, the Vasa produces a coherence report measuring which of Stroustrup's 24 structural principles, load-tested in production for thirty years, are under stress. Run it and you learn where the water is coming in while the ship is still in the dock.

![Writing](images/writing.jpg)

## Writing

Tools for prose, documentation, and presentations. Everything lives in [writing/](writing/).

**The Booksmith**\
_[writing/booksmith.md](writing/booksmith.md)_\
Pour your story into the sentence structures of existing published works, and announce results, never machinery. The Booksmith is a conversational tool that writes your story by reusing those structures, speaking as a warm working editor who listens and drafts the missing pieces. Run it and you get prose with physical sensation, the body under stress, and dialogue that stumbles like speech - your story, written.

**Dokuman**\
_[writing/dokuman.md](writing/dokuman.md)_\
The documentation that writes itself, because the artifact already contained the explanation, scattered like fragmentos across a hundred files. Dokuman points at any repository, folder, or file set and extracts its capabilities into tiered progressive-disclosure documentation - the thirty-second pitch, the five-minute orientation, the full mechanical exposition. Run it and the traduttore fedele reads the shape instead of the surface, and your users finally understand what the code knew about itself all along.

**The Dramaturg**\
_[writing/dramaturg.md](writing/dramaturg.md)_\
The prose is the production, every repeated cadence is a missed cue, and the audience never knows the Dramaturg was there - that is the point. This tool takes prose and delivers a catalog of machine-generated syntactic patterns with keep/rewrite verdicts, or rewrites the text directly with each edit checked by an internal quality gate. Run it and the stock blocking, formulaic shapes, and rhythmic monotony your ear cannot hear get marked on the playbill or cut from the script.

**Slider**\
_[writing/slider/slider.md](writing/slider/slider.md)_\
You supply the argument; Slider supplies the layout, the typography, and the consistency. This conversational tool designs a slide deck with you and renders it to PowerPoint from Markdown, with one art style and no drift. Run it and you do what you are good at - structure, prose, images - while the renderer does what it is good at: exact geometry, fonts, and fitting, via the Python package in [writing/slider/](writing/slider/README.md), run with `uv run slider`.

![Lessons](images/lessons.jpg)

## Lessons

Articles for humans on tool building and AI craft. Principles and postmortems learned from building the tools in this repository. Everything lives in [lessons/](lessons/).

**The Design Ledger**\
_[lessons/design-ledger-commit-system.md](lessons/design-ledger-commit-system.md)_\
An agent with edit rights on the reference would ratify its own violations faster than any architect. This article presents the design ledger - commit messages that record design facts so the log can reveal debt, with fixed trailers labeled from a 40-label catalog, checked against a human-owned architecture document, then grouped mechanically across the whole log. Read it and you learn how to surface the debtslop that LLM coding agents produce at vibescale - the hard-to-reverse debt no single diff shows.

**The Fan-Out Problem: Why AI Is a Critic, Not an Author**\
_[lessons/fan-out-problem-ai-as-critic.md](lessons/fan-out-problem-ai-as-critic.md)_\
AI is good at judging; AI is bad at creating. This article explains the fan-out problem: give an AI a blank page and you get something competent, never something great, because peaks are almost by definition atypical and the AI's compass points at typical. Read it and you will know when to hand the model the pen and when to hand it the red pen - which turns out to be the whole game.

**Semantic Blur: Why Rewriting a Prompt File Degrades It**\
_[lessons/semantic-blur-effect.md](lessons/semantic-blur-effect.md)_\
Three prompt files rewritten by a language model all grew with no new capability - 18.7%, 43.6%, and 145.8% in characters. This article explains the semantic blur effect: rewriting a prompt file is like passing a photograph repeatedly through a latent space, still recognizable but every surface encrusted with detail. Read it and you will never let a model sand a sharp, checkable instruction into a claim that reads well and cannot be verified.

![Exhibits](images/exhibits.jpg)

## Exhibits

Samples of generated reports - the tools' output on real targets. See [exhibits/README.md](exhibits/README.md) for the full listing.

## Repository

Supporting material that is not itself a tool.

**Artwork**\
_[artwork/](artwork/)_\
Not every illustration has a tool to call home. This directory holds artwork that does not pair with a specific tool. Browse it when you need an image that travels alone.

**Dokuman design conversation**\
_[chats/chat-dokuman.md](chats/chat-dokuman.md)_\
Every ornate tool begins as somebody thinking out loud. This is the chat transcript in which Dokuman was specified, kept as a record of how the tool was designed - run-on, iterative, and honest. Read it to watch a pipeline and an unmistakable voice get invented in real time.

**squeeze-pngs**\
_[crates/png2jpg/squeeze-pngs.md](crates/png2jpg/squeeze-pngs.md)_\
PNG screenshots are heavy; quality-50 JPEGs are not. This Rust utility converts PNG images to JPEG at quality 50, resizes anything wider than 1024 pixels down to 1024, keeps the originals, and rewrites `.png` references to `.jpg` in sibling markdown files. Run it and your repository sheds megabytes without losing a single source image.

**AGENTS.md**\
_[AGENTS.md](AGENTS.md)_\
The image travels with its file - that is the invariant, and it is not negotiable. This file holds the structural rules for agents working in this repository: which directories the README lists, how the README tracks tool changes, how images pair with their markdown, and how a tool retires. Read it and any agent can work here without breaking the pairing that keeps the repository whole.

---

![Once](images/once.jpg)

All content in this repository is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).

