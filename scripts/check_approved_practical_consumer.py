#!/usr/bin/env python3
import sys,json,hashlib,urllib.request,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=Path(sys.argv[4]);D.mkdir(parents=True,exist_ok=True)
items=json.loads((R/'source/approved-practical-v13/consumer-lock.json').read_text())
for x in items:
 p=D/x['path']
 if not p.exists():p.write_bytes(urllib.request.urlopen(x['url'],timeout=60).read())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'],p
cp=':'.join(str(D/x['path']) for x in items if x['path'].endswith('.jar'))
sources=[str(D/x['path']) for x in items if x['path'].endswith('.kt')]+[str(R/'tests/ApprovedPracticalConsumerCheck.kt')]
jar=D/'approved-check.jar'
subprocess.run(['java','-cp',cp,'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-classpath',cp,'-d',str(jar),*sources],check=True)
log=[]
for mode,heap in [('full','1g'),('cold','192m'),('replace','192m'),('repeat','192m')]:
 p=subprocess.run(['java','-Xmx'+heap,'-cp',str(jar)+':'+cp,'tribixbite.cleverkeys.langpack.ApprovedPracticalConsumerCheck',mode,*sys.argv[1:4]],check=False,text=True,capture_output=True);print(p.stderr,end="",file=sys.stderr);p.check_returncode();print(p.stdout,end='',flush=True);log.append(p.stdout)
Path(sys.argv[2]).with_name('consumer-check.txt').write_text(''.join(log))
