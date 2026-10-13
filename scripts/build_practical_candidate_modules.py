#!/usr/bin/env python3
"""Prepare auditable candidate modules against accepted v11; never build a langpack."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import zipfile

from build_common_forms_trial import (ordinary, selected, compact_entry, WORDFREQ_COMMIT,
    SourceOracle, MORFEUSZ_VERSION, DICTIONARY_ID)
from build_compact_names_trial import CompactPool
from build_compact_source_trial import decode_entry
from build_deferred_names_trial import read_base
from build_pl_preview import is_candidate
from build_thematic_forms_trial import write_pack
from build_variant_trial import canonical_bytes, read_json, sha256
from shared_metadata_v2 import nodes

BASE_SHA='8169a8ac33261fc245d46a344193759a0c1a84b0eb49cf2436e46ccaed90a229'
DICT_SHA='c8c3870be1aaaeee0cd20f47e7e807b45897024dd032bccd45358cf70d8e4cdc'
BUNDLE_NAME='cleverkeys-pl-practical-candidates.zip'


def key_shape(surface):
    if not surface or surface!=surface.strip(): return 'invalid-surface'
    if is_candidate(surface.lower()): return 'single-key'
    if any(c.isspace() for c in surface): return 'phrase-no-splitting'
    return 'punctuation-or-unsupported-key'


def link_targets(text):
    """Complete source targets; no labels, guessed stems or phrase components."""
    result=set()
    for link in re.findall(r'\[\[([^\[\]]+)\]\]',text):
        target=link.split('|',1)[0].split('#',1)[0].strip()
        if target and ':' not in target:result.add(target)
    return sorted(result)


def lexical_matches(key,evidence):
    lower={p['interpretationId'] for p in evidence['generatedFormProofs'] if p['form']==key}
    return [r for r in evidence['interpretations'] if r['id'] in lower and ordinary(r)]


def read_snapshot(directory):
    raw=(directory/'intake-lock.json').read_bytes(); lock=read_json(raw)
    files=[]
    for row in lock['files']:
        if Path(row['path']).name!=row['path']:raise ValueError('source path')
        data=(directory/row['path']).read_bytes()
        if len(data)!=row['bytes'] or sha256(data)!=row['sha256']:raise ValueError('source checksum')
        files.append((row,read_json(data)))
    return lock,files,sha256(raw)


def source_candidates(files):
    terms=defaultdict(list); members=defaultdict(set); pages={};entities={}
    for meta,data in files:
        kind=meta['kind']
        if kind=='wiktionary-index':
            for page in data['query']['pages']:
                rev=page['revisions'][0];text=rev['slots']['main']['content']
                for surface in link_targets(text):terms[surface.lower()].append(dict(surface=surface,
                    title=page['title'],revision=rev['revid'],url='https://pl.wiktionary.org/w/index.php?oldid='+str(rev['revid']),snapshot=meta['path']))
        elif kind=='wikipedia-category-membership':
            for p in data['query']['categorymembers']:members[p['pageid']].add(meta['title'])
        elif kind=='wikipedia-article-identities':
            for p in data['query']['pages']:pages[p['pageid']]=p
        elif kind in {'wikidata-entities','wikidata-entity-projection'}:entities.update(data['entities'])
    names=defaultdict(list)
    for pid,categories in sorted(members.items()):
        page=pages[pid];qid=page.get('pageprops',{}).get('wikibase_item');entity=entities.get(qid,{})
        labels=entity.get('labels',{});label=labels.get('pl') or labels.get('en')
        # Missing labels remain article-title candidates, including disambiguation text.
        # No stripping parentheses or inventing canonical spellings.
        surface=label['value'] if label else page['title'];rev=page['revisions'][0]
        websites=[];types=[]
        for property,target in [('P856',websites),('P31',types)]:
            for claim in entity.get('claims',{}).get(property,[]):
                snak=claim['mainsnak'];value=snak.get('datavalue',{}).get('value')
                if snak.get('snaktype')=='value':target.append(value)
        names[surface.lower()].append(dict(surface=surface,labelLanguage=label['language'] if label else None,
            pageId=pid,articleTitle=page['title'],articleRevision=rev['revid'],
            url='https://pl.wikipedia.org/w/index.php?oldid='+str(rev['revid']),categories=sorted(categories),
            wikidataId=qid,wikidataRevision=entity.get('lastrevid'),officialWebsiteClaims=websites,instanceOfClaims=types))
    return terms,names


def capacity(records):
    valid=[r for r in records if r['keyShape']=='single-key' and not r['inBase']]
    estimates=[r['runtimeEstimate'] for r in valid if r['runtimeEstimate'] is not None]
    return dict(records=len(records),uniqueKeys=len(records),baseOverlap=sum(r['inBase'] for r in records),
        newSingleKeys=len(valid),newOtherShapes=sum(not r['inBase'] and r['keyShape']!='single-key' for r in records),
        statusCounts=dict(sorted(Counter(r['status'] for r in records).items())),
        estimatedRecords=len(estimates),estimatedNodes=sum(e['nodes'] for e in estimates),
        estimatedBytes=sum(e['bytes'] for e in estimates),unestimatedRecords=len(valid)-len(estimates))


def candidates_from_sources(source_map,module,base,pool,oracle,zipf):
    result=[]
    for key,proofs in sorted(source_map.items()):
        spellings=sorted({p['surface'] for p in proofs});shape=key_shape(key);exists=key in base
        evidence=oracle.evidence(key) if shape=='single-key' else None
        matches=lexical_matches(key,evidence) if evidence else []
        proposal=None;estimate=None
        if matches:
            proposal=pool.encode(compact_entry(key,evidence));estimate=dict(nodes=nodes(proposal),bytes=len(canonical_bytes(proposal)))
        status=('already-in-v11' if exists else 'needs-non-single-key-support' if shape!='single-key' else
            'source-attested-ordinary-review' if matches and module=='digital-terms' else
            'needs-name-spelling-and-usage-review' if module=='apps-and-services' else 'needs-lexical-and-morphology-review')
        result.append(dict(surfaceKey=key,sourceSpellings=spellings,keyShape=shape,inBase=exists,
            status=status,wordfreqZipfPl=zipf(key),sourceUnits=proofs,nativeEvidence=evidence,
            metadataProposal=proposal if module=='digital-terms' else None,
            runtimeEstimate=estimate if module=='digital-terms' else None,
            languageAndMeaningInferred=False,inflectionsInvented=False))
    return result


def build(base_raw,audit,directory,out,oracle,zipf,provenance,expected_base=BASE_SHA,expected_dictionary=DICT_SHA,
          expected_audit=None,expected_daily=1333):
    members,manifest,doc,words,_,_=read_base(base_raw,expected_base,expected_dictionary,11,3)
    base={w.lower() for w,_ in words};pool=CompactPool(doc);anchors={}
    for e in doc['entries']:
        frequency=zipf(e['surfaceKey'])
        if frequency<2.5:continue
        for r in decode_entry(pool,e).get('metadata',{}).get('sourceEvidence',{}).get('lexicalReadings',[]):
            if e['surfaceKey'] in r['surfaces'] and ordinary(dict(tag=r['partOfSpeech'],nameClasses=r.get('nameClasses',[]),labels=r.get('labels',[]))):
                anchors[r['lemma']]=max(anchors.get(r['lemma'],0),frequency)
    daily=[];digest=sha256(audit.read_bytes())
    if digest!=expected_audit:raise ValueError('ordinary audit checksum')
    seen=set()
    with audit.open('rb') as stream:
        for line in stream:
            row=read_json(line);key=row['surfaceKey']
            if key in seen:raise ValueError('duplicate ordinary audit key')
            seen.add(key)
            if key in base:continue
            evidence={k:row[k] for k in ['interpretations','generatedFormProofs']};matches=lexical_matches(key,evidence)
            frequency=zipf(key);family=max((anchors.get(r['lemma'],0) for r in matches),default=0)
            if not matches or not selected(frequency,family):continue
            if frequency!=row['zipf'] or oracle.evidence(key)!=evidence:raise ValueError('ordinary source snapshot mismatch')
            encoded=pool.encode(compact_entry(key,evidence))
            daily.append(dict(surfaceKey=key,sourceSpellings=sorted({p['form'] for p in evidence['generatedFormProofs']}),keyShape='single-key',inBase=False,
                status='native-revalidated-common-candidate',wordfreqZipfPl=frequency,familyZipf=family,
                previousReason=row['reason'],sourceAuditSha256=digest,nativeEvidence=evidence,
                metadataProposal=encoded,runtimeEstimate=dict(nodes=nodes(encoded),bytes=len(canonical_bytes(encoded))),
                languageAndMeaningInferred=False,inflectionsInvented=False))
    daily.sort(key=lambda r:(-r['wordfreqZipfPl'],r['surfaceKey']))
    if len(daily)!=expected_daily:raise ValueError('daily candidate count changed')
    lock,files,lock_sha=read_snapshot(directory);terms,names=source_candidates(files)
    modules={'common-families':daily,'digital-terms':candidates_from_sources(terms,'digital-terms',base,pool,oracle,zipf),
             'apps-and-services':candidates_from_sources(names,'apps-and-services',base,pool,oracle,zipf)}
    # Union accounting, never sum overlapping module rows as additional dictionary words.
    new_sets={name:{r['surfaceKey'] for r in rows if not r['inBase'] and r['keyShape']=='single-key'} for name,rows in modules.items()}
    union=set().union(*new_sets.values());known={};conflicts=set()
    for name,rows in modules.items():
        for r in rows:
            key=r['surfaceKey']
            if key not in union or r['metadataProposal'] is None:continue
            value=canonical_bytes(r['metadataProposal'])
            if key in known and known[key]!=value:conflicts.add(key)
            known[key]=value
    report=dict(candidateOnly=True,importable=False,baseVersion=11,baseWordCount=len(words),baseSha256=sha256(base_raw),
        baseMetadataEntries=len(doc['entries']),baseMetadataNodes=nodes(doc),baseMetadataBytes=len(members['language-intelligence.json']),
        remainingEntries=120000-len(doc['entries']),remainingNodes=2000000-nodes(doc),remainingBytes=32*1024*1024-len(members['language-intelligence.json']),
        modules={name:capacity(rows) for name,rows in modules.items()},newSingleKeyUnion=len(union),
        overlapByModulePairs={a+' + '+b:len(new_sets[a]&new_sets[b]) for a in sorted(modules) for b in sorted(modules) if a<b},
        metadataProposalConflicts=sorted(conflicts),ordinaryAuditSha256=digest,sourceLockSha256=lock_sha,lexicalProvenance=provenance,
        notes=['No dictionary.bin, manifest.json, APK, importable pack or changes to installed v11.',
            'Index/category membership is a source selection signal, not proof of sense, current product activity or useful rank.',
            'Modern name spellings, activity, Polish use, inflections and case collisions need separate review; no guessed meanings.',
            'Metadata estimates cover known proposed entries only; unknown costs are null, not zero.',
            'Old rare-names v12 is held; private dictionary is not an input; no old base word removed.'])
    output={'candidate-bundle.json':canonical_bytes(report)}
    for name,rows in modules.items():
        output['modules/'+name+'/candidates.jsonl']=b''.join(canonical_bytes(r) for r in rows)
        output['modules/'+name+'/new-single-keys.txt']=''.join(r['surfaceKey']+'\n' for r in rows if not r['inBase'] and r['keyShape']=='single-key').encode()
    # Human review lists retain source spellings and explicit review status.
    polish_status={'native-revalidated-common-candidate':'potwierdzony SGJP; kandydat do przeglądu',
        'source-attested-ordinary-review':'potwierdzony SGJP; ocenić użyteczność',
        'needs-lexical-and-morphology-review':'sprawdzić polskie użycie, pisownię i odmianę',
        'needs-name-spelling-and-usage-review':'sprawdzić nazwę, aktualność i polskie użycie',
        'needs-non-single-key-support':'fraza/interpunkcja; osobna ścieżka obsługi',
        'already-in-v11':'już w v11'}
    for name,rows in modules.items():
        lines=['NOWE KANDYDATURY — '+name,'Materiał do przeglądu, nie zatwierdzone dodatki.','']
        for r in rows:
            if r['inBase']:continue
            lines.append(' / '.join(r['sourceSpellings'])+' | '+polish_status[r['status']]+' | Zipf PL: '+str(r['wordfreqZipfPl']))
        output['modules/'+name+'/DO-PRZEJRZENIA.txt']=('\n'.join(lines)+'\n').encode()
    summary=['PACZKA MODUŁÓW Z KANDYDATAMI — BAZA v11','',
        'Bez zmiany zainstalowanego słownika i bez paczki do importu.',
        'Pominięta dodatkowa partia nazw v12; wszystkie słowa v11 pozostają.',
        '', 'Moduł | Nowe pojedyncze klucze | Już obecne w v11 | Nowe frazy/interpunkcja',
        *[name+' | '+str(report['modules'][name]['newSingleKeys'])+' | '+str(report['modules'][name]['baseOverlap'])+' | '+str(report['modules'][name]['newOtherShapes']) for name in modules],
        '', 'Unia nowych pojedynczych kluczy: '+str(report['newSingleKeyUnion'])+' (moduły nakładają się).',
        str(len(daily))+' zwykłych form ponownie potwierdzono SGJP; pozostałe potwierdzenia to dowód poprawności, nie popularności.',
        'Kategorie aplikacji obejmują także starsze produkty i ogólne pojęcia. Nie są kompletną bazą współczesnych marek.',
        'Nowe nazwy wymagają weryfikacji pisowni, aktualności, użyteczności i ewentualnej odmiany.',
        'Frazy/łączniki zostają całe; nie rozbijamy ich na fikcyjne samodzielne słowa.',
        'Pojedynczy nowy klucz może mieć kilka źródeł, odczytań lub wariantów pisowni.',
        'Pozostała pojemność v11: '+str(report['remainingEntries'])+' wpisów / '+str(report['remainingNodes'])+' elementów / '+str(report['remainingBytes'])+' bajtów metadanych.',
        'Koszty metadanych są znane tylko dla propozycji opartych na SGJP; reszta wymaga osobnego pomiaru.',
        'Następny etap: przegląd źródeł i kandydatur, wspólna selekcja, pełne testy danych oraz dopiero później langpack.',
        'Prywatny słownik nie jest źródłem i jego duplikaty sprawdzimy na końcu.']
    output['RAPORT.txt']=('\n'.join(summary)+'\n').encode()
    output['sources/intake-lock.json']=(directory/'intake-lock.json').read_bytes()
    for meta,_ in files:output['sources/'+meta['path']]=(directory/meta['path']).read_bytes()
    readme=('KANDYDATURY DO ROZBUDOWY POLSKIEGO SŁOWNIKA\n\n'
        'To materiał do przeglądu, NIE paczka do importu w klawiaturze. Bazą pozostaje v11.\n'
        'common-families: zwykłe formy, ponownie zweryfikowane natywnym SGJP.\n'
        'digital-terms: całe hasła indeksów Informatyka, Technika i Slang.\n'
        'apps-and-services: nazwy z zamrożonych polskich kategorii Wikipedii i etykiet Wikidanych.\n'
        'Każdy JSONL zachowuje dowody źródłowe, pisownię, częstość, obecność w v11 i status.\n'
        'Listy new-single-keys.txt obejmują kandydatury, nie zatwierdzone dodatki.\n'
        'Istniejące wpisy pozostają w JSONL do kontroli nakładania, ale nie są nowymi słowami.\n'
        'Frazy i interpunkcja nie są rozbijane; brak dowodu/częstości nie dowodzi nieistnienia.\n'
        'Nie wymyślamy opisów znaczeń ani odmian. Dalsze zatwierdzanie i testy są osobnym etapem.\n'
        'Koszty metadanych nie obejmują przyszłej proweniencji. Brak kosztu oznacza niezmierzone, nie zero.\n\n'
        'Pochodzenie i atrybucja: Morfeusz2/SGJP i wordfreq według istniejącego NOTICE v11;\n'
        'indeksy Wikisłownika i dane Wikipedii: autorzy Wikimedia, CC BY-SA 4.0, URL w intake-lock;\n'
        'etykiety/claims Wikidanych: CC0, QID i wersja w rekordach. Kategorie i etykiety nie są definicjami SI.\n')
    output['CZYTAJ-MNIE.txt']=readme.encode();output['sources/BASE-NOTICE.txt']=members['NOTICE.txt']
    package=write_pack(output);out.mkdir(parents=True,exist_ok=True)
    if (out/BUNDLE_NAME).exists():raise ValueError('candidate bundle already exists')
    with zipfile.ZipFile(__import__('io').BytesIO(package)) as z:
        if any(Path(n).name in {'manifest.json','dictionary.bin','language-intelligence.json'} for n in z.namelist()):raise ValueError('accidental importable output')
    for name,data in output.items():
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    (out/BUNDLE_NAME).write_bytes(package);(out/'candidate-bundle.sha256').write_text(sha256(package)+'  '+BUNDLE_NAME+'\n')
    return report


def main():
    p=argparse.ArgumentParser();
    for name in ['base-pack','ordinary-audit','sources','out']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();import morfeusz2,wordfreq
    from importlib.metadata import distribution,version
    native=morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
    direct=json.loads(distribution('wordfreq').read_text('direct_url.json') or '{}')
    if (str(morfeusz2.__version__)!=MORFEUSZ_VERSION or native.dict_id()!=DICTIONARY_ID or version('wordfreq')!='3.2.0'
            or direct.get('vcs_info',{}).get('commit_id')!=WORDFREQ_COMMIT):raise ValueError('native lexical source snapshot')
    root=Path(__file__).resolve().parents[1];audit_sha=read_json((root/'docs/common-forms-trial-v1/reviewed-report.json').read_bytes())['auditSha256']
    provenance=dict(morfeuszVersion=MORFEUSZ_VERSION,sgjpDictionaryId=DICTIONARY_ID,wordfreqVersion='3.2.0',wordfreqCommit=WORDFREQ_COMMIT)
    report=build(a.base_pack.read_bytes(),a.ordinary_audit,a.sources,a.out,SourceOracle(native),lambda w:wordfreq.zipf_frequency(w,'pl'),provenance,expected_audit=audit_sha)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
