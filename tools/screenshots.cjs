/* Screenshots for review. Needs a static server on the site root and a
   Chromium build:
     python3 -m http.server 8123
     NODE_PATH=$(npm root -g) node tools/screenshots.cjs
   Override with BASE_URL and CHROME_PATH if your paths differ, e.g.
     BASE_URL=http://127.0.0.1:8123/dar-chams/ node tools/screenshots.cjs */
const CHROME = process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const BASE = process.env.BASE_URL || 'http://127.0.0.1:8123/';
const { chromium } = require((process.env.NODE_PATH || '') + '/playwright-core');

const SHOTS = [
  ['01-home-1440',            'index.html',   1440],
  ['02-home-390',             'index.html',    390],
  ['03-rooms-1440',           'rooms.html',   1440],
  ['04-rooms-390',            'rooms.html',    390],
  ['05-village-1440',         'village.html', 1440],
  ['06-village-390',          'village.html',  390],
  ['07-contact-1440',         'contact.html', 1440],
  ['08-contact-390',          'contact.html',  390],
  ['09-contact-filled-1440',  'contact.html', 1440, { fill: true }],
  ['10-contact-filled-390',   'contact.html',  390, { fill: true }],
  ['11-contact-ar-filled-1440','contact.html?lang=ar', 1440, { fill: true, ar: true }],
  ['12-home-ar-1440',         'index.html?lang=ar', 1440],
  ['13-home-ar-390',          'index.html?lang=ar',  390],
  ['14-rooms-ar-1440',        'rooms.html?lang=ar', 1440],
  ['15-village-ar-390',       'village.html?lang=ar', 390]
];

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME });
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
