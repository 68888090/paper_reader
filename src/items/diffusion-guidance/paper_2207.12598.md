# CLASSIFIER-FREE DIFFUSION GUIDANCE 论文总结

## 基本信息

- **论文标题**: Classifier-Free Diffusion Guidance
- **作者**: Jonathan Ho, Tim Salimans（Google Research, Brain team）
- **发表时间**: 2022年7月26日（arXiv），短版本发表于 NeurIPS 2021 Workshop on Deep Generative Models and Downstream Applications
- **刊物/平台**: arXiv:2207.12598v1 [cs.LG]

## 面向的问题

扩散模型（Diffusion Models）在图像和音频合成上表现优异，但此前缺乏类似于 GAN（如 BigGAN 的截断采样）或流模型（如 Glow 的低温采样）中"低温采样"的能力。Dhariwal & Nichol (2021) 提出的**分类器引导（Classifier Guidance）**方法通过在采样时引入一个额外的图像分类器的梯度，实现了样本质量（FID）和多样性（IS）之间的权衡，类似于 BigGAN 的截断参数。

但分类器引导存在以下问题：
1. **管道复杂化**：需要额外训练一个分类器，且该分类器必须在一系列噪声水平的数据上进行训练，无法直接使用预训练分类器。
2. **对抗性疑虑**：分类器引导的本质是在采样时将分数估计与分类器梯度混合，这类似于基于梯度的对抗攻击（试图"迷惑"分类器），因此怀疑其在 FID、IS 等分类器相关指标上的提升是否仅仅因为对分类器具有对抗性。
3. **与 GAN 训练的相似性**：沿分类器梯度方向更新与 GAN 训练有相似之处，质疑是否因为"变得更像 GAN"而获得了更好的分类器指标分数。

## 提出的方法：无分类器引导（Classifier-Free Guidance）

本文提出 **Classifier-Free Guidance**，完全不使用任何分类器，而是联合训练一个条件扩散模型和一个无条件扩散模型，在采样时混合两者的分数估计，实现与分类器引导相同的 FID/IS 权衡效果。

### 核心思想

核心公式为：

$$\tilde{\epsilon}_\theta(z_\lambda, c) = (1 + w)\epsilon_\theta(z_\lambda, c) - w\epsilon_\theta(z_\lambda)$$

其中 $w$ 为引导强度。这等价于：
- 当 $w > 0$ 时，将分数估计朝向条件分布方向外推，远离无条件分布方向
- 可解释为：$\tilde{\epsilon}_\theta(z_\lambda, c) = \epsilon_\theta(z_\lambda, c) + w(\epsilon_\theta(z_\lambda, c) - \epsilon_\theta(z_\lambda))$，即条件分数加上引导方向

## 整个方法的流程

### 第一步：训练数据与模型架构

- **数据集**：ImageNet 64×64、ImageNet 128×128（类别条件生成），以及文本到图像生成任务
- **模型架构**：使用 U-Net 结构的扩散模型，基于连续时间扩散框架训练
- **参数化方式**：使用 $\epsilon$-prediction：$x_\theta(z_\lambda) = (z_\lambda - \sigma_\lambda \epsilon_\theta(z_\lambda)) / \alpha_\lambda$

### 第二步：训练过程（核心创新——同时训练条件与无条件模型）

**关键技巧——随机丢弃条件信息**：

训练时，对每个样本以概率 $p_{\text{uncond}}$ 将条件 $c$ 替换为一个空标记 $\emptyset$（null token）。即：

1. 以概率 $1 - p_{\text{uncond}}$：正常输入条件 $c$，训练条件模型 $\epsilon_\theta(z_\lambda, c)$
2. 以概率 $p_{\text{uncond}}$：将条件 $c$ 设为 $\emptyset$，训练无条件模型 $\epsilon_\theta(z_\lambda)$（即 $\epsilon_\theta(z_\lambda, \emptyset)$）

这样一来，**同一个模型同时学会了条件生成和无条件生成**，无需训练两个独立模型。$\epsilon_\theta(z_\lambda, \emptyset)$ 就等价于无条件分数估计。

### 第三步：前向过程（加噪过程）

使用连续时间扩散框架，给定数据 $x \sim p(x)$：
- $q(z_\lambda|x) = \mathcal{N}(\alpha_\lambda x, \sigma_\lambda^2 I)$
- $\alpha_\lambda^2 = 1/(1 + e^{-\lambda})$，$\sigma_\lambda^2 = 1 - \alpha_\lambda^2$
- $\lambda = \log(\alpha_\lambda^2 / \sigma_\lambda^2)$ 代表对数信噪比
- 前向过程沿 $\lambda$ 减小的方向进行（信噪比降低）

