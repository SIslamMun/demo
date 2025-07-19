Output baseline_1.mp4
Require claude
Set Theme "Catppuccin Frappe"
Set Width 1200
Set Height 1200
Set Shell bash
Set TypingSpeed 25ms

Sleep 500ms

Type "iowarp mcp add slurm -- uv run --with 'git+https://github.com/iowarp/scientific-mcps#subdirectory=Slurm' slurm-mcp"
Sleep 500ms
Enter
Sleep 100ms

Type "iowarp mcp add hardware -- uv run --with 'git+https://github.com/iowarp/scientific-mcps#subdirectory=Node_Hardware' node-hardware-mcp"
Sleep 500ms
Enter
Sleep 100ms

Type "iowarp mcp add lmod -- uv run --with 'git+https://github.com/iowarp/scientific-mcps#subdirectory=lmod' lmod-mcp"
Sleep 500ms
Enter
Sleep 100ms

Type "iowarp mcp add adios -- uv run --with 'git+https://github.com/iowarp/scientific-mcps#subdirectory=Adios' adios-mcp"
Sleep 500ms
Enter
Sleep 100ms

Type "iowarp mcp add arxiv -- uv run --with 'git+https://github.com/iowarp/scientific-mcps#subdirectory=Arxiv' arxiv-mcp"
Sleep 500ms
Enter
Sleep 100ms

Type "iowarp mcp add pandas -- uv run --with 'git+https://github.com/iowarp/scientific-mcps#subdirectory=Pandas' pandas-mcp"
Sleep 500ms
Enter
Sleep 100ms

Type "iowarp mcp add slurm -- uv run --with 'git+https://github.com/iowarp/scientific-mcps#subdirectory=Slurm' slurm-mcp"
Sleep 500ms
Enter
Sleep 100ms

Type "iowarp mcp add jarvis -- uv run --with 'git+https://github.com/iowarp/scientific-mcps#subdirectory=Jarvis' jarvis-mcp"
Sleep 500ms
Enter
Sleep 100ms

Set TypingSpeed 50ms

Type "iowarp --dangerously-skip-permissions"
Sleep 1s

Hide
Enter
Sleep 1s
Type "/clear"
Sleep 500ms
Enter
Show
Sleep 1s

Type "Hello. Who are you?"
Enter

Wait+Screen@60s /DONE/

Type "/clear"
Sleep 500ms
Enter
