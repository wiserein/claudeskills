---
name: caj2pdf
description: >
  读取和转换中国知网 (CNKI) 专有文献格式的工具集。支持 CAJ、KDH、NH 格式的
  元数据读取、PDF 转换和批量处理。Use when 用户需要查看 CAJ 文件内容、将 CAJ/KDH/NH
  转为 PDF、批量转换知网文献，或提到 "CAJ 转 PDF""打开 CAJ""知网文献转换"。
---

# CAJ 转 PDF Skill

你是一个 CAJ 文件处理专家，帮助用户读取和转换中国知网 (CNKI) 的专有文献格式。

## 支持的文件格式

| 格式 | 说明 | 转换支持 |
|------|------|---------|
| `.caj` | 中国学术期刊全文格式 | ✅ 完整支持 |
| `.kdh` | 知网学位论文格式 | ⚠️ 部分支持 |
| `.nh` | 知网学位论文格式（新版） | ⚠️ 部分支持 |

## 核心能力

### 1. 读取 CAJ 文件信息

```bash
python3 ~/.claude/skills/caj2pdf/scripts/caj_info.py <file.caj>
```

输出信息包括：
- 文件类型和版本
- 总页数
- 大纲/目录结构
- 文件大小

### 2. CAJ 转 PDF

```bash
python3 ~/.claude/skills/caj2pdf/scripts/caj_convert.py <file.caj> -o <output.pdf>
```

转换后的 PDF：
- 保留可选择/搜索的文本层（非图片 PDF）
- 保留原文档大纲/书签
- 保持原始排版

### 3. 批量转换

```bash
python3 ~/.claude/skills/caj2pdf/scripts/caj_convert.py --batch <directory> -o <output_dir>
```

递归搜索目录下所有 `.caj`/`.kdh`/`.nh` 文件并逐一转换。

## 工作流程

### Step 1: 检查环境依赖

首次使用前检查并安装依赖：

```bash
python3 ~/.claude/skills/caj2pdf/scripts/install_deps.py
```

依赖说明：
- **Python 3.8+**
- **PyMuPDF (fitz)** — 已安装时可做 PDF 后处理（压缩、合并、OCR）
- **PyPDF2** — PDF 元数据写入
- **mutool** — MuPDF 命令行工具，部分 CAJ 子格式需要
- **caj2pdf** — 核心转换库，首次运行时会自动通过 pip 安装

### Step 2: 查看文件信息

先读取 CAJ 文件元数据，确认文件类型是否支持：

```bash
python3 ~/.claude/skills/caj2pdf/scripts/caj_info.py <file.caj>
```

如果输出报错 `Unknown file type` 或 `Unsupported file type`，说明该文件无法通过 caj2pdf 直接转换，跳到 Step 4 使用替代方案。

### Step 3: 执行转换

```bash
python3 ~/.claude/skills/caj2pdf/scripts/caj_convert.py <file.caj> -o <output.pdf>
```

### Step 4: 替代方案（当 caj2pdf 转换失败时）

如果 caj2pdf 无法处理目标文件，有多种替代方案：

#### 方案 A：PyMuPDF 直接读取

部分 CAJ 文件内部其实是 PDF 流，PyMuPDF 可以直接打开：

```bash
python3 ~/.claude/skills/caj2pdf/scripts/caj_convert.py <file.caj> --method pymupdf -o <output.pdf>
```

#### 方案 B：全球学术快报（官方工具）

caj2pdf-2025 方案的三步流程：

1. **收集 CAJ 文件**到一个目录
2. **使用"全球学术快报"桌面版**（知网官方阅读器）
   - 文件 → 导入 → 选择所有 CAJ 文件
   - 文件 → 导出 → 导出为 PDF
   - 全球学术快报下载地址：https://cajviewer.cnki.net/
3. **批量回迁** PDF 到原始位置

Claude 可以帮你完成第 1 步和第 3 步，第 2 步需要你在全球学术快报中手动操作。

#### 方案 C：CAJViewer 打印

1. 用 CAJViewer 打开文件
2. 文件 → 打印 → 选择 "Microsoft Print to PDF"
3. 缺点：生成的 PDF 是图片，文字不可选择

如果使用此方案生成了图片 PDF，可以后续用 `caj2pdf outlines` 命令补回大纲：

```bash
caj2pdf outlines <原始.caj> -o <图片版.pdf>
```

## 转换质量对比

| 方案 | 文本可选择 | 保留大纲 | 图片质量 | 成功率 |
|------|-----------|---------|---------|--------|
| caj2pdf CLI | ✅ | ✅ | 原图 | 60-80% |
| PyMuPDF 直读 | ✅ | ❌ | 原图 | 30-50% |
| 全球学术快报 | ✅ | ✅ | 原图 | 95%+ |
| CAJViewer 打印 | ❌ | 可补 | 取决于设置 | 100% |

## 脚本参数参考

### caj_info.py

```
usage: caj_info.py <file.caj> [file2.caj ...]

读取 CAJ 文件的元数据信息。
支持同时查看多个文件。
```

### caj_convert.py

```
usage: caj_convert.py <input.caj> [-o output.pdf] [options]

options:
  -o, --output PATH       输出 PDF 路径（默认：与输入同名的 .pdf）
  --batch DIRECTORY       批量转换目录下所有 CAJ 文件
  --method {caj2pdf,pymupdf,auto}
                          转换方法（默认：auto，自动选择最佳方案）
  --compress              压缩输出 PDF
  --no-outlines           不提取大纲
```

## 常见问题

### Q: 转换后 PDF 是空白的？
A: 该文件可能是 HN 格式，caj2pdf 对 HN 格式支持有限。尝试方案 B（全球学术快报）。

### Q: mutool not found？
A: Windows 用户需下载 mupdf 的 mutool.exe 并加入 PATH：
```bash
# 可使用 Chocolatey
choco install mupdf
# 或手动下载：https://mupdf.com/releases/
```

### Q: pip 安装 caj2pdf 失败？
A: 尝试从 GitHub 直接安装：
```bash
pip install git+https://github.com/caj2pdf/caj2pdf.git
# 或使用重构版
pip install caj2pdf-restructured
```
