const {test, expect} = require('@playwright/test');
const { chromium } = require('@playwright/test');

// uses authenticated storage state to skip the catcha before running the test
test.use({storageState: 'auth.json'});

test('real estate test', async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('https://larizzare.com/');
  await page.getByRole('link', { name: 'Services' }).click();
  await page.getByRole('link', { name: 'Contact' }).nth(1).click();

  // ---------------------
  await context.close();
  await browser.close();
});