训练目标为去噪分数匹配：

$$\mathbb{E}_{\epsilon, \lambda} \left[ \|\epsilon_\theta(z_\lambda) - \epsilon\|_2^2 \right]$$

其中 $\epsilon \sim \mathcal{N}(0, I)$，$z_\lambda = \alpha_\lambda x + \sigma_\lambda \epsilon$。

$\lambda$ 的采样分布：$\lambda = -2\log \tan(au + b)$，$u \sim U[0, 1]$，模拟离散时间的余弦噪声调度。

### 第四步：反向过程（采样过程）

采样时，沿 $\lambda$ 递增方向迭代（$\lambda_{\min} \rightarrow \lambda_{\max}$）：

1. **起始**：$z_{\lambda_{\min}} \sim \mathcal{N}(0, I)$
2. **过渡**：$p_\theta(z_{\lambda'}|z_\lambda) = \mathcal{N}(\tilde{\mu}_{\lambda'|\lambda}(z_\lambda, x_\theta(z_\lambda)), (\tilde{\sigma}_{\lambda'|\lambda}^2)^{1-v}(\sigma_{\lambda'|\lambda}^2)^v)$
3. **引导采样**：在每个时间步，使用混合预测：
   - $\tilde{\epsilon}_\theta(z_\lambda, c) = (1 + w)\epsilon_\theta(z_\lambda, c) - w\epsilon_\theta(z_\lambda, \emptyset)$
   - 将 $\tilde{\epsilon}_\theta$ 代入 $x_\theta(z_\lambda)$ 得到引导后的 $\tilde{x}_\theta(z_\lambda)$
   - 用 $\tilde{x}_\theta$ 计算反向过程的均值
4. **最终输出**：$x_\theta(z_{\lambda_{\max}})$ 为生成的图像

其中 $v$ 为插值超参数（控制方差在 $\tilde{\sigma}^2$ 和 $\sigma^2$ 之间的位置）。

### 第五步：后处理

- 在 ImageNet 类别条件生成中：直接生成对应类别的图像，与分类器引导对比 FID 和 IS
- 在文本到图像生成中：使用 CLIP 重排序或直接从提示词生成

## 主要实验结果

1. **ImageNet 64×64**：无分类器引导实现了与 ADM（有分类器引导）可比的 FID/IS 权衡曲线。$w=2$ 时 FID 达到最优。$p_{\text{uncond}}$ 取 0.1 到 0.3 之间效果相当，过高会损害无条件生成能力。

2. **ImageNet 128×128**：$w=3$ 时 FID 为 2.53，优于分类器引导的 ADM（FID=2.97）。64×128 图像输出中心裁剪到 64×64 进行评估。

3. **无条件引导的可选做法**：当无条件模型与条件模型共享架构但分开训练时（无随机丢弃），也可进行无分类器引导，效果略有下降。

4. **文本到图像生成**：在 GLIDE 上验证了无分类器引导的有效性，结合 CLIP 引导可获得更好效果。

## 无分类器引导的性质

- 引导强度 $w$ 越大：样本质量（FID）先提升后下降，多样性（IS/召回率）单调下降
- $w$ 通过减小多样性来提高每个样本的质量——类似于 BigGAN 截断的"低温采样"效果
- 在三个高斯分布混合的玩具示例上，引导效果表现为：将条件密度缩放为比原始条件分布更"尖锐"的分布，等概率密度面移向高密度区域中心

## 与分类器引导的关系

论文证明了无分类器引导与分类器引导在分数函数层面存在关系。当分类器为 $p(c|x) \propto p(x|c)/p(x)$ 时，两者的梯度方向一致，因此无分类器引导可理解为"隐式地使用了一个由生成模型本身定义的条件概率分类器"。

---

> **📎 读者的读后补充**
>
> 这一篇文章使用了空 token（$\emptyset$）的设置，目标是通过空 token 实现在条件分数与无条件分数之间的插值/外推，从而在不训练额外分类器的情况下模拟分类器引导的效果。核心是利用空 token 训练时同时获得条件与无条件分数估计，采样时通过两者的线性组合（$(1+w)\epsilon_{\text{cond}} - w\epsilon_{\text{uncond}}$）来调节生成的保真度-多样性权衡。
>
> 但这与我（读者）最初想寻找的"空查询"方法有所不同——本文的空 token 是用于训练阶段的条件丢弃和采样阶段的分数外推，而非用于查询阶段的"空查询"机制。尽管如此，本文在扩散模型引导方法上具有相当的建设性意义。
