#!/usr/bin/env python3
"""Station / train finder in the footer of the home page (28 Nov 2026).

  python3 tools/add_footer_finder.py [--write]

1. Writes /search-index.json from the live pages: every /train/<no>/ page (number, name)
   and every /station/<code>/ page (code, name).
2. Puts a search box (<!--finder-start-->...<!--finder-end-->) above "Track a popular train"
   in the footer of /index.html. Typing a station name/code or train number/name lists
   matches that link to /station/<code>/ and /train/<no>/. The index loads only when the
   box is first used.
Re-run after any rebuild of the train / station pages (it refreshes the index and replaces its own block).
"""
import glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S, E = '<!--finder-start-->', '<!--finder-end-->'

BLOCK = S + r'''
    <div class="ffind" id="ffind">
      <h5>Find your station or train</h5>
      <label class="sr" for="ffq">Station name or code, train number or name</label>
      <input id="ffq" type="search" autocomplete="off" placeholder="Station (Kanpur or CNB) or train (12301 or Rajdhani)" aria-controls="ffres">
      <div id="ffres" aria-live="polite"></div>
    </div>
    <style>
    .ffind{margin-top:30px}.ffind h5{color:#fff;font:600 16px var(--font-head);margin-bottom:12px}
    .ffind .sr{position:absolute;left:-9999px}
    .ffind input{width:100%;max-width:560px;box-sizing:border-box;padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.08);color:#fff;font:16px var(--font-body)}
    .ffind input::placeholder{color:rgba(255,255,255,.6)}
    .ffind input:focus{outline:2px solid #fff;outline-offset:2px}
    #ffres{margin-top:12px;display:grid;gap:14px;max-width:760px}
    #ffres h6{color:rgba(255,255,255,.7);font:600 12px var(--font-body);letter-spacing:.06em;text-transform:uppercase;margin-bottom:8px}
    #ffres div{display:flex;flex-wrap:wrap;gap:8px}
    #ffres a{border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:6px 12px;font-size:13px}
    #ffres p{color:rgba(255,255,255,.75);font-size:14px}
    </style>
    <script>
    (function(){
      var q=document.getElementById('ffq'),out=document.getElementById('ffres'),idx=null,loading=false,wait=[];
      function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
      function load(cb){
        if(idx){cb();return}
        wait.push(cb);
        if(loading)return;loading=true;
        fetch('/search-index.json').then(function(r){return r.json()}).then(function(j){
          idx={t:j.t.map(function(x){return {k:x[0],n:x[1],h:(x[0]+' '+x[1]).toLowerCase()}}),
               s:j.s.map(function(x){return {k:x[0],n:x[1],h:(x[0]+' '+x[1]).toLowerCase()}})};
          loading=false;var w=wait;wait=[];w.forEach(function(f){f()});
        }).catch(function(){loading=false;wait=[];out.innerHTML='<p>Search could not load. Please try again.</p>'});
      }
      function rank(list,toks,raw){
        var res=[];
        for(var i=0;i<list.length;i++){
          var e=list[i],ok=true;
          for(var j=0;j<toks.length;j++){if(e.h.indexOf(toks[j])<0){ok=false;break}}
          if(!ok)continue;
          var kl=e.k.toLowerCase(),nl=e.n.toLowerCase(),sc=3;
          if(kl===raw)sc=0;else if(kl.indexOf(raw)===0||nl.indexOf(raw)===0)sc=1;else if((' '+nl).indexOf(' '+toks[0])>=0)sc=2;
          res.push([sc,e]);
        }
        res.sort(function(a,b){return a[0]-b[0]||(a[1].n<b[1].n?-1:1)});
        return res.slice(0,8).map(function(x){return x[1]});
      }
      function show(){
        var raw=q.value.trim().toLowerCase();
        if(raw.length<2){out.innerHTML='';return}
        load(function(){
          var toks=raw.split(/\s+/),st=rank(idx.s,toks,raw),tr=rank(idx.t,toks,raw),h='';
          if(st.length)h+='<section><h6>Stations</h6><div>'+st.map(function(e){return '<a href="/station/'+e.k.toLowerCase()+'/">'+esc(e.n)+' ('+esc(e.k)+')</a>'}).join('')+'</div></section>';
          if(tr.length)h+='<section><h6>Trains</h6><div>'+tr.map(function(e){return '<a href="/train/'+e.k+'/">'+esc(e.k+' '+e.n)+'</a>'}).join('')+'</div></section>';
          out.innerHTML=h||'<p>No station or train found for &ldquo;'+esc(q.value.trim())+'&rdquo;.</p>';
        });
      }
      q.addEventListener('focus',function(){load(function(){})},{once:true});
      q.addEventListener('input',show);
      q.addEventListener('keydown',function(ev){if(ev.key==='Enter'){var a=out.querySelector('a');if(a){ev.preventDefault();location.href=a.getAttribute('href')}}});
    })();
    </script>
''' + E


def main():
    write = '--write' in sys.argv
    trains = []
    for f in glob.glob(os.path.join(ROOT, 'train', '*', 'index.html')):
        n = os.path.basename(os.path.dirname(f))
        s = open(f, encoding='utf-8').read()
        h = re.search(r'<h1>(\d+) (.*?): live running status</h1>', s)
        if h:
            trains.append([n, html.unescape(h.group(2))])
    stations = []
    for f in glob.glob(os.path.join(ROOT, 'station', '*', 'index.html')):
        c = os.path.basename(os.path.dirname(f)).upper()
        s = open(f, encoding='utf-8').read()
        h = re.search(r'<h1>Trains at (.*?) \(', s)
        if h:
            stations.append([c, html.unescape(h.group(1))])
    trains.sort(); stations.sort()
    print('trains', len(trains), 'stations', len(stations))
    if not write:
        return
    with open(os.path.join(ROOT, 'search-index.json'), 'w', encoding='utf-8') as fh:
        json.dump({'t': trains, 's': stations}, fh, ensure_ascii=False, separators=(',', ':'))
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    s = re.sub(re.escape(S) + r'.*?' + re.escape(E) + r'\n?', '', s, flags=re.S)
    a = '    <div class="ftrains">'
    assert s.count(a) == 1
    s = s.replace(a, BLOCK + '\n' + a)
    open(p, 'w', encoding='utf-8').write(s)
    print('written')


if __name__ == '__main__':
    main()
