This repository contains the source code for the article [I Used Autogen GraphFlow and Qwen3 Coder to Solve Math Problems — And It Worked](https://www.dataleadsfuture.com/i-used-autogen-graphflow-and-qwen3-coder-to-solve-math-problems-and-it-worked/).

To run this project, you should first install the dependencies:

```shell
cd ..
uv sync --prerelease=allow
```

Next, create a `.env` file to store your LLM's API settings.

This project uses a Docker-based Python runtime environment, so you'll also need to build an image named `python-docker-env`:

```shell
cd 06_Super_Teacher_Workflow
cd docker_executor
docker build -t python-docker-env .
```

The project uses MLflow to trace how the LLM is being called. You need to install and start MLflow:
```shell
mlflow server --host 127.0.0.1 --port 8080
```

Add the following line to your `.env` file:
```text
MLFLOW_TRACKING_URI=http://localhost:5000/
```

Once everything is set up, you can use Chainlit to launch your user interface:
```shell
cd 06_Super_Teacher_Workflow
chainlit run app.py
```