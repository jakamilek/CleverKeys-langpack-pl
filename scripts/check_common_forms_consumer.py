#!/usr/bin/env python3
"""Run focused JUnit and a full-pack check against the actual Kotlin consumer."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--consumer', type=Path, required=True)
    parser.add_argument('--base-pack', type=Path, required=True)
    parser.add_argument('--pack', type=Path, required=True)
    parser.add_argument('--build-dir', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.build_dir.mkdir(parents=True, exist_ok=True)
    jars = []
    for item in json.loads((root / 'tests/fixtures/common-forms-jvm-tools.json').read_text()):
        file = args.build_dir / Path(item['path']).name
        if not file.exists():
            with urllib.request.urlopen('https://repo.maven.apache.org/maven2/' + item['path'], timeout=60) as response:
                file.write_bytes(response.read())
        if hashlib.sha256(file.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('JVM dependency checksum mismatch: ' + file.name)
        jars.append(str(file.resolve()))
    cp = ':'.join(jars)
    src = args.consumer / 'src/main/kotlin/tribixbite/cleverkeys'
    files = [src / 'langpack/LanguageIntelligence.kt', src / 'SwipeSurfaceVariants.kt']
    files += [src / 'swipe/geometric' / name for name in
              ['CkdtDictionaryReader.kt', 'GeometricDictionary.kt', 'ArrayBackedDictionary.kt']]
    files += [args.consumer / 'src/test/kotlin/tribixbite/cleverkeys/langpack/LanguageIntelligenceTest.kt',
              root / 'tests/CommonFormsConsumerCheck.kt']
    compiled = args.build_dir / 'consumer-check.jar'
    subprocess.run(['java', '-Xmx1g', '-cp', cp, 'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
                    '-no-stdlib', '-no-reflect', '-jvm-target', '17', '-classpath', cp,
                    '-d', str(compiled), *map(str, files)], check=True)
    runtime_cp = str(compiled.resolve()) + ':' + cp + ':' + str((args.consumer / 'src/test/resources').resolve())
    subprocess.run(['java', '-Xmx1g', '-cp', runtime_cp, 'org.junit.runner.JUnitCore',
                    'tribixbite.cleverkeys.langpack.LanguageIntelligenceTest'], check=True)
    subprocess.run(['java', '-Xmx1g', '-cp', runtime_cp,
                    'tribixbite.cleverkeys.langpack.CommonFormsConsumerCheckKt',
                    str(args.base_pack), str(args.pack)], check=True)


if __name__ == '__main__': main()
