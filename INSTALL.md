# Install Attention Control

Pick your agent below. Every route installs the same two-layer style. The
canonical text is [`output-styles/attention-control.md`](./output-styles/attention-control.md).
`scripts/sync_style.py` generates every other file in this repo from it.

Claude Code is the only agent with an output style slot. Codex, Cursor, Gemini
CLI, Copilot, and Zed have none, so the same rules ship as a skill, a rules
file, or an `AGENTS.md` block. Codex has a `personality` setting, but it takes
three fixed values and reads no custom file.

<details open>
<summary><strong>Claude Code</strong></summary>

The style applies to every turn once you select it. No slash command, no
invocation.

The style file sets `keep-coding-instructions: true`, so Claude Code keeps its
built-in software engineering instructions. This style changes how Claude
writes, not how it codes.

### Install from the terminal

```bash
claude plugin marketplace add aaddrick/attention-control
```

```bash
claude plugin install attention-control@attention-control
```

### Install from inside Claude Code

```
/plugin marketplace add aaddrick/attention-control
```

```
/plugin install attention-control@attention-control
```

```
/reload-plugins
```

`/plugin` with no argument opens the plugin manager: **Discover**, **Installed**,
**Marketplaces**, and **Errors** tabs.

### Select the style

Run `/config`, select **Output style**, and pick **Attention Control**. It takes
effect after `/clear` or the next session. Claude Code writes your choice to
`.claude/settings.local.json` in the current project.

### Select the style without the picker

`outputStyle` is a top-level key in the settings file. It sits beside `model`,
`env`, and `permissions`. It never goes inside them:

```json
{
  "model": "opus",
  "env": { "EXAMPLE_VAR": "1" },
  "outputStyle": "Attention Control"
}
```

`model` and `env` stand in for keys you may already have. Keep them. Add the
`outputStyle` line beside them.

Pick the file by scope:

1. `~/.claude/settings.json` applies to every project.
2. `.claude/settings.json` applies to one project, shared with collaborators.
3. `.claude/settings.local.json` applies to one project, for you alone.

The most local file wins. `.claude/settings.local.json` beats
`.claude/settings.json`, which beats `~/.claude/settings.json`.

`/config` writes your pick to `.claude/settings.local.json`, so a style you
once picked in a project keeps overriding your user file. Remove the
`outputStyle` key from that local file when the user-level value must apply.

### Install without the plugin

```bash
git clone https://github.com/aaddrick/attention-control
```

```bash
mkdir -p ~/.claude/output-styles
```

```bash
cp attention-control/output-styles/attention-control.md ~/.claude/output-styles/
```

### Verify

```bash
claude plugin list
```

Or run `/config` and check the Output style list for **Attention Control**.

### Update

```bash
claude plugin update attention-control
```

Restart Claude Code to apply it.

### Uninstall

```bash
claude plugin uninstall attention-control
```

```bash
claude plugin marketplace remove attention-control
```

Or keep it and turn it off: `claude plugin disable attention-control`.

### On-demand instead of always-on

The plugin also ships the same rules as a skill. Claude Code prefixes a plugin
skill with the plugin name, so the skill is
`/attention-control:attention-control`. Type it to turn the rules on for one
session, and "stop attention control" to turn them off.

To get the short name `/attention-control`, copy the skill in yourself instead:

```bash
mkdir -p ~/.claude/skills
```

```bash
cp -R attention-control/skills/attention-control ~/.claude/skills/
```

</details>

<details>
<summary><strong>Codex</strong></summary>

Codex has no output style. Its `personality` setting takes three fixed values
(`none`, `friendly`, `pragmatic`) and accepts no custom file, so the rules ship
as a skill and as an `AGENTS.md` block.

### Install from the terminal

```bash
codex plugin marketplace add aaddrick/attention-control --ref main
```

```bash
codex plugin add attention-control@attention-control
```

Codex reads this repo's `.claude-plugin/marketplace.json`, so one marketplace
file serves both harnesses.

### Install from inside Codex

```
/plugins
```

That opens the plugin browser. Install from it, then start a new thread. Codex
loads a plugin's skills at thread start.

### Invoke

```
$attention-control:attention-control
```

Codex prefixes a plugin skill with the plugin name. To get the short name
`$attention-control`, copy the skill in yourself instead:

```bash
git clone https://github.com/aaddrick/attention-control
```

```bash
mkdir -p ~/.agents/skills
```

```bash
cp -R attention-control/skills/attention-control ~/.agents/skills/
```

### Turn the built-in personality off

The personality instructions and these rules both govern tone. Set the
personality to `none` in `~/.codex/config.toml`:

```toml
personality = "none"
```

Or run `/personality` in a session and select **None**.

### Verify

```bash
codex plugin list
```

### Update

```bash
codex plugin marketplace upgrade attention-control
```

```bash
codex plugin remove attention-control
```

```bash
codex plugin add attention-control@attention-control
```

### Uninstall

```bash
codex plugin remove attention-control
```

```bash
codex plugin marketplace remove attention-control
```

