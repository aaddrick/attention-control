# Notice

This style combines two existing works. Neither author takes part in this
project. This file credits both.

## Shape layer

**[ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)** by Ayoub G. — MIT.

The shape layer (rules 1 to 11) adapts that project's ruleset. The evaluation
harness (`scripts/run_evals.py`, `evals/rubric.md`, and 14 of the 24 cases in
`evals/cases.jsonl`) derives from the same project. The MIT license text and
both copyright lines are in [LICENSE](./LICENSE).

Changes from that project:

1. Shape rule 2, "Do the work you own", is new here. The other ten shape rules
   adapt that project's ruleset.
2. The style ships as a Claude Code **output style**, so it applies to every
   turn without an invocation. Six other harnesses have no output style slot,
   so the same rules also ship as a skill.
3. A second layer controls sentence-level language, not response shape.
4. The rubric adds a `language` dimension and reweights the others.
5. Ten cases are new here: two `language`, two `verbatim`, one `decision`, and
   five `uncertainty`.

## Language layer

**[`asd-ste100` output style](https://gist.github.com/L1nefeed/4164ecaaf77879e76dca3c06f142f1c2)**
by [L1nefeed](https://github.com/L1nefeed).

That gist is a Claude Code output style that condenses ASD-STE100 into rules an
agent can follow. The language layer here derives from it directly: the word
rules, the grammar rules, the sentence limits, the structure rules, and the
scope section that separates prose from verbatim text.

The gist states no license. This project credits it by name and link, and
claims no permission beyond that. If L1nefeed wants a change to this credit or
to the derived text, open an issue and it gets made.

Changes from that gist:

1. The rules merge with a shape layer, so a precedence section resolves the four
   places where the two collide.
2. The standard-verb list is fixed to ten verbs, so a response cannot rotate
   synonyms.
3. A persistence section states that the rules do not expire across turns.

## ASD-STE100

**[ASD-STE100 Simplified Technical English](https://www.asd-ste100.org/)**,
Issue 9, published by the AeroSpace and Defence Industries Association of Europe.

The specification is copyright ASD. This repo reproduces **no text from it**.
The rules here reach this project through the gist above, reduced to what applies
to an agent that writes prose, code, and shell commands. Three deliberate
departures from the standard:

1. STE Part 1 rule GR-3 does not approve the pronoun "I". This style permits it,
   because the agent reports its own actions.
2. STE restricts writers to an approved dictionary of about 900 words. This style
   keeps a short list of standard verbs instead, and permits any technical term
   used consistently.
3. STE governs maintenance and procedural documentation. This style governs
   conversational output, so it adds shape rules that STE has no reason to carry.

"Simplified Technical English" and "ASD-STE100" name the source standard. The
ASD does not certify, endorse, or sponsor this project.
