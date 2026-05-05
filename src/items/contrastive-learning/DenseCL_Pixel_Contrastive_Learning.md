# DenseCL: Dense Contrastive Learning for Self-Supervised Visual Pre-Training

## 基本信息

- **论文标题**: Dense Contrastive Learning for Self-Supervised Visual Pre-Training
- **作者**: Xinlong Wang, Rufeng Zhang, Chunhua Shen, Tao Kong, Lei Li（The University of Adelaide, Tongji University, ByteDance AI Lab）
- **发表时间**: 2021年4月（arXiv:2011.09157v2 [cs.CV]）
- **代码**: https://git.io/DenseCL

## 面向的问题

已有的自监督学习方法（如 SimCLR、MoCo-v2）几乎都设计和优化于**图像分类任务**——它们的预训练目标是对整张图片进行实例判别（instance discrimination），使用全局特征向量做对比学习。然而，这种**图像级预测**与**密集预测任务**（如目标检测、语义分割、实例分割）之间存在根本性差距：

1. **图像分类**：对整张图片分配一个类别 → 使用全局特征 ($h \in \mathbb{R}^d$)
2. **密集预测**：对每个像素/区域进行分类或回归 → 需要局部特征 ($\mathbf{H} \in \mathbb{R}^{C \times H \times W}$)

作者指出，更好的图像分类性能**并不能保证**更好的目标检测性能。因此需要一种**直接为密集预测任务定制的自监督学习方法**——在像素级别进行对比学习。

## 核心方法定位：像素级对比学习

DenseCL 把自监督学习视为一个**密集成对对比学习**问题，而非全局图像分类问题。核心思想：

> 在特征图的**每个空间位置**上执行对比学习，正样本来自同一图片另一增强视图的**对应空间位置**，负样本来自不同图片的特征向量。

这意味着对比的粒度从"整张图片"下沉到"像素/局部特征"级别。

## 方法流程

### 第一步：数据增强（同实例级方法）
与 SimCLR/MoCo-v2 一致，对每张图片采样两次增强操作，生成两个视图 $x^1, x^2$。但增强后**保持空间分辨率**用于后续密集对比。

### 第二步：Backbone Encoder（前向传播）
使用全卷积网络（FCN）提取特征图，**保留空间信息**：

$$\mathbf{F}^q = \text{Backbone}(x^1) \in \mathbb{R}^{C \times S_h \times S_w}$$

$$\mathbf{F}^k = \text{Backbone}(x^2) \in \mathbb{R}^{C \times S_h \times S_w}$$

注意：此处不进行平均池化，输出是**三维特征图**而非一维向量。

### 第三步：Dense Projection Head（密集投影头——核心创新）

与 SimCLR 的全局投影头不同，DenseCL 使用**密集投影头**：

**全局投影分支**（与 MoCo-v2 相同，保留实例级对比）：
- 全局平均池化 → MLP → 全局特征向量 $q, k \in \mathbb{R}^{128}$

**密集投影分支**（新增，实现像素级对比）：
- 使用 $1 \times 1$ 卷积替代全局池化 + MLP
- 保持特征图空间维度，对每个空间位置生成一个特征向量
- 输出 $\mathbf{Q}, \mathbf{K} \in \mathbb{R}^{d \times S_h \times S_w}$，空间维度与骨干特征图完全一致

### 第四步：密集对比损失（Dense Contrastive Loss）

这是 DenseCL 最核心的创新——在特征图的**每个空间位置**计算对比损失。

**正样本匹配（建立空间对应关系）**：

输入图片经过相同的增强变换（裁剪 + resize），因此两个视图之间存在像素级别的空间对应关系：视图 1 中位置 $(h, w)$ 的局部特征，其正样本就是视图 2 中**对应空间位置**的局部特征。

**密集损失函数**：

$$\mathcal{L}_{\text{dense}} = \frac{1}{S_h S_w} \sum_{h=1}^{S_h} \sum_{w=1}^{S_w} \ell(\mathbf{Q}_{h,w}, \mathbf{K}_{h,w})$$

其中 $\ell(q, k)$ 为对比损失（InfoNCE）：
$$\ell(q, k) = -\log \frac{\exp(q \cdot k^+ / \tau)}{\exp(q \cdot k^+ / \tau) + \sum_{k^-} \exp(q \cdot k^- / \tau)}$$

**负样本来源**：
- 实例级方法：负样本是 batch 中**其他图片的全局特征**
- DenseCL（像素级）：负样本是 **key encoder 特征图中所有其他空间位置的特征向量** + 记忆库中存储的特征

**最终训练目标**：

$$\mathcal{L} = (1 - \lambda) \mathcal{L}_{\text{global}} + \lambda \mathcal{L}_{\text{dense}}$$

- $\mathcal{L}_{\text{global}}$：原有 MoCo-v2 的全局对比损失（实例级）
- $\mathcal{L}_{\text{dense}}$：新增的密集对比损失（像素级）
- $\lambda$：平衡系数（通常取 0.5）

### 第五步：后处理（下游密集预测任务微调）

训练完成后，**同时丢弃**全局和密集投影头，仅保留 backbone 的特征图输出：

1. **目标检测**：Faster R-CNN，使用 backbone 特征图提取 RoI
2. **语义分割**：FCN，直接使用 backbone 特征图进行像素级分类
3. **实例分割**：Mask R-CNN

**主要实验结果**（基于 ImageNet 预训练，COCO 预训练效果更佳）：

| 任务 | MoCo-v2 基线 | DenseCL | 提升 |
|------|-------------|---------|------|
| PASCAL VOC 目标检测 | - | - | **+2.0% AP** |
| COCO 目标检测 | - | - | **+1.1% AP** |
| COCO 实例分割 | - | - | **+0.9% AP** |
| PASCAL VOC 语义分割 | - | - | **+3.0% mIoU** |
| Cityscapes 语义分割 | - | - | **+1.8% mIoU** |

计算开销极低——仅增加 <1% 训练时间，但带来显著的密集预测性能提升。

## 核心结论

1. **图像级预训练与密集预测任务之间存在结构性差距**：全局对比学习学到的特征对密集预测任务而言是次优的
2. **密集对比学习直接在像素空间优化**：通过 $1 \times 1$ 卷积投影头和空间对应匹配，将对比从"图 vs 图"下沉到"像素 vs 像素"
3. **保留全局分支的混合策略有效**：$\mathcal{L} = (1-\lambda)\mathcal{L}_{\text{global}} + \lambda\mathcal{L}_{\text{dense}}$ 兼顾了实例级和像素级特征
4. **极低的额外开销**：仅增加 <1% 计算量，但密集预测任务提升显著
