#!/usr/bin/env python3
"""Live search box on top of the /train/ page (28 Nov 2026).

  python3 tools/add_train_list_search.py [--write]

Puts a box (<!--tsearch-start-->...<!--tsearch-end-->) above the list of all trains on
/train/index.html. As the visitor types, the list shows only trains whose number or name
contains every typed word (any order, any case); no Enter, no waiting. Replaces its own block.
Re-run after any rebuild of /train/index.html.
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S, E = '<!--tsearch-start-->', '<!--tsearch-end-->'
BLOCK = S + r'''<div class="tsearch" style="margin-top:20px">
<label for="tsq" style="display:block;font-weight:600;color:var(--ink);margin-bottom:8px">Search all trains</label>
<input id="tsq" type="search" autocomplete="off" placeholder="Type a train number or name, e.g. 12301 or Rajdhani" style="width:100%;box-sizing:border-box;padding:14px 16px;border:1.5px solid var(--line);border-radius:12px;font:16px var(--font-body,system-ui);color:var(--ink);background:#fff">
<p id="tsn" aria-live="polite" style="margin-top:8px;font-size:14px;color:#7A819E"></p>
</div>
<script>
function tsInit(){
  var q=document.getElementById('tsq'),n=document.getElementById('tsn');
  var box=document.querySelector('.links');
  if(!q||!box)return;
  var links=[].slice.call(box.querySelectorAll('a')),hay=links.map(function(a){return a.textContent.toLowerCase()});
  function run(){
    var toks=q.value.toLowerCase().split(/\s+/).filter(Boolean),shown=0;
    for(var i=0;i<links.length;i++){
      var ok=true;for(var j=0;j<toks.length;j++){if(hay[i].indexOf(toks[j])<0){ok=false;break}}
      links[i].style.display=ok?'':'none';if(ok)shown++;
    }
    n.textContent=toks.length?(shown?shown+' train'+(shown===1?'':'s')+' found':'No train found. Try the train number, or check the '+'live status page.'):'';
  }
  q.addEventListener('input',run);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',tsInit);else tsInit();
</script>
''' + E


def main():
    p = os.path.join(ROOT, 'train', 'index.html')
    s = open(p, encoding='utf-8').read()
    s = re.sub(re.escape(S) + r'.*?' + re.escape(E) + r'\n?', '', s, flags=re.S)
    a = '<div class="links" style="margin-top:20px">'
    assert s.count(a) == 1, s.count(a)
    s = s.replace(a, BLOCK + a)
    if '--write' in sys.argv:
        open(p, 'w', encoding='utf-8').write(s)
        print('written')


if __name__ == '__main__':
    main()
