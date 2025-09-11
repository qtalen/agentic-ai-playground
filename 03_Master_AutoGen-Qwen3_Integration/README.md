This repository contains the source code for the article [Build AutoGen Agents with Qwen3: Structured Output & Thinking Mode](https://www.dataleadsfuture.com/build-autogen-agents-with-qwen3-structured-output-thinking-mode/).

To test this code, you'll need to install the dependencies first:

```shell
cd ..
pip install -e .
```

--------------------------------

Source file descriptions:
* `/utils/openai_link.py`: The OpenAI-like client we implemented this time.
* `01_openai_like_client.py`: How to use the OpenAI-like client to connect to Qwen3.
* `02_structured_output.py`: Several methods to implement structured_output.
* `03_thinking_mode.py`: Ways to enable/disable Qwen3's thinking mode.
* `04_structured_output_practice.py`: Source code for the practice project.