# Claude Code Skills

作者 [@wiserein](https://github.com/wiserein) 整理的三个 Claude Code skill，覆盖学术文献、文档处理、数学建模场景。

## 安装

把对应目录复制到你的 skill 目录即可：

- **全局**（所有项目可用）：`~/.claude/skills/<skill名>/`
- **单项目**：`.claude/skills/<skill名>/`

例如：

```bash
cp -r caj2pdf ~/.claude/skills/
```

重启 Claude Code 后，在对话中直接描述需求即可触发对应 skill。

## Skill 列表

### 1. caj2pdf — 知网 CAJ 转 PDF

读取和转换中国知网（CNKI）专有文献格式，支持 CAJ / KDH / NH 的元数据读取、PDF 转换与批量处理。

- 触发：`CAJ 转 PDF`、`打开 CAJ`、`知网文献转换`
- 转换核心基于开源项目 [caj2pdf/caj2pdf](https://github.com/caj2pdf/caj2pdf)（MIT License，见 `caj2pdf/caj2pdf_repo/LICENSE`）

### 2. aigc-reduce — 学术论文 AIGC 降重

降低学术论文的 AIGC 查重率、减少 AI 味，帮助论文表达更自然、更像人工书写。定位为 **AI 合规自查与写作质量优化**，请勿用于规避学术诚信规范。

- 触发：`降 AI 味`、`降重`、`去 AI 检测`、`AIGC 查重`

### 3. cumcm-master — 数学建模（CUMCM）全流程

以国一为标杆的国赛全流程指南，含审题建模、编程求解、论文写作、LaTeX 排版、图表规范、评阅扣分点与国一评分标准。

- 触发：`数学建模`、`国赛`、`美赛`、`CUMCM`、`建模论文`
- `templates/cumcmthesis.cls` 为 CUMCM 官方 LaTeX 模板，版权归全国大学生数学建模竞赛组委会。

## 许可

各 skill 目录下的代码与文档采用 MIT License（作者 wiserein），除非其中另有标注。第三方组件（caj2pdf、cumcmthesis 官方模板）保留其原始许可与版权。
