# -*- coding: utf-8 -*-
"""
孙正聿 表达风格 DNA —— 统计脚本（v2）
用法: python expression_stats.py <articles_dir>
所有数字均由本脚本实际计算，不做任何估计。
"""
import os, re, sys, statistics
from collections import Counter

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

META = {
    "A-01": dict(title="标准与选择：我们时代的哲学理念", year=2017, genre="报刊长文", place="爱思想转载"),
    "A-02": dict(title="自主知识体系的标识性概念", year=2026, genre="报纸理论版", place="光明日报"),
    "A-03": dict(title="哲学的追求", year=2023, genre="报纸理论版", place="光明日报"),
    "A-04": dict(title="哲学社会科学研究怎样面向现实", year=2024, genre="报纸理论版", place="人民日报"),
    "A-05": dict(title="哲学之为哲学：“不是问题”的“基本问题”", year=2011, genre="学术论文", place="期刊"),
    "A-06": dict(title="理论思维的前提批判·导言（节选）", year=1990, genre="学术专著", place="北师大版重印"),
    "A-07": dict(title="“知其不可而为之”——孙正聿教授访谈录", year=2008, genre="访谈（口语）", place="晋阳学刊"),
}

SENT_END = "。！？"
CLOSERS = "”’」』）"
HEAD_RE = re.compile(r"^[一二三四五六七八九十]+、")

def load(fn):
    with open(os.path.join(DIR, fn), encoding="utf-8") as f:
        return f.read()

def paragraphs(text):
    return [p.strip() for p in text.split("\n") if p.strip()]

def split_sents(para):
    out, buf, i, n = [], [], 0, len(para)
    while i < n:
        ch = para[i]
        buf.append(ch)
        if ch in SENT_END:
            j = i + 1
            while j < n and para[j] in CLOSERS:
                buf.append(para[j]); j += 1
            out.append("".join(buf)); buf = []
            i = j
            continue
        i += 1
    if buf:
        out.append("".join(buf))
    return [s.strip() for s in out if s.strip()]

def chars(s):
    return len(re.sub(r"\s", "", s))

RE_DUIJU = {
    "不仅…而且": r"不仅[^。；！？]{0,40}?而且",
    "既…又": r"既[^。；！？]{0,25}?又",
    "不是…而是": r"不是[^。；！？]{0,40}?而是",
}
RE_DUIJU_WIDE = {
    "不仅…而且宽80": r"不仅[^。；！？]{0,80}?而且",
    "既…又宽60": r"既[^。；！？]{0,60}?又",
    "不是…而是宽80": r"不是[^。；！？]{0,80}?而是",
}
UPPER_WORDS = {"不仅…而且": "不仅", "既…又": "既", "不是…而是": "而是"}

STRUCT_WORDS = ["首先","其次","再次","最后","第一","第二","第三","总之","因此","但是","然而","不过",
                "同时","另一方面","也就是说","换言之","事实上","当然","只有","才能","必须","应当",
                "需要","关键在于","本质上","根本","归根到底","所谓","不是"]

PHILO_WORDS = ["前提","批判","反思","超越","本体","存在","思","真理","自由","必然","主体","客体",
               "辩证法","历史性","现代性","形而上学","理论思维","常识","科学","哲学观"]

WEST = ["马克思","恩格斯","黑格尔","列宁","康德","海德格尔","尼采","亚里士多德","柏拉图","笛卡尔",
        "胡塞尔","蒯因","赖欣巴哈","瓦托夫斯基","卡尔纳普","海德格尔"]
CN = ["孔子","孟子","老子","庄子","高清海","冯友兰","王国维","李大钊","贺麟","苏东坡","陈子昂"]

