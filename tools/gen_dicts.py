#!/usr/bin/env python3
# 由青简官方开源词库(CC-BY-SA-4.0)生成运行时 键<TAB>译文 词库，并与现有干净词库合并（官方优先）
import os, re, hashlib, sys

BASE = r'C:\Users\Administrator\Desktop\中英对照表\官方源文件'
OUT = r'_c2-166\dict_out'
os.makedirs(OUT, exist_ok=True)
POS = re.compile(r'^[A-Za-z]+\.\s*')

def parse_glossary(path):
    m = {}
    dup = 0
    with open(path, encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip('\n')
            if not ln or ln.startswith('#'):
                continue
            cols = ln.split('\t')
            key = cols[0].strip()
            if not key:
                continue
            senses = []
            for c in cols[1:]:
                c = POS.sub('', c.strip()).strip()
                if c and c not in senses:
                    senses.append(c)
            if not senses:
                continue
            if key in m:
                dup += 1
                for s in senses:
                    if s not in m[key] and len(m[key]) < 3:
                        m[key].append(s)
            else:
                m[key] = senses[:3]
    return m, dup

def load_runtime(path):
    m = {}
    if not os.path.exists(path):
        return m
    with open(path, encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip('\n')
            if '\t' in ln:
                k, v = ln.split('\t', 1)
                m[k] = v
    return m

def merge_write(existing_path, official_map, out_path):
    base = load_runtime(existing_path)
    added = 0
    for k, senses in official_map.items():
        val = ', '.join(senses)
        if k not in base:
            base[k] = val  # 只补缺口，不改写已有干净词条（保证 eval 不降）
            added += 1
    keys = sorted(base.keys())
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        for k in keys:
            f.write(k + '\t' + base[k] + '\n')
    return len(base), added

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

zen, dup_en = parse_glossary(os.path.join(BASE, 'glossary-en.tsv'))
zhn, dup_zh = parse_glossary(os.path.join(BASE, 'glossary-zh.tsv'))

n_zh, add_zh = merge_write(r'_c2-166\zh2en.txt', zen, os.path.join(OUT, 'zh2en.txt'))
n_en, add_en = merge_write(r'_c2-166\en2zh.txt', zhn, os.path.join(OUT, 'en2zh.txt'))

def validate(p, label):
    raw = open(p, 'rb').read()
    assert not raw.startswith(b'\xef\xbb\xbf'), label + ' BOM'
    lines = raw.decode('utf-8').split('\n')
    if lines and lines[-1] == '': lines = lines[:-1]
    keys = []
    multi_tab = 0
    for ln in lines:
        if '\t' not in ln: raise SystemExit(label + ' no tab: ' + ln[:30])
        k, v = ln.split('\t', 1)
        if '\t' in v: multi_tab += 1
        keys.append(k)
    sorted_ok = keys == sorted(keys)
    dup = len(keys) - len(set(keys))
    print('%s lines=%d multi_tab=%d sorted=%s dup=%d' % (label, len(lines), multi_tab, sorted_ok, dup))
    return len(lines), sorted_ok, dup

lz, sz, dz = validate(os.path.join(OUT, 'zh2en.txt'), 'zh2en')
le, se, de = validate(os.path.join(OUT, 'en2zh.txt'), 'en2zh')

samples = ['你好','计算机','吃饭','葡萄','学生','hello','computer','apple','book','hello']
print('== samples ==')
for s in samples:
    for p in ['zh2en', 'en2zh']:
        pass
def lookup(p, k):
    with open(p, encoding='utf-8') as f:
        for ln in f:
            if ln.startswith(k + '\t'):
                return ln.rstrip('\n').split('\t', 1)[1]
    return None
for s in ['你好','计算机','吃饭','葡萄','学生','我在干什么']:
    print('zh2en', s, '->', lookup(os.path.join(OUT,'zh2en.txt'), s))
for s in ['hello','computer','apple','book','you']:
    print('en2zh', s, '->', lookup(os.path.join(OUT,'en2zh.txt'), s))

print('OFFICIAL', 'glossary-en tsv sha', sha(os.path.join(BASE,'glossary-en.tsv')))
print('OFFICIAL', 'glossary-zh tsv sha', sha(os.path.join(BASE,'glossary-zh.tsv')))
print('DONE zh=%d (add %d) en=%d (add %d) dup_en=%d dup_zh=%d' % (n_zh, add_zh, n_en, add_en, dup_en, dup_zh))
