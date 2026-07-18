#!/usr/bin/env python3
"""引用自愈：以 git 基线快照做“内容锚”，把随上游同步漂移的 `file:line` 机械重定位。

根治思路
--------
书稿引用形如 `crates/.../foo.rs:123`。行号是最脆的锚，每次 monorepo 同步都可能偏移。
本工具不在正文里塞锚，而是把“书上次校验通过的 git commit”（基线）当锚库：

  基线快照里第 123 行的内容 = 这条引用真正指向的东西。
  在当前代码里重新定位这段内容 → 得到当前行号 → 机械改写。

于是：
  * 纯行号漂移（绝大多数）→ 自动重定位、0 token；
  * 那一行/那段代码被实质改写或删除 → 锚找不到 → 报进“需人工/LLM 复核”清单；
  * 成本随真实语义 churn 走，而非书大小或同步大小。

基线 commit 存于 `book/.cite-baseline`（一行，如 `ee567dc`）。heal --write 成功后
应把它更新为当前 commit。

用法
----
  cite_heal.py check [--repo-root .] [--baseline REF]
      只分析，不改。全部可解析（含平移）→ 退出 0；有锚失踪/歧义 → 退出 1 并列出。
  cite_heal.py heal  [--repo-root .] [--baseline REF] [--write]
      重定位；--write 把平移了的行号改回正文。末尾打印“需复核”短清单。
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

CITE = re.compile(r"((?:crates|prod)/[\w\-./]+\.\w+):(\d+)(?:-(\d+))?")
MANUSCRIPTS = "manuscript"
BASELINE_FILE = ".cite-baseline"
MIN_ANCHOR_LEN = 5  # 过短的行（`}`、空行）不足以做唯一锚，需扩窗


def sh(repo: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, check=True,
        )
        return out.stdout
    except subprocess.CalledProcessError:
        return None


def baseline_lines(repo: Path, ref: str, rel: str) -> list[str] | None:
    """基线快照中 rel 的行（无换行）。文件在基线不存在返回 None。"""
    txt = sh(repo, "show", f"{ref}:{rel}")
    return None if txt is None else txt.splitlines()


def current_lines(repo: Path, rel: str) -> list[str] | None:
    p = repo / rel
    if not p.is_file():
        return None
    return p.read_text(encoding="utf-8", errors="ignore").splitlines()


_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? ")
_regions_cache: dict[str, list[tuple[int, int]]] = {}


def changed_regions(repo: Path, ref: str, rel: str) -> list[tuple[int, int]]:
    """基线→当前，rel 被改动的“基线侧”行区间列表（用于判定引用邻域是否变过）。"""
    key = f"{ref}:{rel}"
    if key in _regions_cache:
        return _regions_cache[key]
    diff = sh(repo, "diff", "--unified=0", ref, "--", rel) or ""
    regions: list[tuple[int, int]] = []
    for line in diff.splitlines():
        m = _HUNK.match(line)
        if m:
            start = int(m.group(1))
            length = int(m.group(2)) if m.group(2) else 1
            if length == 0:  # 纯新增，锚定在旧行 start
                regions.append((start, start))
            else:
                regions.append((start, start + length - 1))
    _regions_cache[key] = regions
    return regions


def relocate(anchor_lines: list[str], cur: list[str]) -> tuple[int | None, str]:
    """在 cur 中定位 anchor_lines（1 或 2 行的连续块），返回 (新起始行1based, 状态)。"""
    stripped = [a.strip() for a in anchor_lines]
    n = len(anchor_lines)
    hits = []
    for i in range(len(cur) - n + 1):
        if all(cur[i + k].strip() == stripped[k] for k in range(n)):
            hits.append(i + 1)
    if len(hits) == 1:
        return hits[0], "resolved"
    if len(hits) == 0:
        return None, "gone"
    return None, "ambiguous"


def analyze_citation(repo: Path, ref: str, rel: str, start: int, end: int | None):
    base = baseline_lines(repo, ref, rel)
    cur = current_lines(repo, rel)
    if cur is None:
        return {"status": "file-missing", "rel": rel, "start": start}
    if base is None:
        return {"status": "file-new", "rel": rel, "start": start}
    if start > len(base):
        return {"status": "baseline-oob", "rel": rel, "start": start}

    W = 3
    lo, hi = start - W, (end or start) + W
    region_changed = any(a <= hi and b >= lo for a, b in changed_regions(repo, ref, rel))

    # 就地解析：引用行在当前代码里内容未变，直接判定（避免同名行造成假歧义）。
    if (start <= len(cur)
            and base[start - 1].strip()
            and cur[start - 1].strip() == base[start - 1].strip()):
        return {"status": "resolved", "rel": rel, "start": start, "end": end,
                "new_start": start, "new_end": end, "moved": False,
                "region_changed": region_changed}

    anchor = [base[start - 1]]
    # 锚太短 → 加入下一非空行组成 2 行锚，提升唯一性
    if len(anchor[0].strip()) < MIN_ANCHOR_LEN:
        j = start  # 0-based index of next line
        while j < len(base) and not base[j].strip():
            j += 1
        if j < len(base):
            anchor.append(base[j])

    new_start, status = relocate(anchor, cur)
    if status != "resolved":
        # 单行歧义时，尝试用 2 行锚再定位
        if len(anchor) == 1 and start < len(base):
            two = [base[start - 1], base[start]]
            new_start, status = relocate(two, cur)
        if status != "resolved":
            return {"status": status, "rel": rel, "start": start,
                    "anchor": anchor[0].strip()[:70]}

    delta = new_start - start
    new_end = (end + delta) if end is not None else None
    return {"status": "resolved", "rel": rel, "start": start, "end": end,
            "new_start": new_start, "new_end": new_end, "moved": delta != 0,
            "region_changed": region_changed}


def apply_rewrites(text: str, rmap: dict[tuple[str, int, int | None], tuple[int, int | None]]) -> str:
    """按引用整体（非子串）安全改写行号：CITE 正则逐个匹配，只重写命中 rmap 的那条。"""
    def repl(m: re.Match) -> str:
        rel, s = m.group(1), int(m.group(2))
        e = int(m.group(3)) if m.group(3) else None
        if (rel, s, e) in rmap:
            ns, ne = rmap[(rel, s, e)]
            return f"{rel}:{ns}" + (f"-{ne}" if ne is not None else "")
        return m.group(0)
    return CITE.sub(repl, text)


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] not in ("check", "heal"):
        print(__doc__, file=sys.stderr)
        return 2
    mode = args[0]
    opts = dict(zip(args[1::2], args[2::2]))
    repo = Path(opts.get("--repo-root", ".")).resolve()
    write = "--write" in args
    book = repo / "book"
    ref = opts.get("--baseline")
    if not ref:
        bf = book / BASELINE_FILE
        if bf.is_file():
            ref = bf.read_text(encoding="utf-8").strip()
    if not ref:
        print("ERROR: 无基线 commit（给 --baseline 或写 book/.cite-baseline）", file=sys.stderr)
        return 2

    md_files = sorted((book / MANUSCRIPTS).glob("*.md"))
    healed = 0        # 平移已修
    already = 0       # 无需改
    review: list[dict] = []    # 锚失踪/歧义 — 硬失效
    semantic: list[dict] = []  # 锚在但邻域变了 — 建议核对语义
    per_file_rewrites: dict[Path, list[dict]] = {}

    for md in md_files:
        text = md.read_text(encoding="utf-8")
        for m in CITE.finditer(text):
            rel, s, e = m.group(1), int(m.group(2)), m.group(3)
            end = int(e) if e else None
            r = analyze_citation(repo, ref, rel, s, end)
            r["md"] = md.name
            if r["status"] == "resolved":
                if r["moved"]:
                    healed += 1
                    per_file_rewrites.setdefault(md, []).append(r)
                else:
                    already += 1
                if r.get("region_changed"):
                    semantic.append(r)
            elif r["status"] in ("file-new",):
                already += 1  # 基线后新增文件，行号即当前，视为无需改
            else:
                review.append(r)

    # 应用改写
    if mode == "heal" and write:
        for md, rws in per_file_rewrites.items():
            rmap = {(r["rel"], r["start"], r["end"]): (r["new_start"], r["new_end"])
                    for r in rws}
            text = md.read_text(encoding="utf-8")
            md.write_text(apply_rewrites(text, rmap), encoding="utf-8")

    # 报告
    print(f"基线={ref}  章节={len(md_files)}")
    print(f"引用: 无需改={already}  行号平移{'已修' if (mode=='heal' and write) else '待修'}={healed}  "
          f"硬失效={len(review)}  语义待核对={len(semantic)}")
    if healed and not (mode == "heal" and write):
        print("\n[行号平移 — 机械可修，跑 `heal --write`]")
        for r in [x for f in per_file_rewrites.values() for x in f][:40]:
            print(f"  {r['md']}: {r['rel']}:{r['start']} → :{r['new_start']}")
    if review:
        print("\n[硬失效 — 锚失踪或歧义，必须人工/LLM 复核]")
        for r in review:
            extra = f"  锚=`{r.get('anchor','')}`" if r.get("anchor") else ""
            print(f"  [{r['status']}] {r['md']}: {r['rel']}:{r['start']}{extra}")
    if semantic:
        print("\n[语义待核对 — 锚在但引用邻域被同步改动，正文可能失实]")
        for r in semantic:
            print(f"  {r['md']}: {r['rel']}:{r['start']}"
                  + (f"-{r['end']}" if r.get('end') else ""))

    if mode == "check":
        return 1 if review else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
