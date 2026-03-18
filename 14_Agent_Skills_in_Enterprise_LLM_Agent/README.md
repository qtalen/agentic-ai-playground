Here's the code repo for my article [How to Use Agent Skills in Enterprise LLM Agent Systems](https://www.dataleadsfuture.com/how-to-use-agent-skills-in-enterprise-llm-agent-systems/).

Before you get started, update your project dependencies:

```shell
cd ..
git checkout v0.14.1
uv sync --prerelease=allow
```

Head back to the `14_Agent_Skills_in_Enterprise_LLM_Agent` directory and build the image first:

```shell
cd containers
docker build -t python-code-sandbox .
```

You don't need to run the container manually. The code will spin it up from the image automatically when needed.

Once everything is ready, you can run `agent_skills.py`:

```shell
uv run python agent_skills.py
```

If you run into any errors related to "port 5000", that's because you don't have an MLFlow server running. Just comment out the `mlflow_log()` code and you're good to go.