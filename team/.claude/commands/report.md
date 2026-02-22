Return ONLY a JSON object with these exact keys (no markdown, no code fences, just raw JSON):

- name: from your CLAUDE.md context
- team_name: from your CLAUDE.md context
- favorite_color: from your CLAUDE.md context
- favorite_movie: from your CLAUDE.md context
- temperature: from your CLAUDE.md context
- team_script_output: run `$(git rev-parse --show-toplevel)/team/team-info.py` and include its stdout verbatim
- level: respond with exactly what the /level command specifies
- rootpath: run `git rev-parse --show-toplevel`, compute the relative path from CWD back to that root, and respond in the format "root is <relative-path>" (e.g. "root is ." at root, "root is .." one level deep)
