#!/usr/bin/env python3
"""Run pinned v11 consumer against eight source-linked proposals; Java 17 required."""
import json,hashlib,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'build/selection-review'; D=OUT/'consumer';D.mkdir(parents=True,exist_ok=True)
lock=ROOT/'source/selection-review/consumer-lock.json'
for item in json.loads(lock.read_text()):
 p=D/item['path']
 if not p.exists():p.write_bytes(urllib.request.urlopen(item['url'],timeout=60).read())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],p
jars=list(D.glob('*.jar'));cp=':'.join(str(p) for p in jars if p.name!='check.jar')
run=['java','-cp',cp,'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',cp,'-d',str(D/'check.jar'),str(D/'LanguageIntelligence.kt'),str(D/'SharedSourceMetadata.kt'),str(ROOT/'tests/ExternalLemmaConsumerCheck.kt')]
subprocess.run(run,check=True)
result=subprocess.run(['java','-Xmx384m','-cp',str(D/'check.jar')+':'+cp,'tribixbite.cleverkeys.langpack.ExternalLemmaConsumerCheck',sys.argv[1],str(OUT/'consumer-simulation.json'),str(OUT/'external-bridge-full.json'),str(OUT/'base-metadata-keys.txt')],check=True,capture_output=True,text=True)
(OUT/'consumer-check.txt').write_text(result.stdout);print(result.stdout,end='')
