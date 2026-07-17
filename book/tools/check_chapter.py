#!/usr/bin/env python3
"""章节结构与引用溯源检查。

用法: check_chapter.py <manuscript.md> [--min-words N] [--max-words N]
                        [--min-citations N] [--repo-root PATH]

检查项:
  1. 正文字数（中文按字符、代码块不计）
  2. file:line 引用有效性（文件存在且行号不超过文件长度）
  3. 至少一张示意图（mermaid 代码块或 ASCII 图框）
  4. 章末含"设计要点回顾"
退出码: 0 通过，1 任一项失败（stderr 列出失败项）。
"""
import re
import sys
from pathlib import Path


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(args[0])
    opts = dict(zip(args[1::2], args[2::2]))
    min_words = int(opts.get("--min-words", 8000))
    max_words = int(opts.get("--max-words", 15000))
    min_cites = int(opts.get("--min-citations", 5))
    repo = Path(opts.get("--repo-root", ".")).resolve()

    text = path.read_text(encoding="utf-8")
    failures: list[str] = []

    # 1. 字数（剔除代码块）
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    words = len(re.sub(r"\s", "", prose))
    if not (min_words <= words <= max_words):
        failures.append(f"字数 {words} 不在 [{min_words}, {max_words}] 区间")

    # 2. file:line 引用有效性（形如 path/to/file.rs:123，仅检查指向 crates/ 的）
    cites = re.findall(r"`?((?:crates|prod)/[\w\-./]+\.\w+):(\d+)`?", text)
    if len(cites) < min_cites:
        failures.append(f"file:line 引用 {len(cites)} 处，少于 {min_cites}")
    for rel, line in cites:
        f = repo / rel
        if not f.exists():
            failures.append(f"引用失效: {rel} 不存在")
        elif int(line) > sum(1 for _ in f.open(encoding="utf-8", errors="ignore")):
            failures.append(f"引用失效: {rel}:{line} 超出文件长度")

    # 3. 示意图
    if not re.search(r"```(mermaid|text|ascii)", text) and not re.search(
        r"[┌┐└┘├┤│─►▼]", text
    ):
        failures.append("缺少示意图（mermaid 代码块或 ASCII 图）")

    # 4. 设计要点回顾
    if "设计要点回顾" not in text:
        failures.append('缺少章末"设计要点回顾"清单')

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    print(f"OK: {path.name} 字数={words} 引用={len(cites)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
