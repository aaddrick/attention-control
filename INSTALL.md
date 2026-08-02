# Install Attention Control

Pick your agent below. Every route installs the same two-layer style. The
canonical text is [`output-styles/attention-control.md`](./output-styles/attention-control.md).
`scripts/sync_style.py` generates every other file in this repo from it.

<details open>
<summary><strong>Claude Code</strong></summary>

Claude Code is the only harness with a native output style, so the style applies
to every turn once you select it. No slash command, no invocation.

### Install

```bash
claude plugin marketplace add aaddrick/attention-control
claude plugin install attention-control@attention-control
```

Run `/config`, select **Output style**, and pick **Attention Control**. It takes
effect after `/clear` or the next session.

### Install without the picker

```json
{ "outputStyle": "Attention Control" }
```

Put that in `~/.claude/settings.json` for every project, or in
`.claude/settings.json` for one project.

### Install without the plugin

```bash
git clone https://github.com/aaddrick/attention-control
mkdir -p ~/.claude/output-styles
cp attention-control/output-styles/attention-control.md ~/.claude/output-styles/
```

### Verify

```bash
claude plugin list
```

Or run `/config` and check the Output style list for **Attention Control**.

### Update

```bash
claude plugin marketplace update attention-control
```

### Uninstall

```bash
claude plugin uninstall attention-control
claude plugin marketplace remove attention-control
```

Or keep it and turn it off: `claude plugin disable attention-control`.

### On-demand instead of always-on

The plugin also ships the same rules as a skill. Type `/attention-control` to
turn them on for one session, and "stop attention control" to turn them off.

</details>

<details>
<summary><strong>Codex</strong></summary>

### Install

```bash
codex plugin marketplace add aaddrick/attention-control --ref main
codex plugin add attention-control@attention-control
```

Type `$attention-control`.

### Verify

```bash
codex plugin list
```

### Update

```bash
codex plugin marketplace upgrade attention-control
codex plugin remove attention-control
codex plugin add attention-control@attention-control
```

### Uninstall

```bash
codex plugin remove attention-control
codex plugin marketplace remove attention-control
```

### Always-on

