---
description: Export a Cursor or Claude Code chat to clean markdown - skips thinking bubbles, renders the conversation as the user saw it
---

<!--
When this file is mentioned or loaded, adopt it as system context in full.
You are this tool. Follow its rules. Do not summarize it or discuss it
abstractly. Operate from it.
-->

# Chatlight

A chat is ephemeral until someone pulls it into daylight. Chatlight reads the raw session storage - Cursor's vscdb or Claude Code's JSONL - and renders the conversation exactly as the user saw it: user messages in blockquotes, agent responses verbatim, subagent summaries bracketed, thinking bubbles gone. One markdown file. No artifacts of the underlying format survive.

<img src="images/chatlight.png" alt="Chatlight" width="100%">

---

## Platform Detection

Detect by which session store actually holds data, not by which dotfile directory exists - a workspace can contain both `.cursor/` and `.claude/`:
- **Cursor**: state.vscdb exists at the platform-specific path and contains a `composerData:` row
- **Claude Code**: `~/.claude/projects/<sanitized-path>/` exists and contains `.jsonl` files

If both stores hold data for the workspace, ask which to export.

Write only the matching `<python>` block's content to a .py file (strip the fence markers). Run it. File the output.

---

## Invocation

Both arguments are positional and optional:
1. **Chat UUID** - the session to export. If omitted, use the most recent session (highest mtime)
2. **Output file path** - where to write the markdown. Default: derive from chat title

The Claude Code script also accepts `--branch live|longest` (see Rewinds) and `--force` to overwrite an existing output file. Its progress and skip report goes to stderr.

### Finding the current chat UUID

**Cursor:** List directories in `~/.cursor/projects/{project-slug}/agent-transcripts/`. Sort by mtime descending. The most recent directory name is the chat UUID. The project-slug derives from the workspace path by replacing path separators and colons with dashes (e.g. `c:\Users\Vinnie\src\cursor` becomes `c-Users-Vinnie-src-cursor`).

**Claude Code:** List `.jsonl` files in `~/.claude/projects/<sanitized-path>/`. Sort by mtime descending. The most recent filename (without `.jsonl`) is the session UUID. The sanitized path is the absolute workspace path with both `/` and `.` replaced by `-` (e.g. `/home/user/my.app` becomes `-home-user-my-app`).

---

## Execution

1. Detect the platform
2. Extract the code from inside the matching `<python>` block - strip the opening and closing triple-backtick fence lines, write only the Python source to a scratch .py file. Extract it programmatically; do not retype it
3. Run the script with the chat UUID and output path
4. Read the stderr report. It states how many user messages, agent responses and subagent summaries were exported, and lists every category of event that was skipped. If it prints a `WARNING`, act on it before filing the output
5. File the markdown as **output**: `chatlight-{chat-name-slug}.md`

The .py file is **scratch**.

---

## Output Format

```markdown
# Chat Title Here

---

> User's first message here
> (multiline blockquote, each line prefixed with >)

Agent's visible response text, unmodified.

*[Subagent: Research: fast prompt titling practice]*
Subagent's final text bubble content here.

Agent's next visible response text.

---

> User's second message

Agent response.

---
```

