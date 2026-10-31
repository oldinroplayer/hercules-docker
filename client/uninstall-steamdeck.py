#!/usr/bin/env python3
"""Remove the Family RO client from a Steam Deck (or any Linux with Steam).

Undoes install-steamdeck.py: takes the "Family RO" shortcut out of every Steam
user's shortcuts.vdf, drops its Proton setting from config.vdf, deletes the
Wine prefix Steam made for it and, unless told to keep them, the client folder
(about 8 GB with the download). Steam's own files are backed up beside the
originals as *.bak-familyro-uninstall first.

Run it in Desktop Mode, with Steam closed:
    python3 uninstall-steamdeck.py [--dir ~/Games/FamilyRO] [--keep-files] [--yes]
"""
import argparse
import glob
import importlib.util
import os
import re
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = 'Family RO'

spec = importlib.util.spec_from_file_location('installer', os.path.join(HERE, 'install-steamdeck.py'))
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def entry_appid(entry):
    i = entry.index(b'\x02appid\0') + len(b'\x02appid\0')
    return struct.unpack('<I', entry[i:i + 4])[0]


def remove_shortcut(vdf_path):
    """Drop the NAME entries; return their appids (empty if there were none)."""
    entries = installer.read_shortcuts(vdf_path)
    mine = [e for e in entries if b'\x01AppName\0' + NAME.encode() + b'\0' in e]
    if not mine:
        return []
    shutil.copy(vdf_path, vdf_path + '.bak-familyro-uninstall')
    kept = [e for e in entries if e not in mine]
    fixed = []
    for i, e in enumerate(kept):
        rest = e[e.index(b'\0', 1) + 1:]
        fixed.append(b'\x00' + str(i).encode() + b'\0' + rest)
    open(vdf_path, 'wb').write(b'\x00shortcuts\x00' + b''.join(fixed) + b'\x08\x08')
    return [entry_appid(e) for e in mine]


def remove_compat_tool(config_vdf, appids):
    if not os.path.exists(config_vdf):
        return
    text = open(config_vdf).read()
    new = text
    for appid in appids:
        for key in {appid, appid - (1 << 32)}:  # Steam writes it unsigned or signed
            new = re.sub(r'\n?[ \t]*"%d"\s*\{[^{}]*\}[ \t]*' % key, '', new, count=1)
    if new != text:
        shutil.copy(config_vdf, config_vdf + '.bak-familyro-uninstall')
        open(config_vdf, 'w').write(new)


def ask(question):
    """Read the answer from the terminal even when the script itself came down a pipe."""
    try:
        with open('/dev/tty') as tty:
            print(question, end='', flush=True)
            return tty.readline().strip().lower() == 'y'
    except OSError:
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dir', default='~/Games/FamilyRO')
    ap.add_argument('--keep-files', action='store_true', help='leave the client folder (and its download) in place')
    ap.add_argument('--yes', action='store_true', help='do not ask before deleting the client folder')
    ap.add_argument('--steam-root', help='Steam folder, for testing')
    ap.add_argument('--no-steam-check', action='store_true', help='skip the "Steam is running" check, for testing')
    a = ap.parse_args()
    d = os.path.realpath(os.path.expanduser(a.dir))

    if not a.no_steam_check and subprocess.run(['pgrep', '-x', 'steam'], capture_output=True).returncode == 0:
        sys.exit('Steam is running. Quit it completely (Steam menu > Exit), then run this again.')

    root = os.path.realpath(os.path.expanduser(a.steam_root)) if a.steam_root else installer.steam_root()
    appids = []
    for u in glob.glob(os.path.join(root, 'userdata', '*')):
        vdf = os.path.join(u, 'config', 'shortcuts.vdf')
        if os.path.isdir(u) and os.path.basename(u).isdigit() and os.path.exists(vdf):
            appids += remove_shortcut(vdf)
    appids = sorted(set(appids))
    if appids:
        print('Removed the "%s" shortcut from Steam.' % NAME)
    else:
        print('No "%s" shortcut found in Steam.' % NAME)
    remove_compat_tool(os.path.join(root, 'config', 'config.vdf'), appids)
    for appid in appids:
        prefix = os.path.join(root, 'steamapps', 'compatdata', str(appid))
        if os.path.isdir(prefix):
            shutil.rmtree(prefix)
            print('Deleted the Wine prefix', prefix)

    if a.keep_files:
        print('Kept', d)
        return
    looks_right = any(os.path.exists(os.path.join(d, f)) for f in ('Ragexe_patched.exe', 'Ragexe.exe'))
    if not os.path.isdir(d):
        print('No client folder at', d)
    elif d in ('/', os.path.expanduser('~')) or not looks_right:
        print('%s does not look like the Family RO folder, leaving it' % d)
    else:
        if not a.yes and not ask('Delete %s and everything in it? [y/N] ' % d):
            print('Kept', d)
        else:
            shutil.rmtree(d)
            print('Deleted', d)
    print('Done. Saves and settings live on the server, nothing else is left on this machine.')


if __name__ == '__main__':
    main()
