# 📄 Claude Paper Reader

> AI 驱动的论文阅读助手——基于 Claude Code，自动下载、阅读、总结、对比学术论文。

你只需要给一个 arXiv 链接，Claude 自动完成：下载 PDF → 提取文本 → 生成中文结构化总结 → 多论文对比分析。特别适合需要密集阅读论文的研究者。

## 快速开始（30 秒上手）

```bash
# 1. 安装 Claude Code（如果还没装）
npm install -g @anthropic-ai/claude-code

# 2. Clone 本项目
git clone https://github.com/<your-username>/claude-paper-reader.git
cd claude-paper-reader

# 3. 启动 Claude Code（在项目目录下）
claude
```

然后在 Claude Code 的对话框中输入：

```
读一下这篇论文 https://arxiv.org/pdf/2002.05709
```

Claude 会自动下载、提取文本、生成结构化的中文总结。就是这么简单。

## 这个项目是什么？

阅读学术论文是研究者的日常，但真正"读懂"一篇论文——理清方法流程、与前人工作对比、形成自己的理解——需要大量心力。

Claude Paper Reader 把论文阅读流程**技能化**，封装成 5 个 Claude Code Skill：

```
你贴一个 arXiv 链接
        │
        ▼
  paper-reader      ← 自动下载 PDF + 提取全文
        │
        ▼
  paper-analyst     ← 生成结构化中文总结（方法流程逐步拆解）
        │
        ▼
  paper-customize   ← 按你的阅读视角定制总结
        │
        ▼
  paper-contrast    ← 多论文对比分析
```

每一步的结果都保存为 `.md` 文件，你可以反复查阅、修改、分享。

## 前提条件

| 依赖 | 安装方式 |
|------|----------|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` |
| **Python 3.9+** | 已有即可 |
| **requests** | `pip install requests`（或 `pip install -e .`） |

> **关于 API Key**：使用 Claude Code 需要有 Anthropic API Key 或其他 LLM provider 的 API Key。详见 [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code)。

## 可用技能一览

### 1. `paper-reader` — 下载 + 提取原文

```bash
# 直接在对话中说：
读一下这篇论文 https://arxiv.org/abs/2306.12495
```

自动下载 PDF 到 `src/tmp/`，提取全文文本，原样输出给下游技能。

### 2. `paper-analyst` — 深度总结

接收论文原文，生成结构化的中文总结：
- 基本信息（作者、时间、刊物）
- 面向的问题与提出的方法
- 方法流程逐步拆解（数据集 → 前处理 → 前向 → 反向 → 后处理）

总结保存到 `src/items/<theme>/paper_<id>.md`。

### 3. `paper-customize` — 个性化阅读视角

为每篇论文建立自定义"阅读视角"。例如：
- 对比学习中，你关注"实例级 vs 像素级"的差异
- 扩散模型中，你关注"空查询"机制

视角文件保存为 `.per.md`，可以不断积累和复用。

### 4. `paper-contrast` — 多论文对比

在同一主题下对多篇论文进行横向对比，自动更新 `Comparative.md` 和 `Metrics.md`。

### 5. `paper-process-skill` — 一键全流程

集成以上四个步骤，粘贴链接即可完成从下载到对比的全流程。

## 高级用法

### 自定义阅读视角

```
帮我对这篇论文建立一个"实例级对比学习 vs 像素级对比学习"的阅读视角
```

Claude 会交互式地询问你关注的对比维度，生成专属的透视文件。

### 批量对比

```
对比 src/items/contrastive-learning/ 下的所有论文
```

### 修改已有总结（保留原文，追加修改）

```
根据这篇新论文的创新点，修改原有的 SimCLR 总结
```

新修改内容以引用条形式追加，不会覆盖原文。

## 项目结构

```
claude-paper-reader/
├── .claude/
│   ├── skills/          # 5 个论文处理 skill
│   │   ├── paper-reader/     # 下载 + 提取
│   │   ├── paper-analyst/    # 深度总结
│   │   ├── paper-customize/  # 个性化视角
│   │   ├── paper-contrast/   # 多论文对比
│   │   └── paper-process-skill/  # 全流程
│   ├── rules/           # 写作规范
│   └── agents/          # 比较分析 agent
├── src/
│   ├── tmp/             # 临时下载的论文（不提交 git）
│   └── items/           # 论文总结 + 对比 + 透视文件
├── tests/               # 测试
├── pyproject.toml
└── README.md
```

## 常见问题

### Q: 我需要有编程基础吗？

基本的命令行操作即可。会 `cd` 和粘贴链接就够了。

### Q: 支持哪些论文来源？

目前支持 arXiv（`arxiv.org/abs/...` 或 `arxiv.org/pdf/...`）和直接的 PDF 链接。

### Q: 总结保存在哪里？

保存在 `src/items/<主题名称>/paper_<论文id>.md`，是纯 Markdown 文件，可以用任何编辑器打开。

### Q: 如何处理中文论文？

系统默认使用中文生成总结。英文论文的原文会被提取为英文，但总结为中文。

### Q: API 费用贵吗？

每次读一篇论文约消耗几万到十几万 tokens，具体取决于论文长度。对个人研究者来说成本很低。建议使用 Claude Sonnet 模型以平衡质量与成本。

### Q: 如何反馈问题或建议？

见 [CONTRIBUTING.md](./CONTRIBUTING.md)，或直接提 GitHub Issue。

## 贡献

欢迎通过以下方式参与：
- **提 Issue**：报告 bug、建议新功能、反馈使用体验
- **提 PR**：改进 skill、修复问题、添加新功能
- **分享你的阅读视角**：如果你为某个主题建立了好的阅读视角，欢迎分享

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## License

MIT License — 详见 [LICENSE](./LICENSE)。
