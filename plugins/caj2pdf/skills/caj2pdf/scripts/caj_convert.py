#!/usr/bin/env python3
"""CAJ/KDH/NH 转 PDF 转换工具

支持多种转换方法：
- caj2pdf: 使用 caj2pdf 库，保留文本层和大纲
- pymupdf: 使用 PyMuPDF 直接读取（适用于内嵌 PDF 格式的 CAJ）
- auto: 自动选择最佳方案

用法:
  python caj_convert.py input.caj -o output.pdf
  python caj_convert.py --batch /path/to/dir -o /path/to/output/
"""

import os
import sys
import subprocess
import shutil
import argparse
import io
from pathlib import Path

# 修复 Windows GBK 编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# ─── caj2pdf 路径解析 ───────────────────────────────────────────

SKILL_ROOT = Path(__file__).resolve().parent.parent
CAJ2PDF_REPO = SKILL_ROOT / "caj2pdf_repo"


def _find_caj2pdf_cmd():
    """查找 caj2pdf 命令的可用路径

    返回 (python_exe, script_path) 或 (None, None)
    """
    # 方法 1: 已安装为 pip 包，caj2pdf 在 PATH 中
    if shutil.which("caj2pdf"):
        return (None, "caj2pdf")  # 直接调命令

    # 方法 2: 本地克隆的源码
    if CAJ2PDF_REPO.exists():
        entry = CAJ2PDF_REPO / "caj2pdf"
        if entry.exists():
            return (sys.executable, str(entry))

    return (None, None)


# ─── 转换方法实现 ────────────────────────────────────────────────


