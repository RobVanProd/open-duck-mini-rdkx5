#!/usr/bin/env node
/* Launch a persistent Chrome window for Colab browser-control work.

This script intentionally lives in the repo, but Playwright itself is installed
outside the repo at /home/lsd/robots/browser-control/node_modules/playwright.
*/

const playwrightPath =
  process.env.PLAYWRIGHT_PACKAGE_PATH ||
  '/home/lsd/robots/browser-control/node_modules/playwright';
const { chromium } = require(playwrightPath);

const profile =
  process.env.OPEN_DUCK_COLAB_PROFILE ||
  '/home/lsd/robots/browser-control/playwright-chrome-profile';
const cdpPort = process.env.OPEN_DUCK_COLAB_CDP_PORT || '9223';
const startUrl =
  process.env.OPEN_DUCK_COLAB_URL || 'https://colab.research.google.com/';

(async () => {
  const context = await chromium.launchPersistentContext(profile, {
    channel: 'chrome',
    headless: false,
    viewport: null,
    args: [
      `--remote-debugging-port=${cdpPort}`,
      '--no-first-run',
      '--start-maximized',
    ],
  });

  let page = context.pages()[0];
  if (!page) page = await context.newPage();
  await page.goto(startUrl, { waitUntil: 'domcontentloaded' });

  console.log('PLAYWRIGHT_COLAB_READY');
  console.log(`CDP=http://127.0.0.1:${cdpPort}`);
  console.log(`PROFILE=${profile}`);

  const close = async () => {
    await context.close();
    process.exit(0);
  };
  process.on('SIGINT', close);
  process.on('SIGTERM', close);

  await new Promise(() => {});
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
