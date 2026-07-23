---
style: "Steampunk Victorian cityscape, warm gas lamp lighting, cobblestone streets, period clothing, golden atmospheric tones"
---

# What Belongs in the C++ Standard Library?
The question, the terms, and the evidence.

<!-- A steampunk Victorian cityscape at dusk with warm gas lamps, a grand
     arched building labeled "STANDARD", cobblestone streets with people in
     period clothing, golden sunset sky -->
![title](images/title-bg.png)

## THE QUESTION

Every proposal asks the same thing

<!-- A long queue of Victorian-era people waiting outside a grand vault door
     labeled "STANDARD", holding papers and packages, moody lighting -->
![question](images/question.png)

---

Should this component be added to the C++ standard library?

*Every paper. Every meeting. The same question.*

- This talk is about how to answer it.
- **The default answer matters most.**

## THE ANSWER

The default is **no**

---

The burden of overwhelming proof sits on the proposer. This paragraph is
deliberately long so that the auto-fit logic has something to chew on when it
estimates how much vertical space the right panel needs to hold everything.

*Not hostility. Arithmetic.*

### Why the default is no

- Every addition is permanent
- Every addition has a maintenance cost
- **The rest of this talk is the arithmetic.**

## EVIDENCE

Constructs on parade

---

Here is body text with `inline_code`, a [link to WG21](https://wg21.link),
plus ***bold italic*** and plain *italic* and **bold** spans.

> A blockquote becomes a callout box with an orange border. It is set in
> italics on a slightly lighter background.

A fenced code block:

```cpp
auto answer = should_add ? Decision::yes : Decision::no;
static_assert(answer == Decision::no);
```

Ordered steps:

1. State the proposal
2. Count the cost
3. Demand the proof

Nested bullets:

- Top-level point
  - Supporting sub-point
  - Another sub-point
- Back to top level

# Thank You
Questions, objections, and counterexamples welcome.