def convert_via_caj2pdf(input_path, output_path):
    """使用 caj2pdf 库转换"""
    python_exe, caj2pdf_path = _find_caj2pdf_cmd()

    if caj2pdf_path is None:
        raise RuntimeError(
            "caj2pdf 未找到。请运行 install_deps.py 安装:\n"
            f"  python {SKILL_ROOT / 'scripts' / 'install_deps.py'}"
        )

    if python_exe:
        # 使用本地克隆版本: python caj2pdf convert ...
        cmd = [python_exe, caj2pdf_path, "convert", str(input_path), "-o", str(output_path)]
    else:
        # 使用 PATH 中的 caj2pdf
        cmd = [caj2pdf_path, "convert", str(input_path), "-o", str(output_path)]

    print(f"  执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()

        # 检查是否为已知的不支持错误
        if "Unknown file type" in stderr or "Unsupported file type" in stderr:
            raise RuntimeError(f"caj2pdf 不支持此文件类型: {stderr}")
        elif "HN" in stderr and "unsupported" in stderr.lower():
            raise RuntimeError(f"caj2pdf 不支持 HN 格式: {stderr}")
        else:
            # 输出可能包含有用信息的 stdout
            output = stdout or stderr
            raise RuntimeError(f"caj2pdf 转换失败:\n{output}")

    return result.stdout


def convert_via_pymupdf(input_path, output_path):
    """使用 PyMuPDF 直接读取并保存为 PDF"""
    try:
        import fitz
    except ImportError:
        raise RuntimeError("PyMuPDF (fitz) 未安装，请运行: pip install PyMuPDF")

    print(f"  使用 PyMuPDF 读取...")
    try:
        doc = fitz.open(str(input_path))
    except Exception as e:
        raise RuntimeError(f"PyMuPDF 无法打开此文件: {e}")

    page_count = doc.page_count
    print(f"  页数: {page_count}")

    if page_count == 0:
        doc.close()
        raise RuntimeError("文件包含 0 页，可能不是有效的文档格式")

    # 保存为 PDF
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()
    print(f"  已保存: {output_path}")
    return f"成功转换 {page_count} 页"


def convert_via_caj2pdf_outline_only(input_path, output_path):
    """仅提取大纲信息（用于已有图片 PDF 补充大纲）"""
    python_exe, caj2pdf_path = _find_caj2pdf_cmd()

    if caj2pdf_path is None:
        raise RuntimeError("caj2pdf 未找到，请先运行 install_deps.py")

    if python_exe:
        cmd = [python_exe, caj2pdf_path, "outlines", str(input_path), "-o", str(output_path)]
    else:
        cmd = [caj2pdf_path, "outlines", str(input_path), "-o", str(output_path)]

    print(f"  执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        raise RuntimeError(f"大纲提取失败: {result.stderr.strip()}")

    return result.stdout


def compress_pdf(output_path):
    """使用 PyMuPDF 压缩 PDF"""
    try:
        import fitz
    except ImportError:
        print("  ⚠️ PyMuPDF 未安装，跳过压缩")
        return

    try:
        doc = fitz.open(str(output_path))
        doc.save(
            str(output_path).replace(".pdf", "_compressed.pdf"),
            garbage=4,
            deflate=True,
            clean=True,
        )
        doc.close()

        # 如果压缩版更小，替换原文件
        orig = os.path.getsize(output_path)
        comp = os.path.getsize(str(output_path).replace(".pdf", "_compressed.pdf"))
        if comp < orig:
            os.replace(
                str(output_path).replace(".pdf", "_compressed.pdf"),
                output_path,
            )
            print(f"  📦 压缩: {orig / 1024:.0f} KB → {comp / 1024:.0f} KB")
        else:
            os.remove(str(output_path).replace(".pdf", "_compressed.pdf"))
            print(f"  📦 已是最优大小，无需压缩")
    except Exception as e:
        print(f"  ⚠️ 压缩失败: {e}")


# ─── 主流程 ──────────────────────────────────────────────────────


def convert_single(input_path, output_path, method="auto", compress=False):
    """转换单个文件"""
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        return False

    print(f"\n📄 {input_path.name}")
    print(f"   大小: {os.path.getsize(input_path) / 1024:.0f} KB")

    methods_to_try = []
    if method == "auto":
        methods_to_try = ["pymupdf", "caj2pdf"]
    elif method == "pymupdf":
        methods_to_try = ["pymupdf"]
    elif method == "caj2pdf":
        methods_to_try = ["caj2pdf"]
    else:
        print(f"❌ 未知转换方法: {method}")
        return False

    last_error = None
    for m in methods_to_try:
        try:
            print(f"\n  🔄 尝试 [{m}] 方法...")
            if m == "caj2pdf":
                output = convert_via_caj2pdf(input_path, output_path)
            elif m == "pymupdf":
                output = convert_via_pymupdf(input_path, output_path)
            else:
                continue
            print(f"  ✅ 转换成功！")
            if output:
                for line in output.strip().split("\n"):
                    print(f"     {line}")

            # 压缩
            if compress:
                print()
                compress_pdf(output_path)

            return True

        except RuntimeError as e:
            print(f"  ❌ [{m}] 失败: {e}")
            last_error = e
            continue

    # 所有方法都失败
    print(f"\n❌ 所有方法均转换失败")
    if last_error:
        print(f"   最后错误: {last_error}")
    print(f"\n💡 替代方案:")
    print(f"   1. 安装全球学术快报 (https://cajviewer.cnki.net/)")
    print(f"      文件 → 导入 → 选择 CAJ → 导出为 PDF")
    print(f"   2. CAJViewer 打印为 PDF (文本不可选)")
    return False


def convert_batch(directory, output_dir, method="auto", compress=False):
    """批量转换目录下所有 CAJ 文件"""
    directory = Path(directory)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extensions = ["*.caj", "*.Caj", "*.CAJ",
                  "*.kdh", "*.Kdh", "*.KDH",
                  "*.nh", "*.Nh", "*.NH"]

    files = []
    for ext in extensions:
        files.extend(directory.rglob(ext))

    if not files:
        print(f"❌ 在 {directory} 中未找到 CAJ/KDH/NH 文件")
        return

    print(f"📂 批量转换 {len(files)} 个文件")
    print(f"   源目录: {directory}")
    print(f"   输出目录: {output_dir}")
    print()

    success = 0
    failed = []

    for i, f in enumerate(files, 1):
        rel_path = f.relative_to(directory)
        out_path = output_dir / rel_path.with_suffix(".pdf")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"[{i}/{len(files)}] {rel_path}")
        if convert_single(f, out_path, method=method, compress=compress):
            success += 1
        else:
            failed.append(str(rel_path))
        print()

    # 汇总
    print("=" * 60)
    print(f"  完成: {success}/{len(files)} 成功")
    if failed:
        print(f"  失败 ({len(failed)}):")
        for f in failed:
            print(f"    - {f}")
        print()
        print(f"  失败的文件可尝试用全球学术快报手动转换")
    print("=" * 60)

    return success, failed


# ─── CLI ─────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="CAJ/KDH/NH 转 PDF 转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python caj_convert.py paper.caj -o paper.pdf
  python caj_convert.py paper.caj --method pymupdf -o paper.pdf
  python caj_convert.py --batch ~/Downloads/caj_files/ -o ~/pdfs/
  python caj_convert.py paper.caj --compress -o paper.pdf
        """,
    )

    parser.add_argument("input", nargs="?", help="输入 CAJ/KDH/NH 文件路径")
    parser.add_argument("-o", "--output", help="输出 PDF 路径")
    parser.add_argument(
        "--batch",
        metavar="DIR",
        help="批量转换目录下所有 CAJ/KDH/NH 文件",
    )
    parser.add_argument(
        "--method",
        choices=["auto", "caj2pdf", "pymupdf"],
        default="auto",
        help="转换方法 (默认: auto)",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="压缩输出 PDF",
    )

    args = parser.parse_args()

    # 批量模式
    if args.batch:
        output_dir = args.output or Path(args.batch) / "_pdf_output"
        convert_batch(args.batch, output_dir, method=args.method, compress=args.compress)
        return

    # 单文件模式
    if not args.input:
        parser.print_help()
        sys.exit(1)

    input_path = Path(args.input)
    output_path = args.output or input_path.with_suffix(".pdf")

    success = convert_single(input_path, output_path, method=args.method, compress=args.compress)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