Rules:
- H1 heading with chat title at top (Cursor: `composerHeaders.name`; Claude Code: the session's own `ai-title` event, falling back to the first 6 words of the first user message)
- `---` before every user message (including the first)
- User text in blockquote (`> ` prefix on each line)
- One blank line between every element
- Subagent summaries prefixed with `*[Subagent: {description}]*` on a line alone, followed by blank line, then the summary text
- Agent text reproduced verbatim - preserve all markdown formatting
- No thinking content appears anywhere
- `---` after the final agent response (end-of-file marker)
- Empty text bubbles (text field is `""`) produce no output - skip silently

### Claude Code specifics

**Message shape.** `message.content` is a bare string for anything the human typed and a block list for tool results and richer turns. Handle both.

**Plumbing.** Much of what is stored under `type: "user"` was never typed. `<system-reminder>` blocks carry injected context (CLAUDE.md, memory, environment) and are stripped from within the surrounding message, since a real message can wrap one. `<task-notification>`, `<local-command-*>` envelopes, `isMeta` events and `tool_result` blocks are dropped whole. A slash command arrives wrapped in `<command-name>`/`<command-args>`; the user did type it, so it is unwrapped to the `/command args` line.

**Rewinds.** The JSONL is an append-only tree, not a flat log, so reading it linearly replays abandoned branches as real conversation. Follow `parentUuid` from a leaf to the root. `--branch live` (default) starts from the newest leaf, which is what the UI shows; `--branch longest` starts from the deepest, for when a rewind left the substance on a branch the UI no longer displays. If more events are skipped than exported, the script warns and names the flag.

**Subagents.** A synchronous agent returns its report as the `tool_result`. A background agent returns only a launch stub naming an internal `agentId`; the real report arrives in a later `<task-notification>` and is spooled to a file that is deleted when the session ends. Resolve in that order, strip the `agentId` and any trailing `<usage>` block, and expect older sessions to report `no summary available`.

---

## Success Criteria

- The output contains every user message and every visible agent response from the surviving branch, in order
- No thinking text appears
- No tool-call metadata appears (except subagent summaries)
- No harness plumbing appears - no `<system-reminder>`, no `<task-notification>`, no internal `agentId`
- The markdown renders cleanly in any viewer
- The script exits 0. Any lossy outcome is counted and reported on stderr rather than passed off as a complete export

---

<python id="cursor">

```
"""
Chatlight - Cursor export
Usage: python chatlight_cursor.py <chat-uuid> <output-path>

Reads state.vscdb (cursorDiskKV table), walks bubble headers, writes clean markdown.
Exit 0 on success, 1 on failure.
"""
import sys
import os
import json
import sqlite3
import tempfile
import shutil

def main():
    if len(sys.argv) < 3:
        print("Usage: python chatlight_cursor.py <chat-uuid> <output-path>", file=sys.stderr)
        sys.exit(1)

    chat_uuid = sys.argv[1]
    output_path = sys.argv[2]

    # Locate state.vscdb
    if sys.platform == "win32":
        vscdb_path = os.path.join(os.environ["APPDATA"], "Cursor", "User", "globalStorage", "state.vscdb")
    elif sys.platform == "darwin":
        vscdb_path = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")
    else:
        vscdb_path = os.path.expanduser("~/.config/Cursor/User/globalStorage/state.vscdb")

    if not os.path.exists(vscdb_path):
        print(f"Error: state.vscdb not found at {vscdb_path}", file=sys.stderr)
        sys.exit(1)

    # Open read-only; fall back to temp copy if locked
    temp_copy = None
    try:
        conn = sqlite3.connect(f"file:{vscdb_path}?mode=ro", uri=True)
        conn.execute("SELECT 1 FROM cursorDiskKV LIMIT 1")
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        temp_copy = os.path.join(tempfile.gettempdir(), "chatlight_state.vscdb")
        shutil.copy2(vscdb_path, temp_copy)
        conn = sqlite3.connect(f"file:{temp_copy}?mode=ro", uri=True)

    cursor = conn.cursor()

    # Load composerData from cursorDiskKV (blob values, decode as utf-8)
    key = f"composerData:{chat_uuid}"
    cursor.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (key,))
    row = cursor.fetchone()
    if row is None:
        print(f"Error: composerData not found for UUID '{chat_uuid}'", file=sys.stderr)
        conn.close()
        if temp_copy:
            os.unlink(temp_copy)
        sys.exit(1)

    raw = row[0]
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    composer_data = json.loads(raw)

    # Get chat title from composerHeaders table
    chat_title = "Untitled Chat"
    try:
        cursor.execute("SELECT value FROM composerHeaders WHERE composerId = ?", (chat_uuid,))
        hrow = cursor.fetchone()
        if hrow:
            hval = hrow[0]
            if isinstance(hval, bytes):
                hval = hval.decode("utf-8")
            hdata = json.loads(hval)
            chat_title = hdata.get("name", chat_title)
    except (sqlite3.OperationalError, json.JSONDecodeError):
        pass

    headers = composer_data.get("fullConversationHeadersOnly", [])

    lines = []
    lines.append(f"# {chat_title}")
    lines.append("")

    def get_bubble(bubble_id):
        bkey = f"bubbleId:{chat_uuid}:{bubble_id}"
        cursor.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (bkey,))
        brow = cursor.fetchone()
        if brow is None:
            return None
        bval = brow[0]
        if isinstance(bval, bytes):
            bval = bval.decode("utf-8")
        return json.loads(bval)

    def get_bubble_text(bubble_id):
        blob = get_bubble(bubble_id)
        if blob is None:
            return None
        return blob.get("text", "")

    def get_subagent_summary(subagent_id):
        """Get the last visible text bubble from a subagent's composerData."""
        skey = f"composerData:{subagent_id}"
        cursor.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (skey,))
        srow = cursor.fetchone()
        if srow is None:
            return None
        sval = srow[0]
        if isinstance(sval, bytes):
            sval = sval.decode("utf-8")
        sdata = json.loads(sval)
        sheaders = sdata.get("fullConversationHeadersOnly", [])
        for h in reversed(sheaders):
            grouping = h.get("grouping", {})
            htype = h.get("type", grouping.get("type"))
            if htype == 2 and grouping.get("hasText") and not grouping.get("hasThinking"):
                sbid = h.get("bubbleId")
                if sbid:
                    sbkey = f"bubbleId:{subagent_id}:{sbid}"
                    cursor.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (sbkey,))
                    sbrow = cursor.fetchone()
                    if sbrow:
                        sbval = sbrow[0]
                        if isinstance(sbval, bytes):
                            sbval = sbval.decode("utf-8")
                        sblob = json.loads(sbval)
                        text = sblob.get("text", "")
                        if text:
                            return text
        return None

    for header in headers:
        grouping = header.get("grouping", {})
        msg_type = header.get("type", grouping.get("type"))
        bubble_id = header.get("bubbleId")

        if msg_type == 1:
            # User message
            text = get_bubble_text(bubble_id)
            if text is None or text == "":
                continue
            lines.append("---")
            lines.append("")
            for line in text.split("\n"):
                lines.append(f"> {line}")
            lines.append("")

        elif msg_type == 2:
            # Agent response - classify by grouping flags
            if grouping.get("hasThinking"):
                continue

            tool_id = grouping.get("toolFormerTool")
            if tool_id == 48:
                # Subagent/Task call
                blob = get_bubble(bubble_id)
                if blob:
                    try:
                        tf_data = blob.get("toolFormerData", {})
                        params = tf_data.get("params", "")
                        additional = tf_data.get("additionalData", {})
                        subagent_id = additional.get("subagentComposerId")

                        # params is a JSON string; extract the human-readable label
                        desc = "unnamed task"
                        if params:
                            pdata = params
                            if isinstance(pdata, str):
                                try:
                                    pdata = json.loads(pdata)
                                except json.JSONDecodeError:
                                    pdata = {}
                            if isinstance(pdata, dict):
                                desc = pdata.get("description") or pdata.get("name") or "unnamed task"

                        summary = None
                        if subagent_id:
                            summary = get_subagent_summary(subagent_id)

                        if summary:
                            lines.append(f"*[Subagent: {desc}]*")
                            lines.append("")
                            lines.append(summary)
                            lines.append("")
                        else:
                            lines.append(f"*[Subagent: {desc} - no summary available]*")
                            lines.append("")
                    except (json.JSONDecodeError, KeyError):
                        pass
                continue

            if tool_id is not None:
                # Any other tool call - skip
                continue

            if grouping.get("capabilityType") == 15:
                continue

            if grouping.get("hasText"):
                # Visible agent response
                text = get_bubble_text(bubble_id)
                if text is None or text == "":
                    continue
                lines.append(text)
                lines.append("")

    # End-of-file marker
    lines.append("---")
    lines.append("")

    conn.close()
    if temp_copy and os.path.exists(temp_copy):
        os.unlink(temp_copy)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Exported: {chat_title} -> {output_path}")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

</python>

<python id="claude-code">

```
"""
Chatlight - Claude Code export
Usage: python chatlight_claude.py [session-uuid] [output-path] [--branch live|longest] [--force]

Reads JSONL session file, walks the surviving conversation branch, writes clean markdown.
With no session-uuid, exports the most recent session. Exit 0 on success, 1 on failure.
"""
import sys
import os
import re
import json
import glob as globmod

LAUNCH_STUB = "Async agent launched successfully"

# Envelopes the harness injects under type "user" that the human never typed.
DROP_PREFIXES = (
    "<local-command-stdout>",
    "<local-command-caveat>",
    "<task-notification>",
    "<command-message>",
    "<command-args>",
    "<system-reminder>",
    "[Request interrupted",
)
SYSTEM_REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)
COMMAND_NAME = re.compile(r"<command-name>(.*?)</command-name>", re.DOTALL)
COMMAND_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.DOTALL)
AGENT_ID = re.compile(r"^agentId:.*$", re.MULTILINE)
USAGE = re.compile(r"<usage>.*?</usage>", re.DOTALL)
TOOL_USE_ID = re.compile(r"<tool-use-id>(.*?)</tool-use-id>", re.DOTALL)
OUTPUT_FILE = re.compile(r"<output-file>(.*?)</output-file>", re.DOTALL)


