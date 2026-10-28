# Claude Code Skills Marketplace

学术科研场景的 Claude Code skill 合集，作者 [@wiserein](https://github.com/wiserein)。

## 一键安装

在 Claude Code 里执行：

```
/plugin marketplace add wiserein/claudeskills
```

然后按需安装（可只装你需要的）：

```
/plugin install caj2pdf
/plugin install aigc-reduce
/plugin install cumcm-master
```

## Skill 列表

### 1. caj2pdf — 知网 CAJ 转 PDF

读取和转换中国知网（CNKI）专有文献格式，支持 CAJ / KDH / NH 的元数据读取、PDF 转换与批量处理。

- 触发：`CAJ 转 PDF`、`打开 CAJ`、`知网文献转换`
- 转换核心基于开源项目 [caj2pdf/caj2pdf](https://github.com/caj2pdf/caj2pdf)（MIT License，见 `plugins/caj2pdf/skills/caj2pdf/caj2pdf_repo/LICENSE`）

### 2. aigc-reduce — 学术论文 AIGC 降重

降低学术论文的 AIGC 查重率、减少 AI 味，帮助论文表达更自然、更像人工书写。定位为 **AI 合规自查与写作质量优化**，请勿用于规避学术诚信规范。

- 触发：`降 AI 味`、`降重`、`去 AI 检测`、`AIGC 查重`

### 3. cumcm-master — 数学建模（CUMCM）全流程

以国一为标杆的国赛全流程指南，含审题建模、编程求解、论文写作、LaTeX 排版、图表规范、评阅扣分点与国一评分标准。

- 触发：`数学建模`、`国赛`、`美赛`、`CUMCM`、`建模论文`
- `templates/cumcmthesis.cls` 为 CUMCM 官方 LaTeX 模板，版权归全国大学生数学建模竞赛组委会。

## 手动安装（不用 marketplace）

把 `plugins/<name>/skills/<name>/` 目录复制到 `~/.claude/skills/<name>/` 即可，例如：

```bash
cp -r plugins/caj2pdf/skills/caj2pdf ~/.claude/skills/caj2pdf
```

## 许可

各 plugin 下的代码与文档采用 MIT License（作者 wiserein），除非其中另有标注。第三方组件（caj2pdf、cumcmthesis 官方模板）保留其原始许可与版权。
