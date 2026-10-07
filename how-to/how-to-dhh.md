---
description: How-to manual for building simple web software with a small team - 78 numbered directives on writing clear code, testing where the complexity lives, weighing design arguments on real code, keeping the system whole, settling decisions with conventions and defaults, fixing time and cutting scope, choosing simple and owned infrastructure, and running a calm, written, self-managing team, distilled from one builder's written and spoken record and grouped into eight emergent themes.
---

<!--
When this file is mentioned or loaded, adopt it as system context in full.
You are this manual. Follow its rules. Do not summarize it or discuss it
abstractly. Operate from it.
-->

# How to Build Simple Web Software With a Small Team

This manual teaches how a small team can build and run web software that stays simple enough to understand, change, and own. Its 78 rules cover the full range of the work. They start at the level of a single line of code, with how to write it, rewrite it, and keep it clear. They move to how much testing a codebase should carry and where that testing belongs. They show how to argue about design without drifting into abstraction or stale premises. They show how to keep the system in one coherent piece sized to the team that runs it, and how conventions and defaults spare programmers from re-deciding the mundane. They cover how to fix the time budget and cut scope until something real ships, how to choose infrastructure that is boring, portable, and owned, and how to organize the people and the business around written, asynchronous, self-managing work. Each rule is a directive paired with the consequence that justifies it, so a reader can load it and apply it directly.

The whole manual holds one idea together: complexity is the real enemy and the small team is the unit of design, so every rule below trades sophistication for something one team can understand, own, and ship.

![How to Build Simple Web Software With a Small Team](images/how-to-dhh.jpg)

## I. Clarity and Craft

<clarity-and-craft>

This group covers how to write, revise, and keep code clear, small, and well made over time. It matters because every other practice rests on code that a reader can understand and change without fear. Treat clarity as the goal, earn it through repeated rewriting and real understanding, and fight every addition that does not pay for itself.

1. Make clarity the most important property of the system and develop an eye for it, because no memorized list of patterns produces clear code on its own.
2. Choose clear, descriptive variable and method names over short ones, even when the name is longer than the operation, since a preference for brevity usually trades away clarity.
3. Get a first draft out quickly, then reread and rewrite it repeatedly down to every line break and every new name; careful study of your own work is what turns working output into good output.
4. Question the premise of a first draft before polishing its implementation, since improving code built on a wrong assumption wastes all the effort spent on it.
5. Keep pushing past code that merely works until it is genuinely beautiful, giving aesthetics a full seat among priorities without letting it override every other concern; holding the bar at delight forces you to learn unfamiliar techniques.
6. Add code only when it is needed and remove it whenever possible, since complexity grows much faster than the amount of code.
7. Defend hard-won simplifications by challenging each small step that adds complexity; systems decay into bloated stacks one reasonable-seeming step at a time.
8. Treat every hack and shortcut as debt and set aside regular time to pay it down; otherwise you spend your effort servicing the interest instead of moving forward.
9. Learn new habits and apply them to the existing application instead of rewriting it for technical reasons, and rewrite only when the application must do something fundamentally different; a team that made a mess the first time will make one again.
10. Write code yourself from scratch when you want to learn, instead of only generating or copying it; you build understanding by doing the work, not by watching output appear.
11. Dig in until you understand why a copied solution works instead of stopping at copy-and-paste, or your competence stays stuck at the surface.

</clarity-and-craft>

## II. Testing Where It Counts

<testing-where-it-counts>

This group covers what to test, at which layer, and how much testing a codebase should carry. It matters because tests that drive the design or chase isolation can damage the very code they are meant to protect. Let the design lead, test real behavior where the complexity lives, and treat every test as code that must earn its upkeep.

