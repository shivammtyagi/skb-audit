// Render a self-contained HTML report to PDF with headless Chromium.
// Usage: node print_pdf.js <input.html> <output.pdf>
// Requires the `playwright` package + Chromium (installed via `npx playwright install chromium`).
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [, , inFile, outFile] = process.argv;
  if (!inFile || !outFile) {
    console.error('usage: print_pdf.js <input.html> <output.pdf>');
    process.exit(2);
  }
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.goto('file://' + path.resolve(inFile), { waitUntil: 'networkidle' });
    await page.emulateMedia({ media: 'print' });
    await page.pdf({
      path: outFile,
      format: 'A4',
      printBackground: true,
      margin: { top: '14mm', bottom: '14mm', left: '12mm', right: '12mm' },
    });
  } finally {
    await browser.close();
  }
})().catch((e) => { console.error(e); process.exit(1); });
