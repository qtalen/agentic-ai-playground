This repository contains the source code for the article [Use LLamaIndex Workflow to Create an Ink Painting Style Image Generation Workflow](https://www.dataleadsfuture.com/use-llamaindex-workflow-to-create-an-ink-painting-style-image-generation-workflow/).

To run this code, first install the dependencies:

```shell
cd ..
uv sync --prerelease=allow
```

Next, create a `.env_deepseek` file to store the LLM API settings.

Since this project uses both DeepSeek and OpenAI APIs, you'll need to set up two API keys:

```shell
OPENAI_API_KEY=<your deepseek api key>
OPENAI_API_BASE=<deepseek base url>
REAL_OPENAI_API_KEY=<your openai api key>
REAL_OPENAI_API_BASE=<openai base url>
```

Once everything's ready, run the chainlit interactive interface with this command:

```shell
cd 05_Image_Generation_Workflow
chainlit run app.py
```