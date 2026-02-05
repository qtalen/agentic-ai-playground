This repository contains the source code for the article [Monitoring Qwen 3 Agents with MLflow 3.x: End-to-End Tracking Tutorial](https://www.dataleadsfuture.com/monitoring-qwen-3-agents-with-mlflow-3-x-end-to-end-tracking-tutorial/).

To test-run this code, you'll need to install the dependencies first:

```shell
cd ..
uv sync --prerelease=allow
```

Description of the source files:
* `/utils/autogen_patching.py`: Monkey patch for MLflow ChatMessage to fix Autogen autolog bugs.
* `01_basic_setup.py`: Basic usage based on annotations.
* `02_openai_autolog.py`: How to use OpenAI autolog.
* `03_tracing_stream_output.py`: How to trace LLM's streaming output.
* `04_function_calling_with_context_manager.py`: Using MLflow's context manager to record additional information.
* `05_autogen_agent_integration.py`: Using MLflow in Autogen applications with autolog bug fixes.
* `06_autogen_workflow_tracing.py`: Practical project implementation of using MLflow in Autogen GraphFlow.

