#daily-news-bot 

### 项目简介
**daily-news-bot** 是一个集成 DeepSeek 大模型与 GitHub Actions 的自动化工具，专注于全天候追踪并提炼全球 AI 与水文科学交叉领域的前沿科研情报与行业动态。

本项目它旨在解决科研过程中“信息过载”与“追踪不及时”的问题，帮助关注 AI4S（AI for Science）的同学快速锁定有价值的论文和技术进展。

> **主要内容（持续更新中）：**
> * **自动化巡逻**：每日定时抓取 Arxiv, Nature, OpenAI, 机器之心等 10+ 权威数据源。
> * **智能语义提炼**：利用 DeepSeek-V3 对海量素材（如 LSTM, 径流预报等）进行去重与深度摘要。
> * **Notion 集成**：自动将每周汇总的情报同步至 Notion 协作空间。

---

### 配置运行步骤

本项目基于 **GitHub Actions** 运行，无需本地开机

#### 1. 准备工作
在使用本项目前，请确保已经拥有以下权限：
* **DeepSeek API Key**：前往 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取。
* **Notion 机器人**：在 [Notion Developers](https://www.notion.so/my-integrations) 创建一个 Internal Integration，并将其“Invite”到你的目标 Database 页面。

#### 2. 配置仓库环境变量（Secrets）
由于本项目在云端自动运行，需要将隐私密钥告知 GitHub：
1. 进入 `iheadwater/daily-news-bot` 仓库页面，点击右上角的 **Settings**。
2. 在左侧栏找到 **Secrets and variables** -> **Actions**。
3. 点击 **New repository secret**，依次添加以下三个变量：
   * `DEEPSEEK_API_KEY`: 填入 DeepSeek API Key。
   * `NOTION_TOKEN`: 填入 Notion 机器人的 Internal Integration Token。
   * `NOTION_DATABASE_ID`: 填入 Notion 数据库的 ID。

#### 3. 手动触发测试
配置完成后，可以立即测试系统是否连通：
1. 点击项目上方的 **Actions** 选项卡。
2. 在左侧选择 **Daily News Scraper**。
3. 点击右侧的 **Run workflow** 按钮。
4. 观察运行日志，如果出现 `📡 正在向 DeepSeek 发送真实情报...` 且显示绿色对勾，说明配置成功！

---

### 注意事项

* **关键词调整**：如果希望关注更具体的领域（如：Physics-informed, Transformer），可以修改 `scraper.py` 中的 `KEYWORDS` 列表。
* **安全性提示**：**切勿**将 API Key 直接写在代码中提交，必须通过上述 GitHub Secrets 方式配置。
* **费用说明**：DeepSeek API 运行成本极低，正常运行一个月大约仅消耗 1-2 元人民币，请确保账户余额充足。

