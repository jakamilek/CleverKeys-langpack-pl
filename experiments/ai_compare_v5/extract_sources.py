"""Reproduce the snapshot from an exact v5 package; no inferred lexical attributes."""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path
from contract import ROOT,PACK_SHA,SIDECAR_SHA,canonical,validate_sources

def ckdt(raw):
    if raw[:4]!=b'CKDT' or struct.unpack_from('<I',raw,4)[0]!=2:
        raise ValueError('expected CKDT V2')
    count,start=struct.unpack_from('<II',raw,12)
    pos=start;out={}
    for _ in range(count):
        size=struct.unpack_from('<H',raw,pos)[0];pos+=2
        word=raw[pos:pos+size].decode('utf-8');pos+=size
        rank=raw[pos];pos+=1
        if word.lower() in out:raise ValueError('duplicate CKDT key')
        out[word.lower()]={'surface':word,'rank':rank}
    return out

def extract(pack,cases):
    raw=pack.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PACK_SHA:raise ValueError('wrong exact package')
    with zipfile.ZipFile(pack) as z:
        sidecar=z.read('language-intelligence.json')
        if hashlib.sha256(sidecar).hexdigest()!=SIDECAR_SHA:raise ValueError('wrong sidecar')
        intelligence=json.loads(sidecar);dictionary=ckdt(z.read('dictionary.bin'))
    supplied={e['surfaceKey']:e for e in intelligence['entries']}
    keys=sorted({s['key'] for c in cases['cases'] for s in c.get('candidates',[])})
    entries=[];fallback=[]
    for key in keys:
        if key not in dictionary:raise ValueError('slate key missing in exact pack: '+key)
        if key in supplied:entry=supplied[key]
        else:
            surface=dictionary[key]['surface'];fallback.append(key)
            entry={'surfaceKey':key,'canonicalForm':surface,'capitalization':{
                'defaultSurface':surface,'variants':[{'surface':surface,
                'casePolicy':'lowercase' if surface==key else 'capitalized'}]}}
        entries.append(entry)
    snapshot={'schemaVersion':1,'packSha256':PACK_SHA,'sidecarSha256':SIDECAR_SHA,
              'producerCommit':'041b28ae4587c531ef73e62933e9151cadb84c33',
              'runtimeMetadataEntries':len(intelligence['entries']),
              'dictionaryWordCount':len(dictionary),'canonicalOnlyKeys':fallback,
              'sourceProvenance':intelligence['provenance'],'entries':entries}
    validate_sources(snapshot)
    return snapshot

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,required=True)
    p.add_argument('--verify',action='store_true');a=p.parse_args()
    result=canonical(extract(a.pack,json.loads((ROOT/'cases.json').read_text())))+b'\n'
    target=ROOT/'source-snapshot.json'
    if a.verify:
        if target.read_bytes()!=result:raise ValueError('snapshot mismatch')
    else:target.write_bytes(result)
    print(len(result),hashlib.sha256(result).hexdigest())
