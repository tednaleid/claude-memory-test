Run `git rev-parse --show-toplevel` to find the repo root,
then determine the relative path from the current working
directory back to that root. Respond with only this exact
format, nothing else: root is <relative-path>

For example, if cwd is the repo root: "root is ."
If cwd is one level deep: "root is .."
If cwd is two levels deep: "root is ../.."