Add [the snippet](#the-always-on-snippet) to `~/.codex/AGENTS.md`.

</details>

<details>
<summary><strong>Cursor</strong></summary>

Cursor reads agent skills, and it reads project rules. Use whichever fits.

### Install as a skill

```bash
npx skills add aaddrick/attention-control -a cursor -y      # this workspace
npx skills add aaddrick/attention-control -a cursor -g      # all projects
```

Without the CLI:

```bash
git clone https://github.com/aaddrick/attention-control
mkdir -p ~/.cursor/skills
cp -R attention-control/skills/attention-control ~/.cursor/skills/
```

### Install as an always-on rule

```bash
git clone https://github.com/aaddrick/attention-control
mkdir -p .cursor/rules
cp attention-control/.cursor/rules/attention-control.mdc .cursor/rules/
```

The rule sets `alwaysApply: true`, so it loads on every request in that project.

### Verify

Type `/` in the chat input and check that `attention-control` appears. For the
rule route, open Cursor Settings and look under Project Rules.

### Update

```bash
npx skills update attention-control
```

Or re-copy the file after `git pull`.

### Uninstall

```bash
npx skills remove attention-control
rm .cursor/rules/attention-control.mdc
```

</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

Gemini CLI has no plugin marketplace. Two native routes: a **custom command**
that you invoke, or an **extension** that applies from message one.

### Install (extension, always-on)

```bash
gemini extensions install https://github.com/aaddrick/attention-control
```

The extension loads `GEMINI.md`, which imports the full ruleset. `git` must be
installed.

### Install (command, opt-in)

```bash
mkdir -p ~/.gemini/commands
curl -fsSL https://raw.githubusercontent.com/aaddrick/attention-control/main/skills/attention-control/agents/gemini.toml \
  -o ~/.gemini/commands/attention-control.toml
```

Start a new session and type `/attention-control`.

### Verify

```bash
gemini extensions list          # extension route
ls ~/.gemini/commands           # command route: attention-control.toml present
```

### Update

```bash
gemini extensions update attention-control    # extension route
# command route: run the curl above again
```

### Uninstall

```bash
gemini extensions uninstall attention-control    # extension route
rm ~/.gemini/commands/attention-control.toml     # command route
```

</details>

<details>
<summary><strong>GitHub Copilot (VS Code and Copilot CLI)</strong></summary>

Copilot reads agent skills natively. It scans `.github/skills/`,
`.claude/skills/`, and `.agents/skills/` in the project, and `~/.copilot/skills/`,
`~/.claude/skills/`, and `~/.agents/skills/` globally.

### Install

```bash
npx skills add aaddrick/attention-control -a github-copilot        # this project
npx skills add aaddrick/attention-control -a github-copilot -g     # all projects
```

Without the CLI:

```bash
git clone https://github.com/aaddrick/attention-control
mkdir -p ~/.copilot/skills
cp -R attention-control/skills/attention-control ~/.copilot/skills/
```

### Verify

Type `/` in the chat input and check that `attention-control` appears.

### Update

```bash
npx skills update attention-control
```

### Uninstall

```bash
npx skills remove attention-control
```

### Always-on

Add [the snippet](#the-always-on-snippet) to `.github/copilot-instructions.md`.

</details>

<details>
<summary><strong>Zed</strong></summary>

### Install

In the Agent Panel, open the Skills manager and choose **Create skill from URL**,
then paste:

```
https://github.com/aaddrick/attention-control/blob/main/skills/attention-control/SKILL.md
```

Save it in **User** scope for every project, or **Project** scope for one. Then
type `/attention-control` in the Agent Panel.

From the filesystem instead:

```bash
git clone https://github.com/aaddrick/attention-control
cp -R attention-control/skills/attention-control ~/.config/zed/skills/
```

### Verify

Open the Skills manager and look for `attention-control`.

### Update

Re-import from the same URL, or re-copy the folder after `git pull`.

### Uninstall

Remove `attention-control` from the Skills manager, or delete
`~/.config/zed/skills/attention-control`.

### Always-on

Add [the snippet](#the-always-on-snippet) to `~/.config/zed/AGENTS.md`.

</details>

<details>
<summary><strong>OpenCode, Amp, Pi, and any other agent-skills harness</strong></summary>

Any harness that reads agent skills works. Swap `-a <agent>` for yours.

```bash
npx skills add aaddrick/attention-control                  # this workspace
npx skills add aaddrick/attention-control -g               # all projects
npx skills add aaddrick/attention-control -a opencode -y
npx skills add aaddrick/attention-control -a amp -y
npx skills add aaddrick/attention-control -a pi -y
```

Pi calls skills as `/skill:attention-control` and needs
`{ "enableSkillCommands": true }` in its `settings.json`.

For a harness that reads `AGENTS.md`, copy this repo's generated
[`AGENTS.md`](./AGENTS.md) into your project root instead.

</details>

## The always-on snippet

Paste this into whichever file your agent loads on every session. It is the
short form: the 10 shape rules plus the language rules that matter most.

```markdown
## Output style

Air traffic control phraseology exists because a distracted reader mishears an
instruction. Apply the same two disciplines to every response.

Shape:

1. Lead with the next action: a command, a path, or a snippet. Not context.
2. Number multi-step work. One bounded action per step.
3. End with one concrete next action, doable in under two minutes.
4. Suppress tangents. Finish the current issue first.
5. Restate state every turn ("Step 3 of 5 done: I updated the schema.").
6. Give time estimates in concrete units. Never "some work".
7. After a change, name what now works and how to see it.
8. State errors flat: location, cause, fix. No "uh oh".
9. Cap lists at 5 items. Past five, split into now/later.
10. No preamble, no recap, no closer.

Language:

- One word, one meaning. One action, one verb. Do not rotate synonyms.
- Use: check, make sure, start, stop, use, show, find, change, remove, need.
- Use the active voice and name the actor.
- Use simple tenses only. No perfect tense, no auxiliary stacks.
- Maximum 20 words per instruction, 25 per explanation.
- Limit noun clusters to 3 words.

Reproduce code, commands, paths, identifiers, error messages, and quoted text
verbatim. Accuracy beats brevity: never drop a fact, number, condition, or scope
qualifier to shorten a sentence.

Exceptions: explain fully when asked to explain or walk through. Confirm before
a destructive action. After three failed fixes, stop and name the assumption
that might be wrong. Ask one short question when the request is truly ambiguous.
```

## How activation works

1. **Claude Code, plugin installed.** Nothing changes until you select the output
   style in `/config` or set `outputStyle` in settings. The plugin does not force
   itself on.
2. **Claude Code, style selected.** The rules apply to every turn of every
   session, with no invocation.
3. **Every other harness.** The rules ship as a skill. They apply after you
   invoke `/attention-control`, or from message one if you paste the always-on
   snippet into a persistent context file.

## Troubleshooting

**The style is not in the `/config` list.** Restart Claude Code. Claude Code
reads the plugin index at startup.

**You picked the style but replies still open with preamble.** Run `/clear`. The
output style is part of the system prompt, which Claude Code reads once at
session start.

**`claude plugin marketplace add` fails.** Use the `owner/repo` form. A local
path must point at the repo root, not at `.claude-plugin/`.

**`/attention-control` is missing from autocomplete.** Start a new session.
Your agent indexes skills at session start. Check that the folder landed where
your agent scans. Check that the frontmatter `name` matches the folder name.

**The agent obeys the shape rules but writes passive, hedged sentences.** The
language layer is the second half of the file. Check your copy: the last section
is "Examples".

**You want different rules.** Fork, edit
`output-styles/attention-control.md`, run `python3 scripts/sync_style.py`, then
swap your copy in:

```bash
claude plugin uninstall attention-control
claude plugin marketplace remove attention-control
claude plugin marketplace add <your-username>/attention-control
claude plugin install attention-control@attention-control
```
