"""Verify the actual unsigned device IPA and record its source/toolchain."""
import hashlib
import json
import os
from pathlib import Path
import plistlib
import struct
import subprocess
import zipfile


def command(*args):
    return subprocess.check_output(args, text=True).strip()


ipa = Path('build/AirCard-iOS.ipa')
library = Path('rust-core/target/aarch64-apple-ios/release/libairlift_ffi.a')
assert ipa.is_file() and library.is_file()
framework_root = Path('AirliftFFI.xcframework')
framework = plistlib.loads((framework_root / 'Info.plist').read_bytes())
device_library, = framework['AvailableLibraries']
assert device_library['SupportedPlatform'] == 'ios'
assert device_library['SupportedArchitectures'] == ['arm64']
linked_library = framework_root / device_library['LibraryIdentifier'] / device_library['LibraryPath']
assert hashlib.sha256(linked_library.read_bytes()).digest() == hashlib.sha256(library.read_bytes()).digest()
with zipfile.ZipFile(ipa) as z:
    assert z.testzip() is None, 'Broken IPA archive'
    plist_paths = [n for n in z.namelist()
                   if n.startswith('Payload/') and n.count('/') == 2 and n.endswith('.app/Info.plist')]
    assert len(plist_paths) == 1, plist_paths
    plist_path = plist_paths[0]
    app = plist_path.rsplit('/', 1)[0]
    info = plistlib.loads(z.read(plist_path))
    assert info['CFBundleIdentifier'] == 'com.mak5er.aircard'
    assert info['CFBundleDisplayName'] == 'AirCard Fix'
    assert info['CFBundleVersion'] == '13201'
    assert info['AirCardPosterKitHiddenOptionsFix'] is True
    assert info['UIDeviceFamily'] == [1], 'Unexpected device-family change'
    binary = z.read(f"{app}/{info['CFBundleExecutable']}")
    magic, cpu = struct.unpack_from('<II', binary)
    assert magic == 0xFEEDFACF and cpu == 0x0100000C, 'Expected arm64 Mach-O device executable'
    assert f'{app}/embedded.mobileprovision' not in z.namelist()
    assert not any(n.startswith(f'{app}/_CodeSignature/') for n in z.namelist())

report = {
    'source_commit': command('git', 'rev-parse', 'HEAD'),
    'upstream_commit': '40640c4d827aeab8d798285b57d24fcf6be070d0',
    'run_url': os.environ.get('AIRCARD_RUN_URL'),
    'xcode': command('xcodebuild', '-version'),
    'iphoneos_sdk': command('xcrun', '--sdk', 'iphoneos', '--show-sdk-version'),
    'rust': command('rustc', '-Vv'),
    'bundle_identifier': info['CFBundleIdentifier'],
    'bundle_version': info['CFBundleVersion'],
    'minimum_ios': info['MinimumOSVersion'],
    'architecture': 'arm64',
    'unsigned': True,
    'fresh_rust_library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(),
    'ipa_sha256': hashlib.sha256(ipa.read_bytes()).hexdigest(),
    'ipa_bytes': ipa.stat().st_size,
    'device_verified': False,
}
Path('build/build-info.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
