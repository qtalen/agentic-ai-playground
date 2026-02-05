The directory contains the sample code for my article: [Make Microsoft Agent Framework’s Structured Output Work With Qwen and DeepSeek Models](https://www.dataleadsfuture.com/make-microsoft-agent-frameworks-structured-output-work-with-qwen-and-deepseek-models/)

This article covers an extension to the Microsoft Agent Framework, and the actual code lives in the `common/agent_framework` folder.

To run the examples, first install the dependencies from the root directory:

```shell
cd ..
uv sync --prerelease=allow
```

You’ll also need to create a `.env` file in the root directory and add your Qwen or DeepSeek LLM configuration there.

If you want to follow along with the article’s instructions using `mlflow`, add this line to your `.env` file too:  
`MLFLOW_TRACKING_URI=http://localhost:5000/`

Once everything’s set up, you’re ready to test the sample code:

* `01_structured_output.py` – tests structured output in a single-turn conversation.  
* `02_multi_turn_conversations.py` – tests multi-turn conversations and tries setting `response_format` in different positions.