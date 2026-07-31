This repository contains the source code for my latest article, [How I Cut Kimi K3 Costs in OpenCode](https://www.dataleadsfuture.com/how-i-cut-kimi-k3-costs-in-opencode/).

How to use:
1. Get your API key from [Novita.ai](https://novita.ai/?ref=n2fjmjk&utm_source=affiliate) and paste it into the API KEY field for the Novita provider in OpenCode.
2. Place `executor.md` and `architect.md` into the `~/.config/opencode/agents/` directory on your computer.
3. If your OpenCode does not automatically invoke these two agents based on context, add the following instructions to your `~/.config/opencode/AGENTS.md`:
    ```Markdown
    After planning and research are complete, delegate implementation work (coding, file editing) to the executor subagent first; delegate independent tasks concurrently (no more than 5); exclude UI-layer development (web frontends; desktop apps such as Electron, PySide/PyQt; and Python UI frameworks such as Chainlit, Gradio, Streamlit, Reflex, Dash); handle small changes under 10 lines in a single file yourself.
   
    For complex problems that are hard to solve independently (architecture decisions, root causes of tricky bugs, major trade-off decisions), delegate to the architect subagent for deep reasoning. The task brief must include full context (problem description, relevant code locations, ruled-out hypotheses, attempted solutions). For tricky bugs, you must first verify at least two independent hypotheses without locating the cause before delegating.
    ```
4. Finally, adjust the model configuration for the `explore` and `general` agents in your `~/.config/opencode/opencode.json` file:
   ```json
    {
      "$schema": "https://opencode.ai/config.json",
      "agent": {
        "explore": {
          "model": "novita-ai/deepseek/deepseek-v4-flash"
        },
        "general": {
          "model": "novita-ai/deepseek/deepseek-v4-pro"
        }
      }
    }
   ```
   
Enjoy.