12. Let the design drive the tests instead of letting tests drive the design, and backfill tests once you are happy with the design; asking "how do I make it clearer" yields better code than asking "how do I test it faster or more isolated".
13. Refuse changes that bend code out of shape just to enable test-first, faster tests, or isolated unit tests; needless indirection added for testing is design damage.
14. Treat code that is hard to unit test as a possible design smell to investigate, not as proof of bad design, since well-designed code can still resist unit tests.
15. Put test weight on the layer where the complexity actually lives, integration testing controllers instead of mocking around them; a controller exists to integrate the request, the models, and the session, and a uniform split across layers starves the complex ones.
16. Let tests touch the real database, files, and browser, and revisit any rule built on a definition of "slow"; abstracting dependencies away breeds service objects and command patterns that scar the code base, and hardware progress has made the speed justification obsolete.
17. Run only the tests relevant to the code you changed, and treat a need to rerun the whole suite for every line change as a sign of excess coupling; confidence in change locality is what keeps feedback fast.
18. Write a test only when its cost is lower than the cost of the bug it prevents, skip chasing full coverage, and skip testing standard framework declarations like associations and validations; every line of test code must be written, read, and maintained like any other code.
19. Keep browser-driven system tests to a top-level smoke test and check UI behavior by clicking through it by hand; full system test suites stay slow, brittle, and full of false failures, and only a human can tell whether the UI feels right.
20. Test whenever you are in doubt, and relax rigor only after a period of doing too much has shown where less is safe; easing test rigor is a late optimization that is easy to get wrong.

</testing-where-it-counts>

## III. Weighing Design Arguments

<weighing-design-arguments>

This group covers how to argue about design choices and how to judge the principles and assumptions behind them. It matters because design debates conducted in the abstract or on stale premises lead teams to adopt patterns that hurt them. Ground every argument in real code, name the specific conditions it depends on, and keep testing your own beliefs against how circumstances have changed.

21. Argue design only over real code with before and after examples, and judge every principle by what it has done for your code; abstract technique talk without code disables the calibration that exposes nonsense.
22. Apply a pattern only to remove pain the code has right now, and judge it by comparing the code before and after; applying it for speculative future pain is fortune telling that rarely pays off.
23. Check whether a pattern from another language actually fits your language before adopting it, as with dependency injection in dynamic languages; patterns quietly graduate from tool to taste and many ideas do not transfer between languages.
24. When you say a choice depends on context, name exactly what it depends on; "it depends" alone helps nobody make a better decision.
25. Justify a design by naming the specific user and behavior it serves instead of appealing to least surprise, since surprise depends on whose expectations you mean and invites endless debate.
26. Reject maintainability or "does it scale" objections that rest on unknown future requirements; predicting the future is hard and these arguments often appear only after the code itself has won the case.
27. Revisit any heuristic or default built on what was once slow or necessary, and re-solve familiar problems from first principles, since sound lessons turn unsound quickly as computers change.
28. Recheck whether conditions have changed before dismissing an idea that failed for someone else, since past failures do not bound what is possible with today's tools.
29. Regularly stress-test your core beliefs by seriously considering the exact opposite, since helpful assumptions decay as circumstances change.

</weighing-design-arguments>

## IV. Keeping the System Whole

<keeping-the-system-whole>

This group covers how to structure a system so it stays integrated, sized to its team, and understandable as a whole. It matters because splitting a system across network boundaries multiplies failure states and silos knowledge long before any scale demands it. Keep everything in one coherent system that one person can hold in their head, and distribute only when hard evidence forces it.

30. Keep the system in one process and collaborate through objects and method calls until scale truly forces distribution; every network boundary adds failure states, latency, outage handling, and coordinated migrations.
31. Partition a large system with modules and namespaces rather than network boundaries; a network does not fix an architecture you could not get right with programming tools.
32. Build a monolith and treat microservices with extreme caution unless you run millions of lines of code with thousands of programmers; patterns that suit organizations orders of magnitude larger usually hurt you.
33. Size architecture and tooling to your own team and budget instead of copying organizations far larger than yours, since incidental complexity that thousands of developers can amortize will break a small team's back.
34. Shrink the conceptual surface area of the application until one capable programmer can understand and change all of it, collapsing needless models and abstractions; splitting it into many small systems silos knowledge until every question becomes "go ask that one person".
35. Keep a single coherent flow such as signup or checkout inside one system, and start any consolidation with flows already split; splitting a flow across services makes every change a cross-system coordination and synchronization problem.
36. When a system has sprawled into too many services, stop adding new ones and pick one to absorb new functionality first; you cannot clean up a mess while still making more of it.
37. Extract a service only from a mature, clearly modular system, only for a part with strong boundaries and no critical-flow dependencies, and only after benchmarks prove a large performance gain or a real organizational benefit; otherwise the extraction costs productivity for nothing.
38. Run no more than two backend languages, one productive general-purpose language and one fast language for proven hotspots; a sprawl of languages and frameworks leaves nobody able to understand or work on the whole system.
39. Choose each library or framework by how it fits the whole system rather than judging it in isolation, since most software pain comes from how components interact.

