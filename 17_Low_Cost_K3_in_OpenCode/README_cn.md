这个仓库是我的最新文章[How I Cut Kimi K3 Costs in OpenCode](https://www.dataleadsfuture.com/how-i-cut-kimi-k3-costs-in-opencode/)的源码。

使用方法：
1. 从[Novita.ai](https://novita.ai/?ref=n2fjmjk&utm_source=affiliate)获取你的API Key，并填入到OpenCode上Novita供应商的API KEY输入框里。
2. 将`executor.md`和`architect.md`存放到你的电脑上的`~/.config/opencode/agents/`目录。
3. 如果你的OpenCode不能根据场景自动调用这两个智能体，你可以往你的`~/.config/opencode/AGENTS.md`里写入以下指令：
    ```Markdown
    规划与研究完成后，实施类工作（编码、文件编辑）优先委派 executor 子智能体；无依赖的任务并发委派（不超过5个）；界面层开发（Web 前端、Electron、PySide/PyQt 等桌面应用，以及 Chainlit、Gradio、Streamlit、Reflex、Dash 等 Python 界面框架）除外；单文件少于10行的小改动直接自己完成。
   
    遇到难以独立解决的复杂问题（架构决策、疑难 bug 根因、重大方案权衡），委派 architect 子智能体深度推理，任务说明中必须包含完整背景（问题描述、相关代码位置、已排除的假设、已尝试的方案）。疑难 bug 须先自行完成至少两轮独立假设的验证仍无法定位，才可委派。
    ```
4. 最后，调整`~/.config/opencode/opencode.json`文件里，对`explore`和`general`智能体的模型配置：
   ```json
    {
      "$schema": "https://opencode.ai/config.json",
      "agent": {
        "explore": {
          "model": "novita-ai/deepseek/deepseek-v4-flash"
        },
        "general": {
          "model": "novita-ai/deepseek/deepseek-v4-pro"
        }
      }
    }
   ```
   
开始享用。