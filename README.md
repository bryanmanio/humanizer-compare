# humanizer-compare

A skill for Claude Code that rewrites the copy on a website with [humanizer](https://github.com/blader/humanizer), then shows the old and new pages side by side so you can judge the edits in place.

![An AI-written version of a landing page on the left, with its headline "Unlock the Full Power of Your Server, Right From Your Menu Bar" outlined in red, and the humanized page on the right with "Everything running on your server, in your menu bar" outlined in green. A tooltip under the new headline names the humanizer patterns, §16 Sales language and §20 Decorative headings, and explains the change.](docs/screenshot.png)

For this screenshot, the left side was written on purpose with as many AI writing patterns as possible. The right side is what the skill turned it into.

## What you get

The skill edits the copy in your source files, then opens a comparison page on your local dev server:

- The page as it was on the left and the edited page on the right, scrolling together.
- Changed text outlined in red on the left and green on the right.
- Hover a green box to see which humanizer pattern the edit fixes and why that text was changed.
- A viewport picker to check desktop and phone widths, including copy that only shows on mobile.

It also replies with a table of every edit and a list of what it left alone. Nothing is committed. The comparison files go in a `_compare/` folder that the skill adds to `.git/info/exclude`, so your repo stays clean.

## Install

### Claude Code plugin

```text
/plugin marketplace add bryanmanio/humanizer-compare
/plugin install humanizer-compare@humanizer-compare
```

Installed this way, the skill answers to `/humanizer-compare:humanizer-compare`. Loading a skill from the plugin root needs Claude Code 2.1.142 or newer. On older versions, use the Skills CLI below.

### Skills CLI

```sh
npx skills add bryanmanio/humanizer-compare --global --agent claude-code
```

Leave off `--global` to install it for the current project only.

### Manually

```sh
git clone https://github.com/bryanmanio/humanizer-compare ~/.claude/skills/humanizer-compare
```

To update a manual install, run `git -C ~/.claude/skills/humanizer-compare pull`.

## Use

Open your site's project in Claude Code and ask for it:

```text
/humanizer-compare
```

Or say it in your own words, for example "humanize the copy on my landing page and show me a before and after". The skill finds the copy, snapshots each page, makes the edits, and gives you a `localhost` link to the comparison.

It works on plain HTML sites and on rendered ones such as Next.js, Astro or React. For rendered sites it saves the page's HTML before editing and strips the scripts, so hydration can't swap the new copy into the "before" side.

## Requirements

- Python 3, for the snapshot script and, if your project has no dev server, `python3 -m http.server`.
- A browser tool for Claude (Playwright or a Chrome DevTools MCP) if you want it to check the comparison page itself. Without one, it gives you the link and you check it.

## How the hover reasons work

For each edit, the skill writes an entry in `_compare/changes.json` with the old text, the new text, the humanizer pattern (for example "§20 Decorative headings") and a sentence or two applying that pattern to the specific edit. The comparison page matches each entry to its green box. Edits with nothing visible to outline, like a changed `<title>` or `aria-label`, are listed when you hover the change count in the header.

## Credits

The rewriting rules are [humanizer](https://github.com/blader/humanizer) by Siqi Chen, MIT licensed. A pinned copy is in `humanizer/`, so the skill runs the same rules no matter what else you have installed. `humanizer/SOURCE` records the version and how to update it.

## License

MIT
