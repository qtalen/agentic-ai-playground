这个存储库是我的文章[How I Crushed Advent of Code And Solved Hard Problems Using Autogen Jupyter Executor and Qwen3](https://www.dataleadsfuture.com/how-i-crushed-advent-of-code-and-solved-hard-problems-using-autogen-jupyter-executor-and-qwen3/)的源码。

要运行这个项目，你应该先安装项目和相应的依赖：

```shell
cd ..
pip install --upgrade -e .
```

接下来，创建一个`.env`文件并存放你的大模型的API设置。

就如文章所言，在运行项目前，你还要创建一个jupyter server镜像：

```shell
cd 07_Complete_Advent_of_Code
cd jupyter-server
docker build -t jupyter-server .
```

当所有设置都配置完毕后，你可以使用Chainlit来运行你的项目了：
```shell
cd ..
chainlit run app.py
```