This repo has the source code for my article: [Exclusive Reveal: Code Sandbox Tech Behind Manus and Claude Agent Skills](https://www.dataleadsfuture.com/exclusive-reveal-code-sandbox-tech-behind-manus-and-claude-agent-skills/).

First, go to the project root and install the dependencies:

```shell
cd ..
pip install --upgrade -e .
```

Then, create a `.env` file in the root folder and put your LLM settings in it. You can check the `.env.example` file for reference.

In the article, we need to make a `jupyter-sever` image. The `Dockerfile` is in `09_Reveal_Jupyter_Code_Executor/jupyter-server`. You can build it like this:

```shell
cd 09_Decrypt_Jupyter_Code_Executor
cd jupyter-server

docker build -t jupyter-server .
```

After that, you can try out the example code.

* `docker-compose.yml` — use Docker Compose to start and stop the jupyter-server.
* `code_executor.py` — shows how to use Autogen’s `CodeExecutorAgent` to send code to Jupyter to run.
* `task_planner.py` — the task planner role in a multi-agent app.
* `code_writer.py` — writes Python code snippets based on sub-tasks.
* `app.py` — the main entry for the multi-agent app, uses `RoundRobinGroupChat` to run Python sub-tasks one by one.
* `langchain_with_jupyter_executor.py` — shows how to connect LangChain to the Jupyter Server using Function Calling.