#!/usr/bin/env python3
"""Initialize user profile template for paper-reading-notes skill."""

import os
from datetime import date

PROFILES_DIR = "src/profiles"
PROFILE_FILE = os.path.join(PROFILES_DIR, "user_profile.md")

TEMPLATE = """# 用户画像

> 自动生成于 {today}，最新更新于 {today}

## 关注维度矩阵

| 维度 | 提及次数 | 首次关注 | 最近关注 | 关联论文 |
|------|----------|----------|----------|----------|
| （待填充） | - | - | - | - |

## 研究兴趣演变

（首次使用 paper-reading-notes skill 后自动填充）

## 方法论偏好

（从读后感中推断，首次使用后自动填充）

## 写作风格画像

### 常用表达
（从读后感用词中提取）

### 语气偏好
（待观察）

### 句式特征
（待观察）

### 修改模式
（从用户对总结的修改中学习）

## 校正记录

（用户纠正过的理解偏差，首次使用后自动填充）

## 阅读历史

（每篇读后感的摘要记录）
"""


def main():
    os.makedirs(PROFILES_DIR, exist_ok=True)
    today = date.today().isoformat()

    if os.path.exists(PROFILE_FILE):
        print(f"用户画像已存在: {PROFILE_FILE}")
        print("若要重新初始化，请先删除该文件。")
        return

    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(today=today))

    print(f"用户画像模板已创建: {PROFILE_FILE}")
    print("首次使用 paper-reading-notes skill 时会自动填充内容。")


if __name__ == "__main__":
    main()
