#!/usr/bin/env python3
"""Check real v7/v8 readers, source-case presentation and isolated 192MiB heaps."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--consumer', type=Path, required=True)
    parser.add_argument('--base-pack', type=Path, required=True)
    parser.add_argument('--pack', type=Path, required=True)
    parser.add_argument('--build-dir', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # This driver verifies every pinned dependency checksum before compiling the
    # actual CKDT/metadata consumer, its focused JUnit suite and full old/new diff.
    subprocess.run([sys.executable, str(root / 'scripts/check_common_forms_consumer.py'),
        '--consumer', str(args.consumer), '--base-pack', str(args.base_pack),
        '--pack', str(args.pack), '--build-dir', str(args.build_dir)], check=True)
    jars = [str((args.build_dir / Path(item['path']).name).resolve()) for item in
        json.loads((root / 'tests/fixtures/common-forms-jvm-tools.json').read_text())]
    cp = ':'.join(jars)
    src = args.consumer / 'src/main/kotlin/tribixbite/cleverkeys'
    compiled = args.build_dir / 'names-memory-check.jar'
    subprocess.run(['java', '-Xmx1g', '-cp', cp, 'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
        '-no-stdlib', '-no-reflect', '-jvm-target', '17', '-classpath', cp,
        '-d', str(compiled), str(src / 'langpack/LanguageIntelligence.kt'),
        str(src / 'SwipeSurfaceVariants.kt'), str(root / 'tests/NamesFormsMemoryCheck.kt')], check=True)
    for packs in ([args.pack], [args.base_pack, args.pack]):
        subprocess.run(['java', '-Xmx192m', '-cp', str(compiled.resolve()) + ':' + cp,
            'tribixbite.cleverkeys.langpack.NamesFormsMemoryCheck', *map(str, packs)], check=True)


if __name__ == '__main__': main()
