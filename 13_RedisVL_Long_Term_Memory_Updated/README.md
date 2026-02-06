This is the code repository for my article: [Advanced RedisVL Long-term Memory Tutorial: Using an LLM to Extract Memories](https://www.dataleadsfuture.com/advanced-redisvl-long-term-memory-tutorial-using-an-llm-to-extract-memories/).

Before you begin, please update the project dependencies:

```shell
cd ..
uv sync --prerelease=allow
```

Then go back to the `13_RedisVL_Long_Term_Memory_Updated` folder and run:

```shell
python test_long_term_memory.py
```

That’s it—you’ll be able to chat with an agent that has long-term memory.

Here’s a quick overview of the files:

* `prompt.md`: The prompt used by the agent to extract memories.  
* `redisvl_long_term_memory.py`: Implementation of the `ContextProvider` for long-term memory.  
* `test_long_term_memory.py`: Test script.