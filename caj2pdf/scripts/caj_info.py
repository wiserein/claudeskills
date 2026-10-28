#!/usr/bin/env python3
"""CAJ 文件元数据读取工具

读取中国知网 CAJ/KDH/NH 文件的元数据信息，
包括文件类型、页数、大纲结构等。
"""

import os
import sys
import struct
import json
import subprocess
import shutil
import io
from pathlib import Path

# 修复 Windows GBK 编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SKILL_ROOT = Path(__file__).resolve().parent.parent
CAJ2PDF_REPO = SKILL_ROOT / "caj2pdf_repo"


def _find_caj2pdf():
    """返回 (python_exe_or_None, caj2pdf_cmd_or_path)"""
    if shutil.which("caj2pdf"):
        return (None, "caj2pdf")
    if CAJ2PDF_REPO.exists():
        entry = CAJ2PDF_REPO / "caj2pdf"
        if entry.exists():
            return (sys.executable, str(entry))
    return (None, None)


def read_caj_header(filepath):
    """读取 CAJ 文件的二进制头信息，判断文件类型"""
    with open(filepath, "rb") as f:
        # 读取前 512 字节
        header = f.read(512)

        # 检查 PDF 签名 (部分 CAJ 实际上是嵌在 PDF 里的)
        if header.startswith(b"%PDF"):
            return "pdf-wrapped", "文件头部包含 PDF 签名，可能为 PDF 内嵌格式"

        # 检查常见 CAJ 魔法字节
        magic = header[:16]

        # HN 格式: 文件头多种可能
        if magic[:4] == b"\x00\x00\x00\x00" or magic[:4] == b"\x01\x00\x00\x00":
            return "hn", "HN 格式（学位论文）"

        # 检查是否为 CAJ 标准的压缩流
        try:
            text = header.decode("ascii", errors="ignore")
            if "CAJ" in text or "caj" in text.lower():
                return "caj", "CAJ 标准格式"
        except Exception:
            pass

        # 通用的 hex 检测
        hex_magic = magic.hex()
        return "unknown", f"未知类型 (magic: {hex_magic[:32]})"


def get_file_info(filepath):
    """获取文件基本信息"""
    stat = os.stat(filepath)
    return {
        "path": str(Path(filepath).resolve()),
        "name": Path(filepath).name,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified": stat.st_mtime,
    }


def try_caj2pdf_info(filepath):
    """尝试用 caj2pdf CLI 获取详细信息"""
    python_exe, caj2pdf_cmd = _find_caj2pdf()
    if caj2pdf_cmd is None:
        return None

    if python_exe:
        cmd = [python_exe, caj2pdf_cmd, "show", str(filepath)]
    else:
        cmd = [caj2pdf_cmd, "show", str(filepath)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
        return result.stdout.strip()
    return result.stderr.strip() if result.stderr else None


def try_pymupdf_info(filepath):
    """尝试用 PyMuPDF 读取信息（部分 CAJ 本质是 PDF 流）"""
    try:
        import fitz
        doc = fitz.open(filepath)
        info = {
            "pages": doc.page_count,
            "format": doc.metadata.get("format", "N/A"),
            "title": doc.metadata.get("title", "N/A"),
            "author": doc.metadata.get("author", "N/A"),
            "subject": doc.metadata.get("subject", "N/A"),
        }
        doc.close()
        return info
    except Exception:
        return None


def main():
    if len(sys.argv) < 2:
        print("用法: python caj_info.py <file.caj> [file2.caj ...]")
        print()
        print("读取 CAJ/KDH/NH 文件的元数据信息。")
        sys.exit(1)

    files = sys.argv[1:]

    for i, filepath in enumerate(files):
        if i > 0:
            print("\n" + "─" * 60 + "\n")

        filepath = Path(filepath)
        if not filepath.exists():
            print(f"❌ 文件不存在: {filepath}")
            continue

        # 基本文件信息
        info = get_file_info(filepath)
        print(f"📄 {info['name']}")
        print(f"   路径: {info['path']}")
        print(f"   大小: {info['size_mb']} MB ({info['size_bytes']:,} bytes)")
        print(f"   后缀: {filepath.suffix.upper()}")

        # CAJ 头部分析
        caj_type, caj_desc = read_caj_header(filepath)
        print(f"   类型: {caj_type.upper()} ({caj_desc})")

        # 尝试 PyMuPDF
        pymupdf_info = try_pymupdf_info(filepath)
        if pymupdf_info:
            print(f"\n📖 PyMuPDF 可直接读取:")
            print(f"   页数: {pymupdf_info['pages']}")
            if pymupdf_info['title'] != 'N/A':
                print(f"   标题: {pymupdf_info['title']}")
            if pymupdf_info['author'] != 'N/A':
                print(f"   作者: {pymupdf_info['author']}")

        # 尝试 caj2pdf
        caj2pdf_output = try_caj2pdf_info(filepath)
        if caj2pdf_output:
            print(f"\n📋 caj2pdf 输出:")
            for line in caj2pdf_output.split("\n"):
                print(f"   {line}")
        else:
            print(f"\n💡 提示: caj2pdf CLI 未安装，运行 install_deps.py 安装后可获取更详细信息")

        # 转换建议
        print(f"\n🔧 推荐转换方式:")
        if caj_type == "pdf-wrapped" or (pymupdf_info and pymupdf_info.get("pages", 0) > 0):
            print(f"   1. PyMuPDF 直读 → python caj_convert.py \"{filepath.name}\" --method pymupdf")
            print(f"   2. caj2pdf CLI  → python caj_convert.py \"{filepath.name}\" --method caj2pdf")
        elif caj_type == "hn":
            print(f"   1. 全球学术快报  → 官方软件导入后导出 PDF（成功率最高）")
            print(f"   2. caj2pdf CLI  → python caj_convert.py \"{filepath.name}\" --method caj2pdf")
        else:
            print(f"   1. caj2pdf CLI  → python caj_convert.py \"{filepath.name}\" --method caj2pdf")
            print(f"   2. PyMuPDF 直读 → python caj_convert.py \"{filepath.name}\" --method pymupdf")
            print(f"   3. 全球学术快报  → 官方软件导入后导出 PDF")


if __name__ == "__main__":
    main()
