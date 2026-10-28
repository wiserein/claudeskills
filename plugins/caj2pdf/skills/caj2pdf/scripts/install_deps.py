#!/usr/bin/env python3
"""CAJ2PDF 依赖安装脚本

检查并安装 CAJ 转换所需的 Python 包和系统工具。
"""

import subprocess
import sys
import shutil
import platform
import io
from pathlib import Path

# 修复 Windows GBK 编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# 本 skill 的根目录
SKILL_ROOT = Path(__file__).resolve().parent.parent


def run(cmd, **kwargs):
    """运行命令并返回结果"""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)


def check_python_package(import_name):
    """检查 Python 包是否可导入"""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def pip_install(pkg):
    """安装 Python 包"""
    print(f"  >> 安装 {pkg} ...")
    result = run(f'"{sys.executable}" -m pip install {pkg} -q')
    if result.returncode != 0:
        # 打印详细错误
        err = result.stderr.strip().split("\n")[-3:]
        print(f"  !! 安装失败: {'; '.join(err)}")
        return False
    print(f"  OK {pkg}")
    return True


def check_system_tool(cmd, name):
    """检查系统工具是否可用"""
    if shutil.which(cmd):
        print(f"  OK {name}: {shutil.which(cmd)}")
        return True
    else:
        print(f"  -- {name} 未找到 (可选依赖)")
        return False


def install_caj2pdf_from_source():
    """从 GitHub 克隆 caj2pdf 源码到 skill 目录，做本地安装"""
    repo_dir = SKILL_ROOT / "caj2pdf_repo"

    if repo_dir.exists():
        print(f"  OK caj2pdf 源码已存在于: {repo_dir}")
        return True

    print("  >> 从 GitHub 克隆 caj2pdf ...")
    result = run(
        f'git clone --depth 1 https://github.com/caj2pdf/caj2pdf.git "{repo_dir}"',
        timeout=60,
    )
    if result.returncode != 0:
        print(f"  !! 克隆失败: {result.stderr.strip()}")
        return False

    print(f"  OK 克隆完成: {repo_dir}")

    # 安装 caj2pdf 的 Python 依赖 (PyPDF2, imagesize)
    req_file = repo_dir / "requirements.txt"
    if req_file.exists():
        print("  >> 安装 caj2pdf 依赖 ...")
        result = run(f'"{sys.executable}" -m pip install -r "{req_file}" -q')
        if result.returncode != 0:
            print(f"  !! 依赖安装警告: {result.stderr.strip().split(chr(10))[-1]}")
        else:
            print("  OK 依赖安装完成")

    return True


def main():
    print("=" * 60)
    print("  CAJ2PDF 依赖检查与安装")
    print("=" * 60)
    print()

    system = platform.system()
    print(f"  系统: {system} {platform.machine()}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Skill 目录: {SKILL_ROOT}")
    print()

    # ---- Python 包 ----
    print("-- Python 包 --")

    pkgs = [
        ("PyMuPDF", "fitz"),
        ("PyPDF2", "PyPDF2"),
    ]

    for display_name, import_name in pkgs:
        if check_python_package(import_name):
            print(f"  OK {display_name} 已安装")
        else:
            print(f"  -- {display_name} 未安装")
            pip_install(display_name)

    # ---- caj2pdf 源码 ----
    print()
    print("-- caj2pdf 转换引擎 --")

    if check_python_package("caj2pdf"):
        print("  OK caj2pdf 已安装为 Python 包")
    else:
        print("  -- caj2pdf 未作为 pip 包安装 (Python 3.13 兼容性问题)")
        install_caj2pdf_from_source()

    # ---- 系统工具 ----
    print()
    print("-- 系统工具 --")

    check_system_tool("mutool", "mutool (MuPDF CLI)")

    if system == "Windows":
        if not shutil.which("mutool"):
            print()
            print("  TIP Windows 安装 mutool:")
            print("     1. 下载: https://mupdf.com/releases/")
            print("     2. 把 mutool.exe 所在目录加入 PATH")
            print("     或用: choco install mupdf")
    elif system == "Linux":
        if not shutil.which("mutool"):
            print()
            print("  TIP Linux 安装 mutool:")
            print("     sudo apt install mupdf-tools   # Debian/Ubuntu")
            print("     sudo pacman -S mupdf-tools     # Arch")
    elif system == "Darwin":
        if not shutil.which("mutool"):
            print()
            print("  TIP macOS 安装 mutool:")
            print("     brew install mupdf-tools")

    print()
    print("-- 安装完成 --")
    print()
    print("  核心: PyMuPDF (直读转换) + caj2pdf 源码 (CLI 转换)")
    print("  可选: mutool (部分 CAJ 子格式需要)")
    print()
    caj2pdf_repo = SKILL_ROOT / "caj2pdf_repo"
    if caj2pdf_repo.exists():
        print(f"  caj2pdf 源码位置: {caj2pdf_repo}")
        print(f"  用法: cd {caj2pdf_repo} && python caj2pdf show <file.caj>")


if __name__ == "__main__":
    main()
