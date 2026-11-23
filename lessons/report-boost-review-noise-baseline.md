# Expect False Alarms and Noise in Every Boost Review

*Policy brief for Boost review managers*

Review managers should expect some objections in every Boost review to be false alarms or preferences, however good the library is. A false alarm is an objection to something that is not a defect. A preference is an objection about naming or style where either choice works. Noise is the spread between judges of the same case (Kahneman, Sibony and Sunstein, *Noise*, 2021). The ask is to weigh each objection on its evidence, not on its tone or on the fact that someone raised it. Three research findings support the ask. Between 22% and 65% of the issues reviewers raised were false alarms. Two committees reviewing the same papers each rejected about half of what the other accepted. Readers rated negative reviewers as more intelligent than positive ones, and people who want to stand out turn more critical. Nobody is a villain here. This is ordinary human judgment, and the review manager's job is to factor it out.

One limit applies throughout: no study has measured a Boost review or any library design review, so every number below transfers by analogy.

## Reviewers raise many objections that are not defects

Three peer-reviewed studies checked each raised issue afterward, and Table 1 gives what they found.

Table 1. What reviewers' raised issues turned out to be once each was checked.

| Study | What was reviewed | What the check found |
|---|---|---|
| [Porter et al. 1997](https://userweb.cs.txstate.edu/~rp31/papersSQ/PorterEtAl_TSE.pdf) | 88 inspections of production C++ code at Lucent | 22% false alarms, 60% readability or coding-standard changes only, 18% true defects |
| [Cockton and Woolrych 2001](https://doi.org/10.1007/978-1-4471-0353-0_11) | One drawing editor design, 99 analysts, checked against user tests | 65% of predicted problems were false |
| [Czerwonka et al. 2015](https://www.microsoft.com/en-us/research/wp-content/uploads/2015/05/PID3556473.pdf) | Code review comments at Microsoft | About 15% indicated a possible defect; authors found 33% useful when the reviewer was new to that code |

Porter's team traced most of the 60% to "conflicts between different reviewers about the coding style or conventions used". Before the inspection meeting, about half of the issues individual reviewers wrote down were false alarms.

A better library may not draw fewer objections. Levari et al. call this prevalence-induced concept change: when threatening faces became rare in lab experiments, people began calling neutral faces threatening, "even when participants were forewarned about it and even when they were instructed and paid to resist it" ([Levari et al. 2018](https://pubmed.ncbi.nlm.nih.gov/29954981/)).

## Reviewers of the same work disagree, and that is noise

Across 11 usability studies, the average agreement between any two evaluators of the same design ranged from 5% to 65% ([Hertzum and Jacobsen 2001](http://mortenhertzum.dk/publ/IJHCI2001.pdf)). Peer review shows the same pattern. When two NeurIPS 2021 committees reviewed the same 882 papers, each rejected about half (50.6%) of the papers the other accepted ([Beygelzimer et al. 2023](https://arxiv.org/abs/2306.03262)).

Insurance executives expected two underwriters pricing the same case to differ by about 10%, and the measured median difference was 55% (*Noise*, chapter 2). Managers, in other words, underestimate the spread. The practical reading is that one reviewer's lone objection is weak evidence of a defect, and the others' silence is weak evidence against one.

## Critics look smarter, and wanting to stand out draws objections

Audiences give critics extra credit for intelligence. Readers rated negative book reviewers as "more intelligent, competent, and expert than positive reviewers, even when the content of the positive review was independently judged as being of higher quality" ([Amabile 1983](https://www.hbs.edu/faculty/Pages/item.aspx?num=7402), "Brilliant but Cruel"). People who want that credit act on it: those told to appear smart "were more critical than either those wanting to be liked, or those in a no-goal control group" ([Gibson and Oberlander 2008](https://doi.org/10.1080/15298860701668986)).

Wanting to be different adds to the effect. Across 2.05 billion Reddit comments, threads grew more negative as they went on. In an experiment with 3,685 people, participants became more negative "only when incentivized to be unique" ([Mao et al. 2026](https://doi.org/10.1073/pnas.2527316123)). The authors' explanation is that negativity is the easier way to say something new.

These studies used book reviews, lab tasks, and social media, not technical review. They also measured criticism. The search for this brief found no solid evidence that disagreement alone earns credit for competence.

## Testing each objection beats counting or discounting them

A review manager has three options. Counting objections at face value costs nothing, but it imports false alarms and noise into the decision and rewards a critical tone. Discounting objections across the board fails the other way. In Porter's data 18% of raised issues were true defects, and the journal reviewers that editors rated highest "reported twice as many flaws" in a test manuscript ([Callaham et al. 1998](https://pubmed.ncbi.nlm.nih.gov/9676664/)). Low agreement can also mean that reviewers brought different use cases and each found something real.

The recommended option is to test each objection on its evidence. Ask the reviewer for the failing case, the measurement, or the use case the design cannot serve. Then sort the objection as a defect, a preference, or a false alarm. A naming objection is a defect only if someone can show users misreading the name. Weigh defects in the decision, pass preferences to the author as optional, and set false alarms aside with a one-line reason. This costs the manager time, and only this option separates evidence from false alarms and noise.

As a next step, the manager of the next review can count the objections in each class and publish the count with the result. After a few reviews, Boost will have its own measured false alarm rate.

## False alarms are almost certain, and their rate in Boost is unknown

A given Boost review will almost certainly contain false alarms and preferences. Confidence in that judgment is moderate: studies in several fields agree, but none measured a library design review. The rate in Boost is unknown. Measured false alarm rates elsewhere run from 22% to 65%, and Porter's 22% depends on what the code's author chose to change. Critics are likely to get the same extra credit on a review mailing list. Confidence in that is low, because the evidence comes from outside technical review.

*2026-11-23 06:15 - claude-sonnet-5.5*
