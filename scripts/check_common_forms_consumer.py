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
    parser.add_argument('--thematic-memory-check', action='store_true',
                        help='Also check real v7 and v5/v7 at 192MiB, and v6/v7 at 256MiB, with ballast')
    parser.add_argument('--legacy-base-pack', type=Path,
                        help='Verified v5 ZIP required for the original 192MiB import gate')
    args = parser.parse_args()
    if args.thematic_memory_check and args.legacy_base_pack is None:
        parser.error('--thematic-memory-check requires --legacy-base-pack')
    if args.thematic_memory_check:
        from build_common_forms_trial import BASE_PACK_SHA256
        if hashlib.sha256(args.legacy_base_pack.read_bytes()).hexdigest() != BASE_PACK_SHA256:
            raise ValueError('legacy v5 checksum mismatch for memory gate')
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
    if args.thematic_memory_check:
        files.append(root / 'tests/ThematicFormsMemoryCheck.kt')
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
    if args.thematic_memory_check:
        for heap, packs in [(192, [args.pack]), (192, [args.legacy_base_pack, args.pack]),
                            (256, [args.base_pack, args.pack])]:
            subprocess.run(['java', f'-Xmx{heap}m', '-cp', runtime_cp,
                            'tribixbite.cleverkeys.langpack.ThematicFormsMemoryCheck',
                            *map(str, packs)], check=True)


if __name__ == '__main__': main()
