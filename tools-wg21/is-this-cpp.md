# Tool: Is This C++?

Point this at any proposal, language, library, or blog post. Answer each question yes, no, or not applicable. Count the yeses as a fraction of applicable questions. Read the verdict.

Questions 1-20 and 22-24 come from Bjarne Stroustrup, *The Design and Evolution of C++* (Addison-Wesley, 1994). Question 21 comes from Howard Hinnant.

<img src="images/is-this-cpp.png" alt="Is This C++?" width="100%">

---

**1. Does the subject avoid imposing cost on programs that do not use it?**

> "What you don't use, you don't pay for (zero-overhead rule)." (S4.5)

**2. Is the subject affordable on ordinary hardware?**

> "Affordable on hardware common among developers." (S2.4)

**3. Does the subject leave no room for a lower-level language below it?**

> "Leave no room for a lower-level language below C++ (except assembler)." (S4.5)

**4. Does the subject preserve the static type system without implicit violations?**

> "You need to explicitly use a union, cast, array, an explicitly unchecked function argument, or explicitly unsafe C linkage to break the system." (S4.4)

**5. Are unsafe operations explicit and visible?**

> "I prefer to make semantically ugly operations, such as ill-behaved casts, syntactically ugly to match." (S4.4)

**6. Does the subject treat user-defined types as well as built-in types?**

> "User-defined and built-in types should behave the same relative to the language rules and receive the same degree of support from the language and its associated tools." (S2.4)

**7. Does the subject prefer compile-time checking over run-time checking?**

> "Wherever possible, checking is done at compile time." (S4.4)

**8. Does the subject refrain from forcing the programmer into a single style?**

> "Trying to seriously constrain programmers to do 'only what is right' is inherently wrongheaded and will fail." (S4.2)

**9. Does the subject allow useful features rather than preventing every misuse?**

> "It is more important to allow a useful feature than to prevent every misuse." (S4.3)

**10. Can the subject be combined with other programming styles?**

> "Many hybrid styles of programming must be supported." (S4.2)

**11. Is the subject driven by real problems, not theory alone?**

> "Theory itself is never sufficient justification for adding or removing a feature." (S4.2)

**12. Does the subject provide a transition path from existing practice?**

> "The general strategy is first to provide a better alternative, then recommend that people avoid the old feature or technique, and only years later - if at all - remove the offending feature." (S4.2)

**13. Is the subject useful now?**

> "C++ must be useful to someone with average skills, using an average computer." (S4.2)

**14. Can the subject be composed with separately developed parts?**

> "Anything that allows a component of a larger system to be developed independently and then used without modification in a larger system serves this purpose." (S4.3)

**15. Is the subject a language facility, not a complete system?**

> "C++ is a language, not a complete system." (S4.2)

**16. Does the subject prefer general mechanisms over built-in special-purpose features?**

> "Each time the decision has been to improve the abstraction mechanisms." (S2.1)

**17. Does the subject support deterministic resource management?**

> "I called this technique 'resource acquisition is initialization.'" (S16.5)

**18. Does the subject provide manual control when automation is insufficient?**

> "If in doubt, provide means for manual control." (S4.5)

**19. Can the programmer say what they mean in the language itself?**

> "To allow expression of all important things in the language itself rather than in the comments or through macro hackery." (S4.3)

**20. Do application concepts map directly to language constructs?**

> "The class concept allowed me to map my application concepts into the language constructs in a direct way that made my code more readable than I had seen in any other language." (S1.1)

**21. Does this make the safe thing easy and the unsafe thing possible?**

> "Any good tool is dangerous. I am a big fan of pocket knives and kitchen knives and all that sort of stuff, but they can really help in the kitchen or they can chop your fingers off. You just [have to] know how to use them." - Howard Hinnant

**22. Does the subject avoid depending on or encouraging preprocessor macros?**

> "Preprocessor usage should be eliminated." (S4.4)

**23. Can the subject's properties be verified by local inspection?**

> "Locality is good. When writing a piece of code, one would prefer it to be self-contained except where it needs a service from elsewhere." (S4.4)

**24. Does the subject integrate with existing C++ features rather than creating an isolated sub-language?**

> "Features accepted into C++ must work in combination, must support each other, must compensate for serious real problems in C++ as it stood without them, must fit syntactically and semantically into the language." (S6.4.4)

---

Count the yes answers. Divide by the number of applicable questions. Read the verdict.

| Score         | Verdict |
|---------------|---------|
| 90-100%       | **This is C++.** |
| 71-89%        | **This is not C++.** |
| 52-70%        | **This is certainly not C++.** |
| 29-51%        | **This is not even close to C++.** |
| 0-28%         | **This is another matter entirely.** |

