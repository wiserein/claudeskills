# LaTeX 排版

> 用 LaTeX 写国赛论文，模板固定不乱版。成品模板见 `templates/paper.tex` + `templates/cumcmthesis.cls`。

## 一、环境与编译

- **编译引擎：XeLaTeX**（cumcmthesis.cls 强制要求，支持中文）。
- 推荐 Overleaf 多人协作，但**本地备份/下载 PDF**（Overleaf 提交前半小时会崩）；本地记得 Ctrl+S。
- 公式转 LaTeX 可用"图片识别转 LaTeX"工具；三线表可用生成网站再复制进来。

## 二、文档头设置（复制即用）

```latex
\documentclass[withoutpreface,bwprint]{cumcmthesis}
% withoutpreface：不生成承诺书页 | bwprint：黑白打印

\usepackage{url, subcaption, geometry, setspace, array, graphicx,
            multirow, hyperref, amsmath, amssymb, bm, longtable,
            booktabs, float}

\graphicspath{{../figures/}}   % 图片统一指向 figures/
\geometry{a4paper,top=2.54cm,bottom=2.54cm,left=3.18cm,right=3.18cm}   % 官方规范：上下2.54cm、左右3.18cm

\title{论文标题——副标题点明核心方法}
\begin{document}
\maketitle
```

cumcmthesis.cls 已内置：`\keywords{}`、中文定理环境（定理/假设）、`\upcite{}` 上标引用、章节编号中文化（"一、""1.1"）、booktabs/listings/subcaption 等，无需自己改。

## 三、公式规范

- 重要公式**单独成行 + 编号 (1)(2)**，英文半角括号，右对齐；正文用 `\ref{}` 引用。
- 公式后**加标点**（逗号或句号）。
- 变量用斜体，中文用宋体；公式字体 Times New Roman 斜体。
- 长公式单独占一行，公式浮出文字是常见扣分。
- **禁止公式截图、禁止公式有虚框**。

```latex
% 单行公式（自动编号）
\begin{equation}\label{eq:thickness}
  \Delta\nu = \frac{1}{2 n_1 d \cos\theta_t}
\end{equation}
% 公式后紧跟一段"逐项物理含义"解读
```

## 四、三线表与图

- 三线表写法、图插入写法见 [[06-图表规范]]。

## 五、参考文献（GB/T 7714-2015）

- 数量 8-15 条（最少 5 条），包含期刊、教材、标准文档、AI 工具（如用）。
- **"参考文献"不编号为正文第 X 部分**（高频扣分）。
- 两端对齐排版；期刊论文**不要 DOI 也不要网址**。

### 著录格式（按文献类型）
| 类型 | 格式 |
|------|------|
| 期刊 [J] | 作者. 题名[J]. 刊名, 出版年, 卷(期): 起止页码. |
| 专著 [M] | 作者. 书名[M]. 版本. 出版地: 出版者, 出版年: 页码. |
| 论文集 [C] | 作者. 题名[C]. 出版地: 出版者, 出版年: 页码. |
| 学位论文 [D] | 作者. 题名[D]. 保存地: 保存单位, 年份. |
| 标准 [S] | 标准编号, 标准名称[S]. 出版地: 出版者, 出版年. |
| 专利 [P] | 申请者. 专利题名: 专利号[P]. 公告日期. |
| 电子资源 [EB/OL] | 作者. 题名[EB/OL]. (更新日期)[引用日期]. 获取路径. |
| AI 工具（2025新规） | 工具名, 版本, 开发机构, 使用日期. |

### 文献类型标识代码

专著[M] 期刊[J] 学位论文[D] 会议录[C] 报告[R] 标准[S] 专利[P] 报纸[N] 档案[A] 数据集[DS] 其他[Z]；电子载体：联机[OL] 磁带[MT] 光盘[CD] 磁盘[DK]。作者超过 3 人用"等"（或 et al）。正文引用处标注 [n]，文末按顺序编码制排列。

用 `thebibliography` 手写（不推荐 BibTeX）：
```latex
\begin{thebibliography}{20}
\bibitem{ref1} Goldberg Yu A, Levinshtein M E. Silicon Carbide (SiC)[M].
  In: \textit{Properties of Advanced Semiconductor Materials}. Wiley, 2001: 93-148.
\bibitem{ref2} 张三, 李四. 某论文题名[J]. 某期刊, 2024, 12(3): 45-52.
\bibitem{ref_ai} Claude, Opus 4, Anthropic, 2026年7月.
\end{thebibliography}
```

## 六、AI 标注

AI 使用标注与合规要求见 [[07-AI合规]]。

## 七、附录

- `\section*{附录}` + `\subsection*{}`（不编号）。
- 伪代码用 `verbatim` 环境（不编号），**不放真实代码**，代码贴核心 + 超参数说明，长代码写伪代码。
- 程序文件清单用三线表列"文件名 + 功能 + 运行依赖"。
- 附录不计页数，公式推导可写详细（加分项）。
