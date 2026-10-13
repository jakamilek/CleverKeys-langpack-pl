#!/usr/bin/env python3
"""Compile actual compact source readers and verify v10/v11 content and heap gates."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('consumer', 'base-pack', 'pack', 'build-dir'):
        parser.add_argument('--'+key, type=Path, required=True)
    args = parser.parse_args(); root = Path(__file__).resolve().parents[1]
    args.build_dir.mkdir(parents=True, exist_ok=True)
    jars = []
    for item in json.loads((root/'tests/fixtures/common-forms-jvm-tools.json').read_text()):
        file = args.build_dir/Path(item['path']).name
        if not file.exists():
            with urllib.request.urlopen('https://repo.maven.apache.org/maven2/'+item['path'], timeout=60) as r:
                file.write_bytes(r.read())
        if hashlib.sha256(file.read_bytes()).hexdigest() != item['sha256']: raise ValueError('dependency checksum')
        jars.append(str(file.resolve()))
    cp = ':'.join(jars)
    src = args.consumer/'src/main/kotlin/tribixbite/cleverkeys'
    tests = args.consumer/'src/test/kotlin/tribixbite/cleverkeys/langpack'
    files = [src/'langpack/LanguageIntelligence.kt', src/'langpack/SharedSourceMetadata.kt', src/'SwipeSurfaceVariants.kt']
    files += [src/'swipe/geometric'/name for name in ['CkdtDictionaryReader.kt','GeometricDictionary.kt','ArrayBackedDictionary.kt']]
    files += [tests/'LanguageIntelligenceTest.kt', tests/'SharedLanguageIntelligenceTest.kt', tests/'CompactSourceMetadataTest.kt', root/'tests/CompactSourceConsumerCheck.kt']
    jar = args.build_dir/'compact-consumer.jar'
    subprocess.run(['java','-Xmx1g','-cp',cp,'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib',
        '-no-reflect','-jvm-target','17','-classpath',cp,'-d',str(jar),*map(str,files)],check=True)
    cp = str(jar.resolve())+':'+cp+':'+str((args.consumer/'src/test/resources').resolve())
    subprocess.run(['java','-Xmx1g','-cp',cp,'org.junit.runner.JUnitCore',
        'tribixbite.cleverkeys.langpack.LanguageIntelligenceTest',
        'tribixbite.cleverkeys.langpack.SharedLanguageIntelligenceTest',
        'tribixbite.cleverkeys.langpack.CompactSourceMetadataTest'],check=True)
    for mode, heap in [('full','1g'),('cold','192m'),('replace','192m'),('repeat','192m')]:
        subprocess.run(['java','-Xmx'+heap,'-cp',cp,'tribixbite.cleverkeys.langpack.CompactSourceConsumerCheck',
            mode,str(args.base_pack),str(args.pack)],check=True)


if __name__ == '__main__': main()
