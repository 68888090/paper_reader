# 贡献指南

感谢你想为 Claude Paper Reader 做贡献！这个项目还很早期，任何形式的参与都很有价值。

## 反馈使用体验

你不一定要写代码才能贡献。最简单的贡献方式是：

### 提 Issue

- **Bug 报告**：哪个 skill 出了问题？输入了什么？预期和实际结果是什么？
- **功能建议**：缺什么功能？你想加什么？
- **使用体验**：哪里卡住了？哪里不好用？
- **论文总结质量**：生成的总结哪里不对或不够好？

### 分享你的阅读视角

如果你为某个研究方向建立了好的阅读视角（`.per.md`），欢迎分享出来，其他人可以直接复用。

提 Issue 时附上视角文件路径即可。

## 贡献代码

### 项目结构回顾

```
.claude/skills/       ← Claude Code skill 定义（SKILL.md）+ Python 脚本（scripts/）
.claude/rules/        ← 项目级规则（写作格式、修改规范等）
.claude/agents/       ← Claude Code 子 agent 定义
src/items/            ← 主题分类的论文总结 + 对比分析
```

### 添加新 Skill

1. 在 `.claude/skills/` 下新建文件夹
2. 写 `SKILL.md`（参考已有的 skill）
3. 如果需要 Python 脚本，放在 `scripts/` 下
4. 更新 README.md 的技能列表

### 改进现有 Skill

直接修改对应的 `SKILL.md` 或 `scripts/` 下的脚本即可。

### 开发环境

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

### 提 PR

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/your-feature`)
3. 提交改动 (`git commit -m 'Add something'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

## 行为准则

- 友善、尊重地交流
- 建设性地提反馈
- 包容不同背景和水平的使用者

## 联系方式

直接提 GitHub Issue 是最快的方式。