def die(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def texts(content):
    """Text strings in a message.content, which is a bare string for anything
    the human typed and a block list for tool results and richer turns."""
    if isinstance(content, str):
        return [content]
    if not isinstance(content, list):
        return []
    return [
        b["text"]
        for b in content
        if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)
    ]


def clean(text):
    """Visible user text, or "" if the whole message was harness plumbing."""
    text = SYSTEM_REMINDER.sub("", text).strip()
    if not text:
        return ""
    name = COMMAND_NAME.search(text)
    if name:  # a slash command the user did type: render it as typed
        args = COMMAND_ARGS.search(text)
        return f"{name.group(1).strip()} {args.group(1).strip() if args else ''}".strip()
    if text.startswith(DROP_PREFIXES):
        return ""
    return text


def branch(events, mode):
    """Events on one conversation branch, newest-leaf ("live") or deepest ("longest").

    The JSONL is an append-only tree: rewinds and edited messages leave abandoned
    branches, so reading it linearly replays dead ones as real conversation.
    """
    by_uuid = {e["uuid"]: e for e in events if isinstance(e.get("uuid"), str)}
    ordered = [e for e in events if isinstance(e.get("uuid"), str)]
    if not ordered:
        return events, 0

    def walk(leaf):
        chain, seen, node = [], set(), leaf
        while node is not None and node.get("uuid") not in seen:
            seen.add(node.get("uuid"))
            chain.append(node)
            parent = node.get("parentUuid")
            if not parent:
                return chain[::-1]
            node = by_uuid.get(parent)
        return chain[::-1] if node is None else None

    if mode == "longest":
        parents = {e.get("parentUuid") for e in ordered}
        chains = [walk(e) for e in ordered if e.get("uuid") not in parents]
        chain = max((c for c in chains if c), key=len, default=None)
    else:
        chain = walk(ordered[-1])

    if chain is None:  # broken chain (compaction, partial file): keep file order
        return events, 0
    return chain, len(ordered) - len(chain)