### Always-on

Add [the snippet](#the-always-on-snippet) to `~/.codex/AGENTS.md`.

</details>

<details>
<summary><strong>Cursor</strong></summary>

Cursor has no output style, and it removed Custom Modes. It reads agent skills,
and it reads project rules. Use whichever fits.

### Install as a skill

```bash
npx skills add aaddrick/attention-control -a cursor -y
```

```bash
npx skills add aaddrick/attention-control -a cursor -g
```

The first command installs to `.agents/skills/` in this workspace. `-g` installs
to `~/.cursor/skills/` for all projects.

Without the CLI:

```bash
git clone https://github.com/aaddrick/attention-control
```

```bash
mkdir -p ~/.cursor/skills
```

```bash
cp -R attention-control/skills/attention-control ~/.cursor/skills/
```

### Install as an always-on rule

```bash
git clone https://github.com/aaddrick/attention-control
```

```bash
mkdir -p .cursor/rules
```

```bash
cp attention-control/.cursor/rules/attention-control.mdc .cursor/rules/
```

The rule sets `alwaysApply: true`, so it loads on every request in that project.

### Invoke

Type `/attention-control` in the chat input. Type `@` and pick the skill to
attach it as reference material instead.

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
```

```bash
rm .cursor/rules/attention-control.mdc
```

</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

Gemini CLI has no output style and no plugin marketplace. Two native routes: a
**custom command** that you invoke, or an **extension** that applies from
message one.

### Install (extension, always-on)

```bash
gemini extensions install https://github.com/aaddrick/attention-control
```

The extension loads `GEMINI.md`, which imports the full ruleset. `git` must be
installed.

### Install (command, opt-in)

```bash
mkdir -p ~/.gemini/commands
```

```bash
curl -fsSL https://raw.githubusercontent.com/aaddrick/attention-control/main/skills/attention-control/agents/gemini.toml -o ~/.gemini/commands/attention-control.toml
```

Start a new session and type `/attention-control`.

### Verify

```bash
gemini extensions list
```

```bash
ls ~/.gemini/commands
```

The first command covers the extension route. The second covers the command
route: `attention-control.toml` must be present. Inside Gemini CLI, run
`/extensions list` instead.

### Update

```bash
gemini extensions update attention-control
```

On the command route, run the `curl` command above again.

### Uninstall

```bash
gemini extensions uninstall attention-control
```

```bash
rm ~/.gemini/commands/attention-control.toml
```

The first command covers the extension route. The second covers the command
route.

</details>

<details>
<summary><strong>GitHub Copilot (VS Code and Copilot CLI)</strong></summary>

Copilot has no output style. It reads agent skills natively: it scans
`.github/skills/`, `.claude/skills/`, and `.agents/skills/` in the project, and
`~/.copilot/skills/` globally.

### Install

```bash
npx skills add aaddrick/attention-control -a github-copilot
```

```bash
npx skills add aaddrick/attention-control -a github-copilot -g
```

The first command installs to `.agents/skills/` in this project. `-g` installs
to `~/.copilot/skills/` for all projects.

Without the CLI:

```bash
git clone https://github.com/aaddrick/attention-control
```

```bash
mkdir -p ~/.copilot/skills
```

```bash
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

Zed has no output style. It reads agent skills, and it reads a global
`AGENTS.md`.

### Install

Run the **agent: create skill from url** command from the command palette, then
paste:

```
https://github.com/aaddrick/attention-control/blob/main/skills/attention-control/SKILL.md
```

Then type `/attention-control` in the Agent Panel.

From the filesystem instead:

```bash
git clone https://github.com/aaddrick/attention-control
```

```bash
mkdir -p ~/.agents/skills
```

```bash
cp -R attention-control/skills/attention-control ~/.agents/skills/
```

Zed reads `~/.agents/skills/` for every project and `<worktree>/.agents/skills/`
for one project.

### Verify

Open the Skills manager (`cmd-alt-l` on macOS, `ctrl-alt-l` on Linux) and look
for `attention-control`.

### Update

Re-import from the same URL, or re-copy the folder after `git pull`.

### Uninstall

Remove `attention-control` from the Skills manager, or delete
`~/.agents/skills/attention-control`.

### Always-on

Add [the snippet](#the-always-on-snippet) to `~/.config/zed/AGENTS.md`.

</details>

<details>
<summary><strong>OpenCode, Amp, Pi, and any other agent-skills harness</strong></summary>

Any harness that reads agent skills works. The `skills` CLI knows 80 or more
agent names. Swap `-a <agent>` for yours.

```bash
npx skills add aaddrick/attention-control
```

```bash
npx skills add aaddrick/attention-control -g
```

```bash
npx skills add aaddrick/attention-control -a opencode -y
```

```bash
npx skills add aaddrick/attention-control -a amp -y
```

```bash
npx skills add aaddrick/attention-control -a pi -y
```

The first command installs to this workspace. `-g` installs for all projects.

Pi calls skills as `/skill:attention-control` and needs
`{ "enableSkillCommands": true }` in its `settings.json`.

For a harness that reads `AGENTS.md`, paste
[the always-on snippet](#the-always-on-snippet) into your project's
`AGENTS.md`. For the full ruleset instead, copy the body of
[`output-styles/attention-control.md`](./output-styles/attention-control.md).

This repo's own `AGENTS.md` is a different file. It tells an agent how to work
on this repository, and it mirrors `CLAUDE.md`.

</details>

## The always-on snippet

Paste this into whichever file your agent loads on every session. It is the
short form: the 11 shape rules, the language rules that matter most, and the 6
exceptions.

<!-- BEGIN GENERATED SNIPPET: scripts/sync_style.py -->

```markdown
## Output style

Air traffic control phraseology exists because a distracted reader mishears an
instruction. Apply the same two disciplines to every response.

Shape:

1. Lead with the next action.
2. Do the work you own.
3. Number multi-step work.
4. End with one concrete next action.
5. Suppress tangents.
6. Restate state every turn.
7. Give time estimates in concrete units.
8. Show what now works.
9. State errors flat.
10. Cap lists at 5 items.
11. No preamble, no recap, no closer.

Language:

- One word, one meaning. Use each word with only one meaning in a response.
- One action, one verb. Pick one verb for an action and use it every time. Do
  not rotate synonyms.
- Use the active voice. Name the actor: "The test writes a temporary file", not
  "A temporary file is written".
- Use only simple tenses: simple present, simple past, simple future,
  infinitive, and imperative.
- Do not use the perfect tenses. Write "I changed the file", not "I have
  changed the file".
- Maximum 20 words per sentence in instructions and procedures.
- Maximum 25 words per sentence in descriptions and explanations.
- Limit noun clusters to 3 words. Write "the handler that sets task-queue
  priority", not "the task queue priority handler".
- Use these standard verbs: check, make sure, start, stop, use, show, find,
  change, remove, need.

Reproduce verbatim: code, commands, file paths, identifiers, and error
messages; text you quote from files, documentation, or other sources.

Accuracy always wins over style. Never remove a fact, a condition, a number, or
a scope qualifier to make a sentence shorter. If a rule and precision conflict,
keep the precision.

Uncertainty:

- A hedging adverb carries no information: "perhaps", "possibly", "arguably",
  "somewhat". Delete it.
- Uncertainty is a fact about what you know. State it in plain words: "I have
  not seen your schema", "this depends on the version, which I cannot check".
- Never invent a specific to fill the gap. A version number, a date, a flag
  name, a release note, or a line number you cannot check is a fabrication,
  whatever tone you write it in.

Exceptions:

1. **The reader asks you to explain or walk them through.** Explain fully.
2. **An irreversible action comes next.** Confirm first.
3. **The last three turns were "still broken".** Stop iterating on code.
4. **The request is truly ambiguous.** One short question beats a guess and a
   rewrite.
5. **A rule fights the answer.** The answer wins and the shape stays.
6. **A rule fights the harness.** The system prompt outranks this file.
```

<!-- END GENERATED SNIPPET -->

## How activation works

1. **Claude Code, plugin installed.** Nothing changes until you select the output
   style in `/config` or set `outputStyle` in settings. The plugin does not force
   itself on.
2. **Claude Code, style selected.** The rules apply to every turn of every
   session, with no invocation.
3. **Every other harness.** No other harness has an output style slot, so the
   rules ship as a skill. They apply after you invoke `/attention-control`, or
   from message one if you paste the always-on snippet into a persistent context
   file.
4. **Plugin routes name the skill twice.** Claude Code and Codex both prefix a
   plugin skill with the plugin name:
   `/attention-control:attention-control` and
   `$attention-control:attention-control`. A skill you copy in yourself keeps the
   short name.

## Troubleshooting

**The style is not in the `/config` list.** Restart Claude Code. Claude Code
reads the plugin index at startup.

**`/output-style` reports an unknown command.** Claude Code removed that command
in v2.1.91. Use `/config` and select **Output style**.

**You picked the style but replies still open with preamble.** Run `/clear`. The
output style is part of the system prompt, which Claude Code reads once at
session start.

**`claude plugin marketplace add` fails.** Use the `owner/repo` form. A local
path must point at the repo root, not at `.claude-plugin/`.

**`/attention-control` is missing from autocomplete.** Start a new session.
Your agent indexes skills at session start. Check that the folder landed where
your agent scans. Check that the frontmatter `name` matches the folder name. On
a plugin route, type the namespaced name instead:
`/attention-control:attention-control`.

**The agent obeys the shape rules but writes passive, hedged sentences.** The
language layer is the second half of the file. Check your copy: the last section
is "Examples".

**You want different rules.** Fork, edit
`output-styles/attention-control.md`, run `python3 scripts/sync_style.py`, then
swap your copy in, one command at a time:

```bash
claude plugin uninstall attention-control
```

```bash
claude plugin marketplace remove attention-control
```

```bash
claude plugin marketplace add <your-username>/attention-control
```

```bash
claude plugin install attention-control@attention-control
```