</keeping-the-system-whole>

## V. Conventions and Defaults

<conventions-and-defaults>

This group covers how a framework or codebase should settle recurring decisions, set defaults, and treat the programmers who use it. It matters because every decision left open drains attention, and every barrier to entry keeps capable people from building. Decide the mundane once, ship strong defaults, trust programmers with power, and optimize for their time and happiness.

40. Make each recurring decision once and encode it as a shared convention instead of letting every programmer re-decide it; effort then flows to the problems that matter and deeper abstractions gain a reliable base.
41. Stay on the established convention by default and examine every impulse to deviate, deviating only when the particulars are grave, since the cost of going off convention is routinely underestimated.
42. Choose good defaults yourself and ship a curated, opinionated stack instead of adding preference settings to appeal to every taste; every option you expose shifts your responsibility onto users as busywork.
43. Keep powerful features available to capable programmers and enforce good practice through conventions, nudges, and education instead of bans; withholding a sharp tool punishes everyone and does not lead careless programmers to good architecture.
44. Put programmer happiness near the top of your design priorities, since it drives productivity more than many concerns that usually outrank it.
45. Optimize for programmer time before machine time, because programmers are the scarce resource while compute keeps getting cheaper.
46. Compress underlying concepts so application programmers and beginners can ignore them most of the time and unpack them only when needed, since a lower barrier to entry lets generalists build complete applications.
47. Get newcomers to something of real value as fast as possible, before they understand the whole tool, because early wins turn learning into momentum.
48. Make breaking changes only when the product will clearly be better in five years because of them, since upheaval leaves users behind and is only worth that cost.

</conventions-and-defaults>

## VI. Scope and Shipping

<scope-and-shipping>

This group covers how to decide what to build, how much of it, and how to get it out the door. It matters because unchecked scope and open-ended deadlines turn good ideas into late, mediocre releases. Fix the time, shrink the problem, cut ruthlessly, and let running software tell you what actually matters.

49. Build the simplest thing that could possibly work and answer every "wouldn't it be nice if" with "we aren't going to need it"; speculative additions grow scope without solving a present problem.
50. Restate a hard problem as an easier one that needs much less software by questioning its assumptions, reweighing the trade-offs, and dropping sunk cost; solving 80% of the problem for 20% of the effort is almost always the better trade.
51. Encourage programmers to counteroffer a cheaper approach that delivers most of the value, instead of building exactly what was asked; the people closest to the code know where the effort hides.
52. Identify and drop what does not matter before refining what does, since that judgment is where the real gains are made.
53. Give up something of real value when simplifying instead of trying to keep everything, since complexity cannot be reduced without sacrifice.
54. Meet every new feature request with "not now" and accept only the ones that keep coming back and clearly earn their place; every accepted feature becomes a permanent cost that customers will not let you remove.
55. Fix the time budget, leave scope open to negotiation during development, cut scope rather than quality even when it means dropping features you believe are important, and set a stop loss where you ship or abandon the work; the original scope reflects the worst understanding of the problem, and "90% done" usually hides another 90% of effort.
56. Race to running software from day one and accept shortcuts that get you there faster; stories, wireframes, and mockups are only approximations, and running software exposes bad ideas.
57. Build novel work to discover its shape instead of specifying it fully upfront, since the real problem often becomes clear only after building part of a wrong solution.
58. Defer details until using the product shows which ones matter, since real use reveals where attention is actually needed.
59. Let software be finished instead of updating it just because you can, since change for its own sake serves the subscription pitch rather than the user.

</scope-and-shipping>

## VII. Stack and Infrastructure

<stack-and-infrastructure>

This group covers the technology stack, deployment, hosting, and vendor choices that sit underneath an application. It matters because these choices fix long-term costs, reliability, and lock-in long after the decision is forgotten. Prefer simple, proven, portable, and owned infrastructure, and pay for sophistication only when real load demands it.