---

## Execution Protocol

Each of the 24 questions is evaluated in three phases. A subagent assesses applicability and extracts evidence from the subject. The main context verifies every piece and renders the yes/no/N/A.

### Phase 0 - Applicability Assessment (subagent)

Before extracting evidence, the subagent first assesses whether the question is **applicable** to the subject.

**Applicability rule:** A question is applicable if the subject's design space intersects with the principle. A question is not applicable only when the subject has no conceivable bearing on the principle - not merely when the subject does not address it (that is the "No evidence" case, which remains a valid No answer).

**Locality uncertainty rule (question 23 only):** If the subject proposes annotations or features where local verifiability is genuinely ambiguous - where reasonable experts could disagree on whether the properties can be verified at the point of use - mark this question N/A with a note explaining the ambiguity. Question 23 should only produce a Yes or No when the evidence clearly supports one answer.

If a question is not applicable, the subagent returns `NOT APPLICABLE: [one sentence reason]` and skips evidence extraction. The main context records the N/A answer and moves to the next question.

### Phase 1 - Evidence Extraction (subagent)

For each applicable question (1 through 24, sequentially), launch a subagent. Pass it:

- The question text and its Stroustrup quote
- The full body of the subject document

**Subagent operational discipline:**

1. **Read the entire subject document end-to-end.** No skimming, no sampling. Process every section, code example, rationale paragraph, and design note.
2. **Extract evidence exhaustively.** For each passage, design choice, API shape, stated rationale, code example, or notable omission that bears on the question - extract it. A "piece of evidence" is a direct quote or a specific section reference with a paraphrase tight enough to verify against the source.
3. **Tag each piece.** Every piece of evidence gets exactly one tag: **supports-yes** or **supports-no**. The tag reflects whether that specific piece, taken on its own, indicates the subject satisfies the question.
4. **No interpretation, no verdict.** The subagent does not answer the question. It does not say yes or no overall. It returns only the tagged evidence list.
5. **No evidence is a valid result.** If the subagent completes a full read and finds nothing relevant, it returns exactly: `NO EVIDENCE FOUND`.
6. **Return format:**

```
EVIDENCE [n]: [supports-yes | supports-no]
Source: [section/heading/line reference in the subject]
Content: [direct quote or tight paraphrase]
Reasoning: [one sentence - why this bears on the question]
```

### Phase 2 - Verification (main context)

After each subagent returns:

1. **Re-read each piece of evidence.** For every item the subagent returned, re-examine the quoted content against the question text and the Stroustrup principle. The subagent's tag is a hypothesis, not a conclusion.
2. **Confirm or overturn each tag.** Mark each piece as `verified` (agrees with subagent's tag) or `overturned` (disagrees - state why in one sentence).
3. **Apply the decision rule:**
   - If **any** piece of evidence (after verification) supports-no: answer is **No**
   - If the subagent returned `NO EVIDENCE FOUND`: answer is **No**
   - Only if **every** piece of evidence (after verification) supports-yes: answer is **Yes**
4. **Write the answer.** One sentence citing the decisive evidence. If No, cite the specific piece that fails. If Yes, cite the strongest piece.

---

## File Output

Write the report to `is-this-cpp-{subject-slug}.md`, where `{subject-slug}` is derived from the paper number or subject name (lowercase, hyphens). The verdict is **output**. If a report with this name already exists, increment the version suffix: `-v2`, `-v3`, etc.

---

## Output Format

Begin with title, then subject identification block:

### Is [subject] C++?

* **Document:** [paper number if applicable, e.g. P2300R10; otherwise "N/A"]
* **Subject:** [title of paper, proposal, library, blog post, or feature]
* **Authors:** [author list if known; otherwise "N/A"]
* **Date:** [publication or revision date if known; otherwise "N/A"]
* **Model:** [ai-model identifier that performed the eval]

Then for each question, produce the answer followed by the evidence trail:

**N. [question text]**

**Answer:** Yes/No. [One sentence citing the decisive evidence.]

- **[source reference]:** "[direct quote or tight paraphrase]"
  - Tag: supports-yes/supports-no [verified/overturned]
  - Reasoning: [one sentence]

- **[source reference]:** "[direct quote or tight paraphrase]"
  - Tag: supports-yes/supports-no [verified/overturned]
  - Reasoning: [one sentence]

If no evidence was found for a question:

**N. [question text]**

**Answer:** No. No evidence of compliance in the subject.

If a question is not applicable to the subject:

**N. [question text]**

**Answer:** N/A. [One sentence explaining why the question does not apply to this subject.]

After all 24 answers, produce the summary:

**Score:** X / Y applicable (Z skipped)

**Verdict:** [verdict sentence from the table above]

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
