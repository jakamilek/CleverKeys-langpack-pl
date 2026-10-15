#!/usr/bin/env python3
"""Build exactly the user's accepted 1087 additions on immutable v11."""
import argparse,copy,json,math,hashlib
from pathlib import Path
from importlib.metadata import version,distribution
import wordfreq
from build_practical_candidate_modules import read_base,BASE_SHA,DICT_SHA,CompactPool,decode_entry
from build_common_forms_trial import extend_dictionary,parse_dictionary,WORDFREQ_COMMIT,MAX_BYTES,MAX_TOTAL_BYTES,MAX_ENTRIES,MAX_NODES
from build_shared_metadata_trial import serialize
from build_thematic_forms_trial import write_pack
from shared_metadata_v2 import nodes
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--base-pack',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
 assert version('wordfreq')=='3.2.0';assert json.loads(distribution('wordfreq').read_text('direct_url.json'))['vcs_info']['commit_id']==WORDFREQ_COMMIT
 src=ROOT/'source/approved-practical-v13';raw=(src/'approved.json').read_bytes();decision=json.loads((src/'decision.json').read_text());assert sha(raw)==decision['approvedSha256'];approved=json.loads(raw)
 assert len(approved)==1087 and len({r['surfaceKey'] for r in approved})==1087
 keys={r['surfaceKey'] for r in approved};assert not keys.intersection(decision['rejectedKeys']) and len(decision['rejectedKeys'])==269
 members,manifest,doc,old,aliases,boundary=read_base(a.base_pack.read_bytes(),BASE_SHA,DICT_SHA,11,3);baseline=copy.deepcopy(doc);cp=CompactPool(doc)
 assert not keys.intersection(w.lower() for w,_ in old)
 freq=lambda k:max(1.0,wordfreq.word_frequency(k,'pl')*1e8)
 max_freq=max(freq(k) for k,_ in old);additions=[]
 for r in approved:
  k=r['surfaceKey'];assert wordfreq.zipf_frequency(k,'pl')==r['zipf']
  rank=max(0,min(255,int((1-math.log(freq(k)+1)/math.log(max_freq+1))*255)))
  additions.append((k,rank));assert r['metadataEntry']['surfaceKey']==k
  decoded=decode_entry(cp,r['metadataEntry']);assert decoded['metadata']['sourceEvidence']['lexicalReadings']
 doc['entries']=sorted(doc['entries']+[r['metadataEntry'] for r in approved],key=lambda r:r['surfaceKey']);assert len(doc['entries'])==115386
 before={e['surfaceKey']:e for e in baseline['entries']};after={e['surfaceKey']:e for e in doc['entries']};assert all(after[k]==v for k,v in before.items());assert len(after)==len(doc['entries'])
 binary=extend_dictionary(members['dictionary.bin'],old,aliases,boundary,additions,freq);records,aa,_=parse_dictionary(binary);assert len(records)==205550 and records[:len(old)]==old
 doc['provenance']['dictionarySha256']=sha(binary)
 doc['provenance']['approvedPracticalV13']=dict(basePackSha256=BASE_SHA,approvedSha256=sha(raw),decisionSha256=sha((src/'decision.json').read_bytes()),accepted=1087,rejected=269,wordfreqCommit=WORDFREQ_COMMIT,baseVersion=11,omittedVersion=12)
 side=serialize(doc);assert nodes(doc)<=MAX_NODES and len(side)<=MAX_BYTES and len(doc['entries'])<=MAX_ENTRIES
 manifest.update(version=13,wordCount=len(records));manifest['languageIntelligence']['sha256']=sha(side)
 members['dictionary.bin']=binary;members['language-intelligence.json']=side;members['manifest.json']=json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()+b'\n'
 members['NOTICE.txt']+=b'\nV13: 1087 user-approved practical additions to v11; v12 omitted; 269 ambiguity candidates rejected. Existing words, ranks and source readings retained.\nSources: SGJP/Morfeusz snapshot and pinned wordfreq; factual external lexical links from WSJP and Dobry Slownik retain source URLs and sense identifiers in metadata. No copied dictionary definitions.\n'
 assert all(len(v)<=MAX_BYTES for v in members.values()) and sum(map(len,members.values()))<=MAX_TOTAL_BYTES
 pack=write_pack(members);assert pack==write_pack(members)
 name='cleverkeys-pl-practical-v13.zip';(a.out_dir/name).write_bytes(pack)
 report=dict(version=13,baseVersion=11,words=len(records),metadataEntries=len(doc['entries']),addedWords=1087,rejectedCandidates=269,metadataBytes=len(side),metadataNodes=nodes(doc),addedMetadataBytes=len(side)-len(serialize(baseline)),addedMetadataNodes=nodes(doc)-nodes(baseline),remainingEntries=MAX_ENTRIES-len(doc['entries']),remainingNodes=MAX_NODES-nodes(doc),remainingBytes=MAX_BYTES-len(side),sha256=sha(pack),dictionarySha256=sha(binary),baseSha256=BASE_SHA,allOldWordsRanksUnchanged=True,allOldMetadataUnchanged=True,oldAliasRelativeOrderUnchanged=True,unigramsUnchanged=True,sourceTablesUnchanged=all(doc[k]==baseline[k] for k in ['sourceAttributes','sourceLexemes']),reproducibleArchive=True)
 (a.out_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');(a.out_dir/'SHA256SUMS').write_text(sha(pack)+'  '+name+'\n');(a.out_dir/'approved-keys.txt').write_text(''.join(k+'\n' for k in sorted(keys)));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
