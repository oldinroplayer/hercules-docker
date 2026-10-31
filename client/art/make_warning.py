# Repaints the Korean age notice on the client's warning screen in English.
# Usage: make_warning.py <original warning.bmp as PNG or BMP> <out.png> <bold font .ttf>
# The original comes out of the client GRF (data/texture/<UI folder>/login_interface/warning.bmp).
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src, out = sys.argv[1], sys.argv[2]
FONT = sys.argv[3]
im = Image.open(src).convert('RGB')
W, H = im.size
px = im.load()
# panel interior: repaint with the vertical gradient sampled down a clean margin column
X0, X1, Y0, Y1 = 228, 1692, 442, 1132
col = [tuple(sum(px[x, y][c] for x in range(212, 226)) // 14 for c in range(3)) for y in range(H)]
d = ImageDraw.Draw(im)
for y in range(Y0, Y1):
    d.line([(X0, y), (X1, y)], fill=col[y])
NAVY, EDGE, BLUE = (28, 42, 110), (232, 247, 255), (30, 96, 200)
def text(xy, s, size, fill=NAVY, stroke=3, anchor='la'):
    f = ImageFont.truetype(FONT, size)
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=EDGE, anchor=anchor)
    return d.textlength(s, font=f)
x = 250
text((x, 480), 'This game is rated', 66)
w = text((x, 566), 'Ages 12 and up', 112, BLUE, 4)
body = ['It is not suitable for children or teens below that age.',
        'Because of its cartoon violence, a parent or guardian',
        'should guide and supervise younger players.']
y = 730
for line in body:
    text((x, y), line, 46); y += 66
text((x, y + 34), 'Playing for long periods may harm your health.', 46)
# rating icon captions: black strips under the two icons
for (cx0, cx1), label in (((1420, 1592), 'VIOLENCE'), ((1676, 1868), 'AGES 12+')):
    d.rectangle([cx0 - 10, 262, cx1 + 10, 298], fill=(10, 10, 10))
    f = ImageFont.truetype(FONT, 28)
    d.text(((cx0 + cx1) // 2, 280), label, font=f, fill=(255, 255, 255), anchor='mm')
im.save(out)
print(out, im.size)
