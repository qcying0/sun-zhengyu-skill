# -*- coding: utf-8 -*-
"""三学者文体对比：同一脚本、同一口径。用法: python compare.py"""
import os, re, statistics, sys

SENT_END = "。！？"
CLOSERS = "”’」』）"

def split_sents(para):
    out, buf, i, n = [], [], 0, len(para)
    while i < n:
        ch = para[i]; buf.append(ch)
        if ch in SENT_END:
            j = i + 1
            while j < n and para[j] in CLOSERS:
                buf.append(para[j]); j += 1
            out.append("".join(buf)); buf = []; i = j; continue
        i += 1
    if buf: out.append("".join(buf))
    return [s.strip() for s in out if s.strip()]

def chars(s): return len(re.sub(r"\s", "", s))

def analyze(files):
    text = ""
    for f in files:
        text += open(f, encoding="utf-8", errors="ignore").read() + "\n"
    paras = [p.strip() for p in text.split("\n") if p.strip() and chars(p) > 20]
    sents = []
    for p in paras: sents += split_sents(p)
    sl = [chars(s) for s in sents]
    n = chars(text)
    r = {}
    r["字数"] = n; r["句数"] = len(sents); r["段数"] = len(paras)
    r["句长均值"] = round(sum(sl)/len(sl), 1)
    r["句长中位"] = round(statistics.median(sl), 1)
    r[">100%"] = round(100*sum(1 for x in sl if x > 100)/len(sl), 1)
    r[">150%"] = round(100*sum(1 for x in sl if x > 150)/len(sl), 1)
    r["<30%"] = round(100*sum(1 for x in sl if x < 30)/len(sl), 1)
    r["段均字"] = round(sum(chars(p) for p in paras)/len(paras), 0)
    r["问句%"] = round(100*sum(1 for s in sents if "？" in s)/len(sl), 1)
    r["引号/千"] = round(1000*text.count("“")/n, 1)
    r["顿号/千"] = round(1000*text.count("、")/n, 1)
    r["分号/千"] = round(1000*text.count("；")/n, 1)
    r["破折/千"] = round(1000*text.count("——")/n, 1)
    r["感叹/千"] = round(1000*text.count("！")/n, 1)
    r["逗号/句"] = round(text.count("，")/len(sl), 2)
    for name, rx in {"不仅…而且": r"不仅[^。；！？]{0,40}?而且",
                     "既…又": r"既[^。；！？]{0,25}?又",
                     "不是…而是": r"不是[^。；！？]{0,40}?而是",
                     "所谓": r"所谓", "也就是说": r"也就是说",
                     "第一/其一": r"第一|其一"}.items():
        r[name+"/万字"] = round(10000*len(re.findall(rx, text))/n, 1)
    return r

BASE = "C:/Users/yingqc/.workbuddy-ai/skills"
sets = {
    "孙正聿": sorted(os.path.join(BASE, "sun-zhengyu-perspective/references/sources/articles", f)
                for f in os.listdir(os.path.join(BASE, "sun-zhengyu-perspective/references/sources/articles")) if f.endswith(".txt")),
    "何中华": sorted(os.path.join(BASE, "he-zhonghua-perspective/references/sources/articles", f)
                for f in os.listdir(os.path.join(BASE, "he-zhonghua-perspective/references/sources/articles"))
                if f.endswith(".txt") and "interview" not in f),
    "王韶兴": sorted(os.path.join(BASE, "wang-shaoxing-perspective/references/sources/articles", f)
                for f in os.listdir(os.path.join(BASE, "wang-shaoxing-perspective/references/sources/articles")) if f.endswith(".txt")),
}
res = {k: analyze(v) for k, v in sets.items()}
cols = list(next(iter(res.values())).keys())
print("指标\t" + "\t".join(res.keys()))
for c in cols:
    print(c + "\t" + "\t".join(str(res[k][c]) for k in res))
print()
for k, v in sets.items():
    print(k, "篇数=", len(v))
