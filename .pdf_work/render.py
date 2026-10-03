import struct
import sys

import pypdfium2 as pdfium

source = r"C:\Users\neera\Downloads\ugc-net-2025-law-question-paper-and-answer-key-pdf-dec-31-2025-shift-1-1775454491.pdf"
document = pdfium.PdfDocument(source)
for page_number in map(int, sys.argv[1:]):
    bitmap = document[page_number - 1].render(scale=2.5)
    width, height, stride = bitmap.width, bitmap.height, bitmap.stride
    padding = b"\x00" * ((4 - (width * 3) % 4) % 4)
    raw = bitmap.buffer
    pixels = b"".join(
        bytes(raw[y * stride : y * stride + width * 3]) + padding
        for y in range(height - 1, -1, -1)
    )
    header = b"BM" + struct.pack(
        "<IHHI", 54 + len(pixels), 0, 0, 54
    ) + struct.pack(
        "<IIIHHIIIIII", 40, width, height, 1, 24, 0, len(pixels), 2835, 2835, 0, 0
    )
    with open(f".pdf_work/page{page_number}.bmp", "wb") as output:
        output.write(header + pixels)
