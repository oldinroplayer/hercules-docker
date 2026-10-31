#!/usr/bin/env python3
"""Add this repo's own pieces to the English overlay zip: the translated world
map message table and the family-friendly art (loading screens, English age
notice). Everything else in the zip is build_english.py's output, unchanged.

    package_overlay.py BASE.zip OUT.zip WORLDVIEW_LANGUAGE.lub

BASE.zip is the previous overlay release (or build_english.py's output zipped
with data/ and System/ at the top). WORLDVIEW_LANGUAGE.lub is
Translation/Renewal/data/luafiles514/lua files/worldviewdata/ from the
ROenglishRE checkout. The client reads loose files first, so these simply
win over the Korean ones in the GRFs.

The UI texture folder keeps its Korean name read as Latin-1, the same way
build_english.py writes it, which is what the client asks the OS for under a
non-Korean locale.
"""
import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
UI = 'data/texture/' + '유저인터페이스'.encode('cp949').decode('latin-1')


def main(base, out, worldview):
    new = {'data/luafiles514/lua files/worldviewdata/worldviewdata_language.lub':
           Path(worldview).read_bytes()}
    for i in range(7):
        new['%s/loading%02d.jpg' % (UI, i)] = (HERE / 'art' / ('loading%02d.jpg' % i)).read_bytes()
    notice = Image.open(HERE / 'art' / 'warning.png').convert('RGB')
    for name, size in (('warning.bmp', notice.size), ('warning2.bmp', notice.size), ('warning3.bmp', (640, 480))):
        buf = io.BytesIO()
        notice.resize(size, Image.LANCZOS).save(buf, 'BMP')
        new['%s/login_interface/%s' % (UI, name)] = buf.getvalue()
    with zipfile.ZipFile(base) as zin, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            if info.filename not in new:
                zout.writestr(info, zin.read(info.filename), compress_type=zipfile.ZIP_DEFLATED)
        for name, data in sorted(new.items()):
            zout.writestr(name, data)
    print('wrote', out, 'with', len(new), 'added or replaced files')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
