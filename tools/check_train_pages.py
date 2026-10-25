#!/usr/bin/env python3
"""Regenerates every train page that already exists and reports how many are byte-identical.
  python3 tools/check_train_pages.py catalog.json [--show N]"""
import collections, json, os, subprocess, sys, tempfile, difflib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cat = sys.argv[1]
show = int(sys.argv[sys.argv.index('--show') + 1]) if '--show' in sys.argv else 3
live = set(os.listdir(os.path.join(ROOT, 'train'))) - {'index.html'}
rows = [r for r in json.load(open(cat)) if r['number'] in live]
tmp = tempfile.mkdtemp()
json.dump(rows, open(os.path.join(tmp, 'sub.json'), 'w'))
subprocess.check_call([sys.executable, os.path.join(ROOT, 'tools/build_train_pages.py'), '--catalog', os.path.join(tmp, 'sub.json'), '--out', tmp])
same, bad = 0, []
rows = [r for r in rows if os.path.exists(os.path.join(tmp, 'train', r['number'], 'index.html'))]
for r in rows:
    a = open(os.path.join(ROOT, 'train', r['number'], 'index.html'), encoding='utf-8').read()
    b = open(os.path.join(tmp, 'train', r['number'], 'index.html'), encoding='utf-8').read()
    if a == b: same += 1
    else: bad.append(r['number'])
print('identical %d of %d' % (same, len(rows)))
kinds = collections.Counter()
for n in bad[:300]:
    a = open(os.path.join(ROOT, 'train', n, 'index.html'), encoding='utf-8').read().split('\n')
    b = open(os.path.join(tmp, 'train', n, 'index.html'), encoding='utf-8').read().split('\n')
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            kinds[(x[:28])] += 1; break
    else: kinds['length'] += 1
print(kinds.most_common(8))
for n in bad[:show]:
    a = open(os.path.join(ROOT, 'train', n, 'index.html'), encoding='utf-8').read().split('\n')
    b = open(os.path.join(tmp, 'train', n, 'index.html'), encoding='utf-8').read().split('\n')
    print('==', n)
    for x, y in zip(a, b):
        if x != y:
            sm = difflib.SequenceMatcher(None, x, y)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag != 'equal': print(tag, repr(x[max(0,i1-40):i2+40]), '=>', repr(y[max(0,j1-40):j2+40])); break
            break
