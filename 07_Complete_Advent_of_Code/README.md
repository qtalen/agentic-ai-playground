This repository contains the source code for my article [How I Crushed Advent of Code And Solved Hard Problems Using Autogen Jupyter Executor and Qwen3](https://www.dataleadsfuture.com/how-i-crushed-advent-of-code-and-solved-hard-problems-using-autogen-jupyter-executor-and-qwen3/).

To run this project, you should first install the project and its dependencies:

```shell
cd ..
pip install --upgrade -e .
```

Next, create a `.env` file and add your LLM API settings.

As mentioned in the article, before running the project, you also need to create a Jupyter server image:

```shell
cd 07_Complete_Advent_of_Code
cd jupyter-server
docker build -t jupyter-server .
```

Once everything is set up, you can run your project using Chainlit:
```shell
cd ..
chainlit run app.py
```