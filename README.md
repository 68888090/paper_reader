# 📄 Claude Paper Reader

> AI 驱动的论文阅读助手——基于 Claude Code，自动下载、阅读、总结、对比学术论文。

你只需要给一个 arXiv 链接，Claude 自动完成：下载 PDF → 提取文本 → 生成中文结构化总结 → 多论文对比分析。特别适合需要密集阅读论文的研究者。

## 快速开始（30 秒上手）

```bash
# 1. 安装 Claude Code（如果还没装）
npm install -g @anthropic-ai/claude-code

# 2. Clone 本项目
git clone https://github.com/68888090/paper_reader.git
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

## 对比阅读：这个项目的独特之处

大多数论文阅读工具只能帮你**读懂一篇**论文。Claude Paper Reader 的核心特色在于**对比阅读**——让你在多篇论文之间建立联系、找到差异、形成自己的判断。

### 对比阅读的完整流程

假设你在研究"对比学习"方向，想弄清楚"实例级优化"和"像素级优化"的本质区别：

**第一步：分别读两篇论文**

```
读一下这篇论文 https://arxiv.org/pdf/2002.05709   # SimCLR（实例级）
读一下这篇论文 https://arxiv.org/pdf/2011.09157   # DenseCL（像素级）
```

每篇都会生成结构化的中文总结，保存到 `src/items/contrastive-learning/` 下。

**第二步：建立对比视角**

```
帮我对这两篇论文建立一个"实例级 vs 像素级对比学习"的阅读视角
```

Claude 会交互式地询问你关注的对比维度（如对比单元、正负样本定义、特征提取架构、下游任务适配），然后生成一份**透视文件（`.per.md`）**。

透视文件的核心是**按维度分表对比**，而非泛泛的"A 方法好还是 B 方法好"：

| 维度 | 实例级（SimCLR） | 像素级（DenseCL） |
|------|-----------------|-------------------|
| 对比的基本单元 | 整张图片 → 1个全局向量 | 特征图每空间位置 → $S_h \times S_w$ 个局部向量 |
| 正样本定义 | 同图两视图的全局表示 | 同图两视图对应空间位置的局部表示 |
| 架构关键 | AvgPool 消除空间信息 | $1 \times 1$ 卷积保持空间分辨率 |
| 下游任务 | 图像分类 | 目标检测、语义分割 |

每个维度的对比都附带**判断推理**，告诉你这个差异意味着什么、为什么重要。

**第三步：更新对比总表**

```
把这次对比的结果更新到 Comparative.md
```

`Comparative.md` 是你在这个主题下所有论文对比的汇总索引。随着阅读论文数量的增加，它会自动累积成一份完整的领域对比图谱。

**第四步：用新论文修正旧理解**

```
根据 DenseCL 的创新点，修改原有的 SimCLR 总结
```

修改不会覆盖原文——新内容以**引用条**形式追加在对应文字下方，保留修改痕迹，方便回溯。

### 文件体系——你的阅读成果随时间累积

```
src/items/contrastive-learning/
├── SimCLR_Instance_Contrastive_Learning.md    # 论文 A 总结
├── DenseCL_Pixel_Contrastive_Learning.md      # 论文 B 总结
├── instance_vs_pixel_level.per.md            # 你的对比透视文件
├── Comparative.md                            # 所有论文的对比总表
├── Metrics.md                                # 关键指标汇总
└── README.md                                 # 主题说明
```

每篇新论文不是孤立的文件，而是**织入你已有知识网络的一条新线**。

## 高级用法

### 自定义阅读视角

```
帮我对这篇论文建立一个"实例级对比学习 vs 像素级对比学习"的阅读视角
```

Claude 会交互式地询问你关注的对比维度，生成专属的透视文件。视角可以复用——下次读同类论文时直接套用。

### 批量对比

```
对比 src/items/contrastive-learning/ 下的所有论文
```

### 修改已有总结（原文保留，追加修改）

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
