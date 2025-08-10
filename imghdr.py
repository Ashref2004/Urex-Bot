# imghdr.py - نسخة مستخرجة من Python 3.10
import struct

def what(file, h=None):
    if h is None:
        if hasattr(file, 'read'):
            pos = file.tell()
            h = file.read(32)
            file.seek(pos)
        else:
            with open(file, 'rb') as f:
                h = f.read(32)

    for tf in tests:
        res = tf(h)
        if res:
            return res
    return None

def test_jpeg(h):
    if h[6:10] in (b'JFIF', b'Exif'):
        return 'jpeg'

def test_png(h):
    if h[:8] == b'\211PNG\r\n\032\n':
        return 'png'

def test_gif(h):
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

def test_tiff(h):
    if h[:2] in (b'MM', b'II'):
        return 'tiff'

def test_bmp(h):
    if h[:2] == b'BM':
        return 'bmp'

tests = [test_jpeg, test_png, test_gif, test_tiff, test_bmp]
