/* Screenshots for review.

   Against the deployed site, which is what the captures in screenshots/ are
   taken from — see .github/workflows/screenshots.yml, which runs this on a
   runner that can reach it:
     BASE_URL=https://hafez121.github.io/dar-chams/ node tools/screenshots.cjs

   Against a local copy:
     python3 -m http.server 8123
     NODE_PATH=$(npm root -g) node tools/screenshots.cjs

   CHROME_PATH points at a browser binary when using playwright-core; with the
   full playwright package installed it is not needed. */
const BASE = process.env.BASE_URL || 'http://127.0.0.1:8123/';

// Resolve Playwright from whichever is installed: the full package (CI, which
// manages its own browser) or playwright-core with a browser path supplied.
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch (e) {
  ({ chromium } = require((process.env.NODE_PATH || '') + '/playwright-core'));
}
const LAUNCH = process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {};

// Four pages x two languages x two widths, plus the enquiry form filled in at
// both widths in both languages. Full-page captures.
const SHOTS = [
  ['01-home-1440',              'index.html',           1440],
  ['02-home-390',               'index.html',            390],
  ['03-rooms-1440',             'rooms.html',           1440],
  ['04-rooms-390',              'rooms.html',            390],
  ['05-village-1440',           'village.html',         1440],
  ['06-village-390',            'village.html',          390],
  ['07-contact-1440',           'contact.html',         1440],
  ['08-contact-390',            'contact.html',          390],
  ['09-contact-filled-1440',    'contact.html',         1440, { fill: true }],
  ['10-contact-filled-390',     'contact.html',          390, { fill: true }],
  ['11-home-ar-1440',           'index.html?lang=ar',   1440],
  ['12-home-ar-390',            'index.html?lang=ar',    390],
  ['13-rooms-ar-1440',          'rooms.html?lang=ar',   1440],
  ['14-rooms-ar-390',           'rooms.html?lang=ar',    390],
  ['15-village-ar-1440',        'village.html?lang=ar', 1440],
  ['16-village-ar-390',         'village.html?lang=ar',  390],
  ['17-contact-ar-1440',        'contact.html?lang=ar', 1440],
  ['18-contact-ar-390',         'contact.html?lang=ar',  390],
  ['19-contact-ar-filled-1440', 'contact.html?lang=ar', 1440, { fill: true, ar: true }],
  ['20-contact-ar-filled-390',  'contact.html?lang=ar',  390, { fill: true, ar: true }]
];

(async () => {
  const browser = await chromium.launch(LAUNCH);
  for (const [name, path, width, opt = {}] of SHOTS) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: width < 500 ? 2 : 1 });
    const page = await ctx.newPage();
    await page.goto(BASE + path, { waitUntil: 'networkidle' });
    if (opt.fill) {
      await page.fill('#f-name', opt.ar ? 'ليلى حدّاد' : 'Layla Haddad');
      await page.fill('#f-checkin', '2027-03-14');
      await page.fill('#f-checkout', '2027-03-16');
      await page.fill('#f-guests', '2');
      await page.selectOption('#f-room', 'garden');
      await page.fill('#f-message', opt.ar
        ? 'نصل متأخرين، حوالي التاسعة مساءً. هل التراس متاح لعشاء السبت؟'
        : 'We will arrive late, around 21:00. Is the terrace free for Saturday dinner?');
      await page.evaluate(() => document.activeElement.blur());
    }
    // run every scroll reveal so nothing is caught mid-fade
    await page.evaluate(async () => {
      // the page sets scroll-behavior: smooth, which would turn this into one
      // long animation and skip most of the reveals
      const root = document.documentElement;
      const prev = root.style.scrollBehavior;
      root.style.scrollBehavior = 'auto';
      for (let y = 0; y < document.body.scrollHeight; y += 400) {
        window.scrollTo(0, y);
        await new Promise(r => setTimeout(r, 90));
      }
      window.scrollTo(0, 0);
      root.style.scrollBehavior = prev;
    });
    await page.waitForTimeout(900);
    await page.screenshot({ path: 'screenshots/' + name + '.png', fullPage: true });
    console.log(name, width + 'px', path);
    await ctx.close();
  }
  await browser.close();
})();