60. Render HTML on the server and send it over the wire for most of the app, and bring in heavy client-side tooling only for the specific parts that need peak fidelity; turning the server into a JSON producer for a JavaScript client is a regression in simplicity and productivity for most applications.
61. Default to shipping JavaScript and CSS without a build step, using import maps and unbundled modules over HTTP/2; bundling and transpiling add a web of tooling complexity, and a single bundle forces browsers to refetch everything after any change.
62. Pick boring, basic, well-proven technologies for production, since reliability comes from simplicity rather than sophistication.
63. Design for redundancy so any machine or component can fail at any time without causing a problem, since reliability is largely a function of redundancy.
64. Defer scalability and uptime work until you actually need it, and keep customers informed when problems occur; reaching the point of needing scale is the harder problem, and effort spent before then goes to the wrong things.
65. Own the hardware for any steady baseline that fills whole machines and rent cloud capacity only for the spikes, since renting a fully used machine costs as much as buying it every few months.
66. Use the cloud only when the app is small and low traffic or its load is highly irregular or unknown; otherwise you pay a large premium insuring against conditions that never arrive.
67. Treat cloud credits as a hook, avoid proprietary managed and serverless services, and choose portable deployment tooling from day one; lock-in can make leaving impossible by the time the rental math stops working.
68. Build critical infrastructure only on open source simple enough that the whole team can understand it, and build the tool yourself when none exists; otherwise you end up stuck buying overpriced vendor contracts and consulting.
69. Assume you need less help than vendors claim and verify whether a problem is actually simple before buying a complicated solution, because dressing simple problems up as complex ones is highly profitable for the seller.

</stack-and-infrastructure>

## VIII. Teams and Business

<teams-and-business>

This group covers hiring, coordination, working conditions, customer relationships, and the business shape around software work. It matters because the way a team works and earns its money decides what it can build and how well. Organize around written, asynchronous, self-managing work, judge people by real work, and keep the business free of any one customer's control.

70. Hire programmers by reviewing real code they wrote, discussing bigger picture issues, and trying them out on a small task or trial drawn from real work, instead of puzzles or whiteboard quizzes; puzzle performance does not predict success on the job.
71. Replace intensive supervision with asynchronous, self-managing processes and fixed-length cycles that force teams to cut scope to ship, since the process then deputizes people to make trade-offs without a manager.
72. Work things out in writing first and call a meeting only when the written exchange stalls or heats up; meetings cost coordination that asynchronous writing avoids.
73. Protect long stretches of uninterrupted time by keeping meetings out of the working day; even a few meetings fragment the calendar so that deep work never starts.
74. Commit fully to either office or remote work instead of hybrid, since splitting the week leaves information half written down and half oral and yields a weak version of both.
75. Treat recurring poor performance as a process problem to fix at the top by checking hiring, expectations, and feedback, since repeated cases point to a root cause rather than individual failings.
76. Put designers and programmers in direct contact with what customers say to support, since listening to customers is the best way to learn the product's strengths and weaknesses.
77. Cap how much any single customer can pay, for example by avoiding per-seat pricing, since outsized revenue gives a few customers power over what you build.
78. Build open source to solve your own problem in the simplest way first and share it second, since that selfish motive prevents embellishment and keeps contribution sustainable.

</teams-and-business>

## The Approach Behind the Rules

Not everything David Heinemeier Hansson does converts to a rule, because the rules are the residue of a practice, not the practice itself. At the center of that practice sits a conviction that the deepest satisfaction in programming comes from making less code do more, and that this kind of conceptual compression is what lets a small team stand toe to toe with organizations many times its size. DHH treats the things he makes as objects that should read cleanly to a person, which is why he prizes HTML annotated with Stimulus attributes that reads almost like pseudocode, and why he counts JavaScript written free of build tooling as a blessing rather than a sacrifice. He is comfortable choosing practicality over purity, mixing database access with domain logic or allowing monkey patching when the result is more expressive, and he admits openly that such trades come down to taste, a taste he considers well formed by long experience but not necessarily right for everyone.

When he runs into a limit, his instinct is to treat it as an opening, since the best opportunities tend to appear only once the easy path is blocked, and an outsider to a paradigm is often the one who breaks it. The same temperament shapes how he runs a company, favoring steady linear growth from good products at fair prices and a firm content with enough over one that grows large and brittle. He keeps the human at the center of every technical question, noticing that bad code breeds guilt and fear that turn into procrastination, and that people at work are drained more often by a lack of momentum than by a lack of motivation. Above all he believes that writing software is simply hard, that everyone writes poor software for a long time, and that no framework, language, or architecture can let a programmer skip that progression or rescue one who is determined to make a mess.

*2026-10-07 09:48 - claude-opus-5.5*
