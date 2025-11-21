这个仓库包含了我的这篇文章的源码:[Exclusive Reveal: Code Sandbox Tech Behind Manus and Claude Agent Skills](https://www.dataleadsfuture.com/exclusive-reveal-code-sandbox-tech-behind-manus-and-claude-agent-skills/)

你应该首先去项目根目录安装依赖：

```shell
cd ..
pip install --upgrade -e .
```

然后，在根目录下创建一个`.env`文件然后把你的LLM配置放进去，可以参考`.env.example`文件。

在文章里，我们要创建一个`jupyter-sever`镜像，`Dockerfile`已放在`09_Reveal_Jupyter_Code_Executor/jupyter-server`了。你可以执行以下操作来构建镜像。

```shell
cd 09_Decrypt_Jupyter_Code_Executor
cd jupyter-server

docker build -t jupyter-server .
```

然后你就可以测试示例代码了。

* `docker-compose.yml`你可以利用Docker Compose来管理jupyter-server的启动和停止。
* `code_executor.py`演示了如何使用Autogen的`CodeExecutorAgent`将代码提交到Jupyter去执行。
* `task_planner.py`是多智能体应用中的任务规划者角色。
* `code_writer.py`根据子任务来编写Python代码片段。
* `app.py`是多智能体应用的入口代码，使用`RoundRobinGroupChat`来迭代执行Python子任务。
* `langchain_with_jupyter_executor.py`演示了在LangChain中，如何利用Function Calling来连接Jupyter Server。