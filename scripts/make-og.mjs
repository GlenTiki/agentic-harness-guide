import fs from 'node:fs';
import zlib from 'node:zlib';

const WIDTH = 1200;
const HEIGHT = 630;
const out = process.argv[2] ?? 'public/og.png';

const GLYPHS = {
  A: ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
  B: ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
  C: ['01110', '10001', '10000', '10000', '10000', '10001', '01110'],
  D: ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
  E: ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
  F: ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
  G: ['01110', '10001', '10000', '10111', '10001', '10001', '01111'],
  H: ['10001', '10001', '10001', '11111', '10001', '10001', '10001'],
  I: ['01110', '00100', '00100', '00100', '00100', '00100', '01110'],
  J: ['00111', '00010', '00010', '00010', '00010', '10010', '01100'],
  K: ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
  L: ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
  M: ['10001', '11011', '10101', '10101', '10001', '10001', '10001'],
  N: ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
  O: ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
  P: ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
  Q: ['01110', '10001', '10001', '10001', '10101', '10010', '01101'],
  R: ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
  S: ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
  T: ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
  U: ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
  V: ['10001', '10001', '10001', '10001', '10001', '01010', '00100'],
  W: ['10001', '10001', '10001', '10101', '10101', '11011', '10001'],
  X: ['10001', '10001', '01010', '00100', '01010', '10001', '10001'],
  Y: ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
  Z: ['11111', '00001', '00010', '00100', '01000', '10000', '11111'],
  0: ['01110', '10001', '10011', '10101', '11001', '10001', '01110'],
  1: ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
  2: ['01110', '10001', '00001', '00010', '00100', '01000', '11111'],
  3: ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
  4: ['00010', '00110', '01010', '10010', '11111', '00010', '00010'],
  5: ['11111', '10000', '11110', '00001', '00001', '10001', '01110'],
  6: ['00110', '01000', '10000', '11110', '10001', '10001', '01110'],
  7: ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
  8: ['01110', '10001', '10001', '01110', '10001', '10001', '01110'],
  9: ['01110', '10001', '10001', '01111', '00001', '00010', '01100'],
  ' ': ['00000', '00000', '00000', '00000', '00000', '00000', '00000'],
  ',': ['00000', '00000', '00000', '00000', '00110', '00100', '01000'],
  '.': ['00000', '00000', '00000', '00000', '00000', '01100', '01100'],
  ':': ['00000', '01100', '01100', '00000', '01100', '01100', '00000'],
  '-': ['00000', '00000', '00000', '11111', '00000', '00000', '00000'],
  '+': ['00000', '00100', '00100', '11111', '00100', '00100', '00000'],
};

const hex = (value) => [1, 3, 5].map((i) => parseInt(value.slice(i, i + 2), 16));
const INK = hex('#1b1d1f');
const BACKGROUND = hex('#fafaf7');
const ACCENT = hex('#1a5fd0');
const WRONG = hex('#a8261c');
const WRONG_SOFT = hex('#fbe9e7');
const RIGHT = hex('#1e6b2e');
const RIGHT_SOFT = hex('#e4f3e7');
const MUTED = hex('#565b61');

const pixels = Buffer.alloc(WIDTH * HEIGHT * 3);
const fillRect = (x, y, w, h, color) => {
  for (let row = Math.max(0, y); row < Math.min(HEIGHT, y + h); row += 1) {
    for (let col = Math.max(0, x); col < Math.min(WIDTH, x + w); col += 1) {
      pixels.set(color, (row * WIDTH + col) * 3);
    }
  }
};
fillRect(0, 0, WIDTH, HEIGHT, BACKGROUND);

const textWidth = (text, scale) => text.length * 6 * scale - scale;
const drawText = (text, x, y, scale, color) => {
  let cursor = x;
  for (const char of text.toUpperCase()) {
    const glyph = GLYPHS[char];
    if (!glyph) throw new Error(`no glyph for ${JSON.stringify(char)}`);
    glyph.forEach((row, r) => {
      [...row].forEach((bit, c) => {
        if (bit === '1') fillRect(cursor + c * scale, y + r * scale, scale, scale, color);
      });
    });
    cursor += 6 * scale;
  }
};

fillRect(0, 0, WIDTH, 12, ACCENT);
drawText('THE AGENTIC HARNESS GUIDE', 60, 56, 5, ACCENT);
drawText('GET DEPENDABLE', 60, 126, 10, INK);
drawText('WORK FROM AN', 60, 214, 10, INK);
drawText('AI ASSISTANT', 60, 302, 10, INK);

const card = (x, color, soft, label, figure, detail) => {
  fillRect(x, 395, 520, 160, color);
  fillRect(x + 8, 399, 508, 152, soft);
  drawText(label, x + 28, 415, 3, color);
  drawText(figure, x + 28, 445, 8, INK);
  drawText(detail, x + 28, 521, 3, MUTED);
};
card(60, WRONG, WRONG_SOFT, 'OBSERVED: WRONG HEADLINE', '7,414', 'ALL 20 FLAGGED DOUBT');
card(620, RIGHT, RIGHT_SOFT, 'COMPUTED: CHECKED', '7,281', 'THREE LINES, SAME BILLS');
const note = 'SAME 40 BILLS, TWO TOTALS';
drawText(note, WIDTH - 60 - textWidth(note, 3), 580, 3, MUTED);

const crcTable = Array.from({ length: 256 }, (_, n) => {
  let c = n;
  for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});
const crc32 = (buffer) => {
  let c = 0xffffffff;
  for (const byte of buffer) c = crcTable[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
};
const chunk = (type, data) => {
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length);
  const body = Buffer.concat([Buffer.from(type), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body));
  return Buffer.concat([length, body, crc]);
};
const header = Buffer.alloc(13);
header.writeUInt32BE(WIDTH, 0);
header.writeUInt32BE(HEIGHT, 4);
header.set([8, 2, 0, 0, 0], 8);
const rows = Buffer.alloc((WIDTH * 3 + 1) * HEIGHT);
for (let y = 0; y < HEIGHT; y += 1) {
  pixels.copy(rows, y * (WIDTH * 3 + 1) + 1, y * WIDTH * 3, (y + 1) * WIDTH * 3);
}
const png = Buffer.concat([
  Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
  chunk('IHDR', header),
  chunk('IDAT', zlib.deflateSync(rows, { level: 9 })),
  chunk('IEND', Buffer.alloc(0)),
]);
fs.writeFileSync(out, png);
console.log(`${out}: ${WIDTH}x${HEIGHT}, ${png.length} bytes`);
