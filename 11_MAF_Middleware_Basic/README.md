This folder contains the source code for my latest article: [Microsoft Agent Framework (MAF) Middleware Basics: Add Compliance Fences to Your Agent](https://www.dataleadsfuture.com/microsoft-agent-framework-maf-middleware-basics-add-compliance-fences-to-your-agent/)  

You’ll need to install the project dependencies from the root directory first:  

```shell
cd ..
uv sync --prerelease=allow
```  

You’ll also need to create a `.env` file in the root directory to store your LLM API key and base URL.  

Once everything’s set up, you can follow these steps to try out the sample code:  

1. Run `server.py` first. This will start the server side of AG-UI and provide compliance review services.  
2. Then run `compliance_check.py`. It will launch an interactive session in the terminal so you can give it a try.  
3. `credit_usage_check.py` shows how I use middleware to calculate the remaining credit points for users when they use the agent, and you can use it for reference too.  