rows, corpus = [], {}
for fn in sorted(os.listdir(DIR)):
    if not fn.startswith("A-") or not fn.endswith(".txt"):
        continue
    key = fn[:4]
    text = load(fn)
    paras_all = paragraphs(text)
    def is_head(p):
        if HEAD_RE.match(p) and chars(p) <= 30:
            return True
        # 无句末标点且极短的独立段落，按小标题处理
        if chars(p) <= 20 and not any(c in p for c in "。！？"):
            return True
        return False
    heads = [p for p in paras_all if is_head(p)]
    paras = [p for p in paras_all if not is_head(p)]
    sents, sent_para = [], []
    for pi, p in enumerate(paras):
        ss = split_sents(p)
        sents += ss
        sent_para += [pi] * len(ss)
    slen = [chars(s) for s in sents]
    corpus[key] = dict(text=text, paras=paras, sents=sents, slen=slen, sent_para=sent_para)

    n_char = chars(text)
    n_s = len(sents)
    d = dict(key=key, fn=fn, **META[key])
    d["字数"] = n_char
    d["句数"] = n_s
    d["段数"] = len(paras)
    d["小标题数"] = len(heads)
    d["句长均值"] = round(sum(slen)/n_s, 2)
    d["句长中位"] = round(statistics.median(slen), 1)
    d["句长最长"] = max(slen)
    d["句长最短"] = min(slen)
    d[">100字句"] = sum(1 for x in slen if x > 100)
    d[">150字句"] = sum(1 for x in slen if x > 150)
    d["<30字句"] = sum(1 for x in slen if x < 30)
    d[">100占比"] = round(100*d[">100字句"]/n_s, 1)
    d[">150占比"] = round(100*d[">150字句"]/n_s, 1)
    d["<30占比"] = round(100*d["<30字句"]/n_s, 1)
    plen = [chars(p) for p in paras]
    d["段均字数"] = round(sum(plen)/len(plen), 1)
    d["段长中位"] = round(statistics.median(plen), 1)
    d["段最长"] = max(plen)
    d["每段句数"] = round(n_s/len(paras), 2)
    d[">400字段落占比"] = round(100*sum(1 for x in plen if x > 400)/len(paras), 1)
    d["每句逗号数"] = round(text.count("，")/n_s, 2)

    punct = {"，":"逗号","；":"分号","、":"顿号","：":"冒号","“":"引号对","（":"括号对","——":"破折号","？":"问号","！":"感叹号"}
    for ch, name in punct.items():
        c = text.count(ch)
        d["P:"+name] = c
        d["D:"+name] = round(1000*c/n_char, 2)

    for w in STRUCT_WORDS:
        d["S:"+w] = text.count(w)
    for name, rx in RE_DUIJU.items():
        d["DJ:"+name] = len(re.findall(rx, text))
    for name, rx in RE_DUIJU_WIDE.items():
        d["DJW:"+name] = len(re.findall(rx, text))
    for name, w in UPPER_WORDS.items():
        d["DJU:"+name] = text.count(w)
    for w in PHILO_WORDS:
        d["PH:"+w] = text.count(w)
    for w in WEST:
        d["W:"+w] = text.count(w)
    for w in CN:
        d["C:"+w] = text.count(w)

    qs = [s for s in sents if "？" in s]
    d["问句数"] = len(qs)
    d["问句占比"] = round(100*len(qs)/n_s, 1)
    # 设问后是否即答：问句所在段落中，其后是否还有陈述句
    answered = 0
    for s in qs:
        pi = sent_para[sents.index(s)]
        idx = [i for i, x in enumerate(sents) if sent_para[i] == pi]
        pos = idx.index(sents.index(s))
        if pos < len(idx)-1 and "？" not in sents[idx[pos+1]]:
            answered += 1
    d["问后即答"] = answered
    d["问后即答占比"] = round(100*answered/len(qs), 1) if qs else 0
    d["Q:何谓"] = len(re.findall(r"何谓", text))
    d["Q:何以可能"] = len(re.findall(r"何以可能", text))
    d["Q:是什么？"] = len(re.findall(r"是什么？", text))
    d["Q:为什么"] = len(re.findall(r"为什么", text))
    d["Q:难道"] = len(re.findall(r"难道", text))
    d["Q:不就是"] = len(re.findall(r"不就是", text))
    d["Q:么？"] = len(re.findall(r"么？", text))
    d["Q:吗？"] = len(re.findall(r"吗？", text))
    d["Q:呢？"] = len(re.findall(r"呢？", text))
    d["BI:像/如同/犹如/仿佛/好比"] = len(re.findall(r"像|如同|犹如|仿佛|好比", text))
    d["COLON:一是"] = len(re.findall(r"一是", text))
    d["COLON:其一"] = len(re.findall(r"其一", text))
    d["QUOTE:所谓“"] = len(re.findall(r"所谓“", text))
    d["QUOTE:“即”展开"] = len(re.findall(r"”[^。]{0,6}即", text))
    rows.append(d)

