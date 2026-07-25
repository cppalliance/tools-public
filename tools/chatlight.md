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

Detect which IDE is running:
- **Cursor**: The workspace has a `.cursor/` directory and state.vscdb exists at the platform-specific path
- **Claude Code**: The workspace has a `.claude/` directory and session JSONL files exist at `~/.claude/projects/`

Write only the matching `<python>` block's content to a .py file (strip the fence markers). Run it. File the output.

---

## Invocation

Accept 1-2 arguments:
1. **Chat UUID** (required) - the session to export. If omitted, use the most recent session (highest mtime)
2. **Output file path** (optional) - where to write the markdown. Default: derive from chat title

### Finding the current chat UUID

**Cursor:** List directories in `~/.cursor/projects/{project-slug}/agent-transcripts/`. Sort by mtime descending. The most recent directory name is the chat UUID. The project-slug derives from the workspace path by replacing path separators and colons with dashes (e.g. `c:\Users\Vinnie\src\cursor` becomes `c-Users-Vinnie-src-cursor`).

**Claude Code:** List `.jsonl` files in `~/.claude/projects/<sanitized-path>/`. Sort by mtime descending. The most recent filename (without `.jsonl`) is the session UUID. The sanitized path replaces `/` with `-` and URL-encodes special chars (e.g. `/home/user/myapp` becomes `-home-user-myapp`).

---

## Execution

1. Detect the platform
2. Extract the code from inside the matching `<python>` block - strip the opening and closing triple-backtick fence lines, write only the Python source to a scratch .py file
3. Run the script with the chat UUID and output path
4. Verify the first user message in the output matches what you see in the chat
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
- H1 heading with chat title at top (Cursor: `composerHeaders.name`; Claude Code: first 6 words of first user message)
- `---` before every user message (including the first)
- User text in blockquote (`> ` prefix on each line)
- One blank line between every element
- Subagent summaries prefixed with `*[Subagent: {description}]*` on a line alone, followed by blank line, then the summary text
- Agent text reproduced verbatim - preserve all markdown formatting
- No thinking content appears anywhere
- `---` after the final agent response (end-of-file marker)
- Empty text bubbles (text field is `""`) produce no output - skip silently

---

## Success Criteria

- The output contains every user message and every visible agent response from the session, in order
- No thinking text appears
- No tool-call metadata appears (except subagent summaries)
- The markdown renders cleanly in any viewer
- Before filing the output, confirm the first user message matches what you see in the chat

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
Usage: python chatlight_claude.py <session-uuid> <output-path>

Reads JSONL session file, walks events, writes clean markdown.
Exit 0 on success, 1 on failure.
"""
import sys
import os
import json
import glob as globmod

def main():
    if len(sys.argv) < 3:
        print("Usage: python chatlight_claude.py <session-uuid> <output-path>", file=sys.stderr)
        sys.exit(1)

    session_uuid = sys.argv[1]
    output_path = sys.argv[2]

    # Locate session file
    claude_dir = os.path.expanduser("~/.claude/projects")
    if not os.path.isdir(claude_dir):
        print(f"Error: Claude Code projects directory not found at {claude_dir}", file=sys.stderr)
        sys.exit(1)

    # Search all project dirs for the session UUID
    session_path = None
    for project_dir in globmod.glob(os.path.join(claude_dir, "*")):
        candidate = os.path.join(project_dir, f"{session_uuid}.jsonl")
        if os.path.isfile(candidate):
            session_path = candidate
            break

    if session_path is None:
        print(f"Error: Session file not found for UUID '{session_uuid}'", file=sys.stderr)
        sys.exit(1)

    # Read all events
    events = []
    with open(session_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not events:
        print(f"Error: No events found in session file", file=sys.stderr)
        sys.exit(1)

    # Derive title from first user message (first 6 words)
    chat_title = "Untitled Chat"
    for ev in events:
        if ev.get("type") == "user":
            msg = ev.get("message", {})
            content_blocks = msg.get("content", [])
            for block in content_blocks:
                if block.get("type") == "text":
                    words = block["text"].split()[:6]
                    chat_title = " ".join(words)
                    break
            break

    lines = []
    lines.append(f"# {chat_title}")
    lines.append("")

    # Build tool_use_id -> subagent summary map
    tool_results = {}
    for ev in events:
        if ev.get("type") == "user":
            msg = ev.get("message", {})
            for block in msg.get("content", []):
                if block.get("type") == "tool_result":
                    tool_use_id = block.get("tool_use_id", "")
                    result_content = block.get("content", "")
                    if isinstance(result_content, list):
                        text_parts = [b.get("text", "") for b in result_content if b.get("type") == "text"]
                        result_content = "\n".join(text_parts)
                    tool_results[tool_use_id] = result_content

    for ev in events:
        ev_type = ev.get("type")

        if ev_type == "user":
            msg = ev.get("message", {})
            content_blocks = msg.get("content", [])
            user_text_parts = []
            for block in content_blocks:
                if block.get("type") == "text":
                    user_text_parts.append(block["text"])
            if user_text_parts:
                text = "\n".join(user_text_parts)
                lines.append("---")
                lines.append("")
                for line in text.split("\n"):
                    lines.append(f"> {line}")
                lines.append("")

        elif ev_type == "assistant":
            msg = ev.get("message", {})
            content_blocks = msg.get("content", [])
            text_parts = []
            subagent_calls = []

            for block in content_blocks:
                if block.get("type") == "text":
                    text_parts.append(block["text"])
                elif block.get("type") == "tool_use":
                    name = block.get("name", "")
                    if name in ("Task", "Agent"):
                        tool_id = block.get("id", "")
                        desc = block.get("input", {}).get("description", name)
                        summary = tool_results.get(tool_id, "")
                        subagent_calls.append((desc, summary))

            if text_parts:
                lines.append("\n".join(text_parts))
                lines.append("")

            for desc, summary in subagent_calls:
                if summary:
                    lines.append(f"*[Subagent: {desc}]*")
                    lines.append("")
                    lines.append(summary)
                    lines.append("")
                else:
                    lines.append(f"*[Subagent: {desc} - no summary available]*")
                    lines.append("")

    # End-of-file marker
    lines.append("---")
    lines.append("")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Exported: {chat_title} -> {output_path}")
    sys.exit(0)

if __name__ == "__main__":
    main()

```
</python>
