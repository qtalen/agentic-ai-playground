This directory contains the source code for my latest article: [Build Long-Term and Short-Term Memory for Agents Using RedisVL](https://www.dataleadsfuture.com/build-long-term-and-short-term-memory-for-agents-using-redisvl/).

First, you'll need to install some dependencies from the root directory. Since I'm using the Microsoft Agent Framework, you have to install the pre-release version:

```shell
cd ..
uv sync --prerelease=allow
```

If you'd like to use an OpenAI-compatible embedding model deployed on a server, you'll also need to update your `.env` file by adding the following keys:

* `EMBEDDING_MODEL`: the name of the model you want to use  
* `EMBEDDING_API_KEY`: your API key  
* `EMBEDDING_ENDPOINT`: the base URL of the model  

After that, go back into the `12_RedisVL_Long_Short_Memory` folder. Here's what each file does:

* `redisvl_message_store.py`: implements short-term memory using RedisVL's `MessageHistory`  
* `test_message_store.py`: tests this short-term memory  
* `redisvl_semantic_memory.py`: implements long-term memory using RedisVL's `SemanticMessageHistory`  
* `test_semantic_memory.py`: tests this long-term memory