def subagent_map(events):
    """Agent/Task tool_use_id -> (description, summary).

    Synchronous agents return the report as the tool_result. Background agents
    return only a launch stub naming an internal agentId; the real report arrives
    in a later <task-notification> and is spooled to a file that is deleted when
    the session ends. Never emit the agentId.
    """
    calls, results, spools = {}, {}, {}
    for ev in events:
        content = (ev.get("message") or {}).get("content")
        if ev.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Task", "Agent"):
                    inp = b.get("input") or {}
                    calls[b.get("id")] = str(inp.get("description") or b.get("name")).strip()
        if ev.get("type") != "user":
            continue
        if isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    raw = b.get("content", "")
                    if isinstance(raw, list):
                        raw = "\n".join(x.get("text", "") for x in raw if isinstance(x, dict))
                    results[b.get("tool_use_id")] = raw if isinstance(raw, str) else ""
        for text in texts(content):
            tid = TOOL_USE_ID.search(text) if "<task-notification>" in text else None
            if tid:
                out = OUTPUT_FILE.search(text)
                spools[tid.group(1).strip()] = out.group(1).strip() if out else ""

    out = {}
    for tid, desc in calls.items():
        summary = results.get(tid, "")
        if not summary or LAUNCH_STUB in summary:
            path = spools.get(tid, "")
            summary = ""
            if path and os.path.isfile(path):
                try:
                    with open(path, encoding="utf-8", errors="replace") as f:
                        summary = f.read()
                except OSError:
                    summary = ""
        out[tid] = (desc, USAGE.sub("", AGENT_ID.sub("", summary)).strip())
    return out


