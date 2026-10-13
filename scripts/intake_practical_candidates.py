#!/usr/bin/env python3
"""Freeze public source candidates, not importable words or manually invented senses."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

UA = 'CleverKeysPL-lexical-candidates/1.0 (source audit; no editor data)'
INDEX_TITLES = ['Indeks:Polski - Informatyka', 'Indeks:Polski - Technika', 'Indeks:Polski - Slang']
CATEGORY_TITLES = ['Kategoria:Komunikatory internetowe', 'Kategoria:Serwisy społecznościowe',
                   'Kategoria:Chatboty', 'Kategoria:Usługi strumieniowania muzyki']


def fetch(host, params):
    url = 'https://' + host + '/w/api.php?' + urllib.parse.urlencode(dict(format='json', formatversion=2, **params))
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=25) as response:
        raw = response.read(16*1024*1024+1)
    if len(raw)>16*1024*1024: raise ValueError('source response budget')
    result = json.loads(raw)
    if 'error' in result: raise ValueError(result['error'])
    return raw, result, url



def project_entities(data):
    """Retain literal identity, labels and the two claims actually used in the audit."""
    return dict(entities={qid:{**{k:e[k] for k in ['id','type','lastrevid','modified','missing','labels'] if k in e},
        'claims':{p:[{k:c[k] for k in ['id','rank','mainsnak'] if k in c} for c in e.get('claims',{}).get(p,[])]
                  for p in ['P31','P856'] if p in e.get('claims',{})}} for qid,e in data['entities'].items()})


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    if (a.out/'intake-lock.json').exists(): raise ValueError('source lock already exists')
    lock=[];groups=[];page_categories={};article_titles={}
    def save(name,raw,url,kind,**details):
        (a.out/name).write_bytes(raw)
        lock.append(dict(path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),url=url,kind=kind,**details))
    for i,title in enumerate(INDEX_TITLES):
        raw,data,url=fetch('pl.wiktionary.org',dict(action='query',prop='revisions',rvprop='ids|timestamp|content',rvslots='main',titles=title))
        page=data['query']['pages'][0]
        if page.get('missing'): raise ValueError('Missing source index: '+title)
        rev=page['revisions'][0]
        save(f'index-{i}.json',raw,url,'wiktionary-index',title=title,revision=rev['revid'],revisionTimestamp=rev['timestamp'])
        print(title,rev['revid'],flush=True)
    for i,title in enumerate(CATEGORY_TITLES):
        cont={};batch=0
        while True:
            raw,data,url=fetch('pl.wikipedia.org',dict(action='query',list='categorymembers',cmtitle=title,cmtype='page',cmlimit='max',**cont))
            rows=data['query']['categorymembers']
            if not rows and not cont: raise ValueError('Empty source category: '+title)
            for row in rows:
                page_categories.setdefault(row['pageid'],set()).add(title);article_titles[row['pageid']]=row['title']
            save(f'category-{i}-{batch}.json',raw,url,'wikipedia-category-membership',title=title)
            if 'continue' not in data: break
            cont=data['continue'];batch+=1
            if batch>10:raise ValueError('category paging budget')
        print(title,'frozen',flush=True)
    pageids=sorted(page_categories);entities=set()
    for start in range(0,len(pageids),40):
        raw,data,url=fetch('pl.wikipedia.org',dict(action='query',prop='pageprops|revisions',rvprop='ids|timestamp',pageids='|'.join(map(str,pageids[start:start+40]))))
        for page in data['query']['pages']:
            q=page.get('pageprops',{}).get('wikibase_item')
            if q:entities.add(q)
        save(f'articles-{start//40}.json',raw,url,'wikipedia-article-identities')
    qids=sorted(entities,key=lambda q:int(q[1:]))
    for start in range(0,len(qids),30):
        raw,data,url=fetch('www.wikidata.org',dict(action='wbgetentities',ids='|'.join(qids[start:start+30]),props='labels|claims|info',languages='pl|en'))
        projected=(json.dumps(project_entities(data),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
        save(f'entities-{start//30}.json',projected,url,'wikidata-entity-projection',
             originalResponseSha256=hashlib.sha256(raw).hexdigest(),originalResponseBytes=len(raw),
             projectedFields=['identity','labels-pl-en','P31-mainsnaks','P856-mainsnaks'])
    (a.out/'intake-lock.json').write_text(json.dumps(dict(retrievedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        categorySnapshotScope='direct pages only; membership frozen by response SHA, not category-page revision',
        selection=dict(indexTitles=INDEX_TITLES,categoryTitles=CATEGORY_TITLES,categoryRecursion=False,manualWordSeeds=False),
        files=lock),ensure_ascii=False,indent=2)+'\n')
    print('Frozen',len(lock),'responses;',len(pageids),'articles;',len(qids),'entities',flush=True)


if __name__=='__main__':main()
