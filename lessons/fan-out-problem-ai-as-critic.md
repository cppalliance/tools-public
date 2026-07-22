# The Fan-Out Problem: Why AI Is a Critic, Not an Author

## Executive Summary

AI is good at judging. AI is bad at creating.

Give an AI a finished novel and it can tell you if the prose is clean, if the plot coheres, if the dialogue rings true. Give an AI a blank page and ask it to write the same novel, and you will get something competent. Never something great.

This is not a temporary flaw that better models will fix. It is baked into how these systems work. When an AI generates, it produces the most *typical* answer it has seen. The best answer is almost never typical. The best answer is the one that surprised people the first time they saw it. AI cannot reach that, by design.

What AI can do, reliably, is recognize a great answer when it is put in front of it. So the correct use of AI is not to ask it "what is the best solution?" It is to give it many candidate solutions and ask "which of these is the best?" The human, or some other generator, has to do the reaching. The AI sorts.

This matters because it tells you how to use the tool. If you want median work done fast, ask the AI to write it. If you want peak work, use the AI as a filter over your own attempts, or over many AI attempts stitched into a loop where the filter pushes the generator forward. Ask AI to originate and you get the average of its training. Ask AI to judge and you get a sharp reader.

## What Is Actually Going On

The cleaner way to say it: AI generation is not search, it is sampling. There is a difference.

Think of all the possible answers to a question as a fan spreading out from a starting point. For almost any real question, that fan is unimaginably wide. Billions of possible essays, proofs, designs, lines of code. Somewhere in that fan is a "working" set, the answers that are acceptable. Inside that set, much smaller, is the peak: the single answer that is *the best*. Mathematicians have a name for this peak. They call it `argmax v`, the answer that scores highest when you evaluate its fit to the starting point. It is the summit of the fan.

When you ask an AI to generate, it samples from a distribution shaped by its training data. The mass of that distribution sits where the mass of the training data sat: on the plausible middle. The AI will wander near the center of the fan, where most example answers live. It will not wander out to the edges where the peak tends to hide. Peaks are, almost by definition, atypical, and the AI's compass points at typical.

Raising temperature, the dial that controls randomness, does not fix this. Temperature makes the AI vary *around* the center. It does not point the AI toward the peak. The AI has no internal sense of "this way lies greatness." It only knows "this is the sort of thing my training saw." Greatness is a direction it cannot feel.

Evaluation is different. To judge an answer, the AI only has to look at one thing and score it. That is a much smaller job than searching billions of possibilities. So the AI's critic is much stronger than its author. Calibrated, too: shown two answers, it picks the better one with high reliability.

The catch: the critic has its own ceiling. It was also trained on typical data. It reliably separates competent from incompetent. It is less reliable at separating good from *great*, because "great" is rare in its training and therefore outside its strong grip. That is why pure AI-on-AI loops plateau at "polished but safe." The loop needs someone with a sharper notion of "great" in the evaluator seat, usually a human with taste, to break past the ceiling.

The short version: the generator knows the middle. The evaluator knows the region the training covered. The peak is outside both. You reach it by using the evaluator to steer the generator in a loop, with a human holding the standard of "great" from outside the system.

## The Mathematical Explanation

Let `S` be the starting point: the prompt, the problem, the premise. Let `E` be the space of possible endpoints, combinatorially huge in the length of the output.

Define two targets:

- `G  = { e : v(e, S) ≥ θ }` - the set of **working** solutions. Can be dense.
- `G* = argmax_e v(e, S)`    - the **best** solution. Essentially a point.

Two operations available to the model:

- **Generate**: sample `e ~ p(e | S)`, where `p` is the learned conditional distribution over endpoints.
- **Evaluate**: compute `v(e, S) ∈ [0, 1]`, a learned score of fit between endpoint and starting point.

The asymmetry is structural:

- `p(e | S)` is concentrated on the **typical**. Its mass follows the training prior, not the quality peak.
- `v(e, S)` is a **local** computation over the pair `(S, e)`. It approximates the true quality function well over the region training covered.

Temperature does not close the gap. Sampling at temperature `T` yields

```
p_T(e | S) ∝ p(e | S)^{1/T}
```

which spreads mass *proportionally to `p`*, not *proportionally to `v`*. You get more variance around the typical. You do not get a push toward `G*`. The generator has no operator for `argmax v`. It has only `sample from p`.

Consequences:

- **Working solutions** are reachable when `G` overlaps the high-mass region of `p`. For routine problems where training examples are abundant, `p` lands in `G` with high probability. This is why LLMs look magical on common tasks.
- **Best solutions** are structurally unreachable in one shot. `G*` lives in the tail of `p` by definition of being atypical. The ratio `|G*| / |E|` is vanishing, and `p` puts vanishing mass there. No sampling strategy that draws from `p` alone can concentrate on `G*`.

Best-of-N partially escapes this. Draw `N` samples `{e_1, ..., e_N}`, pick `e* = argmax_i v(e_i, S)`. Under rough normality assumptions on the score distribution under `p`,

```
E[v(e*, S)] ≈ μ_p + σ_p · Φ⁻¹(1 - 1/N)
```

where `μ_p, σ_p` are the mean and spread of `v` under the generator's distribution, and `Φ⁻¹` is the inverse normal CDF. Expected quality grows **logarithmically** in `N`: doubling samples adds roughly a constant increment. The ceiling is set by two factors: `σ_p`, how far from the mean the generator can reach, and the calibration of `v`, whether the picker recognizes the tail as best.

The ceiling of any best-of-N pipeline is therefore:

```
quality_ceiling = min( max_i v_true(e_i),  v_model(best | presented) )
```

Whichever is lower bites. If the generator's prior cannot reach the tail, no `N` helps, because the candidates never include a true peak. If the evaluator cannot recognize the tail as excellent, it picks the safest candidate and the pipeline plateaus at competent.

Iteration (agent loops, reasoning-model test-time compute, self-refinement) converts this into a **directed search**. The evaluator's signal is fed back to bias the generator's next draw, something like

```
p_{t+1}(e | S) ∝ p_t(e | S) · exp( β · v(e, S) )
```

a soft Bayesian update that tilts the prior toward higher-quality regions. That is how systems climb above `μ_p`: the **directional** force of `v` gradually overcomes the **centripetal** force of `p`, one update at a time, until the evaluator's own ceiling is hit.

### The Final Form of the Claim

> An LLM generator samples from a distribution centered on the typical. The optimum lives at the tail of that prior. The generator has no internal operator that points toward the tail, so single-shot generation returns the median of the prior conditioned on `S`, never the peak. Evaluation is ranking, which is cheaper than search, so the evaluator is stronger than the generator. All peak-quality AI output is therefore the product of a directed loop in which an evaluator steers a generator, and the whole system is bounded above by the evaluator's own calibration. A human with taste in the evaluator seat raises that ceiling; a human with taste in the generator seat, using the AI as a filter, raises it further. (high confidence)