def render(events, title, mode):
    live, pruned = branch(events, mode)
    subs = subagent_map(live)
    lines = [f"# {title}", ""]
    n = {"user": 0, "agent": 0, "sub": 0, "nosub": 0, "plumbing": 0, "meta": 0}

    for ev in live:
        content = (ev.get("message") or {}).get("content")
        if ev.get("isSidechain"):
            continue

        if ev.get("type") == "user":
            if ev.get("isMeta"):
                n["meta"] += 1
                continue
            parts = [p for p in (clean(t) for t in texts(content)) if p]
            if isinstance(content, list) and any(
                isinstance(b, dict) and b.get("type") == "image" for b in content
            ):
                parts.append("*[image attached]*")
            if not parts:
                n["plumbing"] += 1 if texts(content) else 0
                continue
            n["user"] += 1
            lines += ["---", ""]
            lines += [f"> {ln}" if ln else ">" for ln in "\n\n".join(parts).split("\n")]
            lines.append("")

        elif ev.get("type") == "assistant" and isinstance(content, list):
            body = [b["text"] for b in content if b.get("type") == "text" and b.get("text", "").strip()]
            if body:
                n["agent"] += 1
                lines += ["\n".join(body), ""]
            for b in content:
                if b.get("type") != "tool_use" or b.get("id") not in subs:
                    continue
                desc, summary = subs[b["id"]]
                if summary:
                    n["sub"] += 1
                    lines += [f"*[Subagent: {desc}]*", "", summary, ""]
                else:
                    n["nosub"] += 1
                    lines += [f"*[Subagent: {desc} - no summary available]*", ""]

    return "\n".join(lines + ["---", ""]), n, pruned, len(live)


def main():
    argv = sys.argv[1:]
    force = "--force" in argv
    mode = "live"
    if "--branch" in argv:
        i = argv.index("--branch")
        mode = argv[i + 1] if i + 1 < len(argv) else ""
        if mode not in ("live", "longest"):
            die("--branch must be 'live' or 'longest'")
        del argv[i : i + 2]
    args = [a for a in argv if not a.startswith("--")]
    uuid = args[0] if args else None
    output_path = args[1] if len(args) > 1 else None

    root = os.path.expanduser("~/.claude/projects")
    if not os.path.isdir(root):
        die(f"Claude Code projects directory not found at {root}")
    if uuid:
        found = globmod.glob(os.path.join(root, "*", f"{uuid}.jsonl"))
        if not found:
            die(f"Session file not found for UUID '{uuid}'")
        session_path = found[0]
    else:
        found = globmod.glob(os.path.join(root, "*", "*.jsonl"))
        if not found:
            die("No session files found")
        session_path = max(found, key=os.path.getmtime)

    events, bad = [], 0
    with open(session_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    bad += 1
    if not events:
        die(f"No events found in {session_path}")

    title = next(
        (e["aiTitle"].strip() for e in reversed(events)
         if e.get("type") == "ai-title" and (e.get("aiTitle") or "").strip()),
        None,
    )
    if not title:
        first = next(
            (c for e in branch(events, mode)[0] if e.get("type") == "user" and not e.get("isMeta")
             for c in (clean(t) for t in texts((e.get("message") or {}).get("content"))) if c),
            "",
        )
        title = " ".join(first.split()[:6]) or "Untitled Chat"

    markdown, n, pruned, kept = render(events, title, mode)
    if not n["user"] and not n["agent"]:
        die(f"No conversation content found in {session_path}")

    if output_path is None:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "untitled"
        output_path = f"chatlight-{slug}.md"
    if os.path.exists(output_path) and not force:
        die(f"{output_path} already exists (use --force to overwrite)")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    # Report losses. Silent truncation reads as "exported everything".
    print(f"Exported: {title} -> {output_path}", file=sys.stderr)
    print(f"  {n['user']} user, {n['agent']} agent, {n['sub']} subagent summaries", file=sys.stderr)
    skipped = [
        f"{v} {k}" for k, v in (
            ("abandoned-branch events", pruned), ("injected/system messages", n["plumbing"]),
            ("meta events", n["meta"]), ("unavailable subagent reports", n["nosub"]),
            ("unparseable lines", bad),
        ) if v
    ]
    if skipped:
        print("  skipped: " + ", ".join(skipped), file=sys.stderr)
    if mode == "live" and pruned > kept:
        print(
            f"  WARNING: skipped more events ({pruned}) than exported ({kept}); this session "
            f"was rewound. Re-run with --branch longest for the fuller branch.",
            file=sys.stderr,
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
```
</python>