# 引号内容
all_text = "\n".join(c["text"] for c in corpus.values())
quoted = re.findall(r"“([^”]{1,300})”", all_text)
qlen = [chars(q) for q in quoted]
qb = {"1字":0, "2-4字":0, "5-10字":0, "11-20字":0, ">20字":0}
for x in qlen:
    if x == 1: qb["1字"] += 1
    elif x <= 4: qb["2-4字"] += 1
    elif x <= 10: qb["5-10字"] += 1
    elif x <= 20: qb["11-20字"] += 1
    else: qb[">20字"] += 1

def table(title, cols):
    print("\n" + "=" * 110)
    print(title)
    print("=" * 110)
    print("\t".join(cols))
    for r in rows:
        print("\t".join(str(r.get(c, "")) for c in cols))

table("【一】样本总表", ["key","year","genre","字数","句数","段数","小标题数","句长均值","句长中位","句长最长","句长最短",
      ">100字句",">100占比",">150字句",">150占比","<30字句","<30占比","段均字数","段长中位","段最长","每段句数",">400字段落占比","每句逗号数"])
table("【二】标点密度（每千字）", ["key"]+["D:"+n for n in ["逗号","分号","顿号","冒号","引号对","括号对","破折号","问号","感叹号"]])
table("【二b】标点绝对数", ["key"]+["P:"+n for n in ["逗号","分号","顿号","冒号","引号对","括号对","破折号","问号","感叹号"]])
table("【三】对举句式", ["key","DJ:不仅…而且","DJW:不仅…而且宽80","DJU:不仅…而且","DJ:既…又","DJW:既…又宽60","DJU:既…又",
      "DJ:不是…而是","DJW:不是…而是宽80","DJU:不是…而是"])
table("【四】结构词频", ["key"]+["S:"+w for w in STRUCT_WORDS])
table("【五】哲学词汇", ["key"]+["PH:"+w for w in PHILO_WORDS])
table("【六】人物引用", ["key"]+["W:"+w for w in WEST]+["C:"+w for w in CN])
table("【七】设问语气", ["key","问句数","问句占比","问后即答","问后即答占比","Q:何谓","Q:何以可能","Q:是什么？","Q:为什么","Q:难道","Q:不就是","Q:么？","Q:吗？","Q:呢？","BI:像/如同/犹如/仿佛/好比","COLON:一是","COLON:其一","QUOTE:所谓“","QUOTE:“即”展开"])

print("\n" + "=" * 110)
print("【八】引号内容长度分布（全语料合并）")
print("=" * 110)
tot = sum(qb.values())
print("引号对数 =", tot, "分布 =", qb, "占比% =", {k: round(100*v/tot,1) for k,v in qb.items()})
print("引号内平均字数 =", round(sum(qlen)/len(qlen), 2))

print("\n【九】分体裁汇总（加权）")
groups = {}
for r in rows:
    groups.setdefault(r["genre"], []).append(r)
for g, rs in groups.items():
    tot_c = sum(x["字数"] for x in rs)
    tot_s = sum(x["句数"] for x in rs)
    tot_p = sum(x["段数"] for x in rs)
    wavg = sum(x["句长均值"]*x["句数"] for x in rs)/tot_s
    print(f"  {g}: 篇数={len(rs)} 字数={tot_c} 句数={tot_s} 加权句长均值={wavg:.1f} "
          f">100占比={100*sum(x['>100字句'] for x in rs)/tot_s:.1f}% <30占比={100*sum(x['<30字句'] for x in rs)/tot_s:.1f}% "
          f"段均字数={tot_c/tot_p:.0f} 每段句数={tot_s/tot_p:.2f} 问句占比={100*sum(x['问句数'] for x in rs)/tot_s:.1f}% "
          f"引号密度={1000*sum(x['P:引号对'] for x in rs)/tot_c:.1f} 顿号密度={1000*sum(x['P:顿号'] for x in rs)/tot_c:.1f}")

print("\n【十】最长句样本（每篇 top3）")
for k, c in corpus.items():
    idx = sorted(range(len(c["slen"])), key=lambda i: -c["slen"][i])[:3]
    print("\n---", k, META[k]["title"])
    for i in idx:
        print("  [%d字] %s" % (c["slen"][i], c["sents"][i][:120]))
