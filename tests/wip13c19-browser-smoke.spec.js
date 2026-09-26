const path = require('node:path');
const { test, expect } = require('@playwright/test');

test.use({
  viewport: { width: 1440, height: 900 },
  launchOptions: { args: ['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader'] }
});

test('C19 starts, runs core checks and opens the 3D ship view', async ({ page }) => {
  test.setTimeout(180_000);
  const pageErrors = [], consoleErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 1350501; });
  const file = path.basename(process.env.SIM_FILE || 'Aegis_SIM_v48_WIP13C19.html');
  await page.goto(`http://127.0.0.1:4173/${file}`, { waitUntil: 'load', timeout: 120_000 });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__), null, { timeout: 60_000 });
  expect(await page.evaluate(() => window.__CORE_SELFTEST_FAILURES__)).toEqual([]);
  await expect(page.locator('#external3dBtn')).toBeVisible();
  await page.locator('#external3dBtn').click();
  await expect(page.locator('#external3DView')).toHaveAttribute('aria-hidden', 'false', { timeout: 45_000 });
  await expect(page.locator('#external3DCanvas')).toBeVisible();
  const view = await page.evaluate(() => ({
    width: document.querySelector('#external3DCanvas').width,
    height: document.querySelector('#external3DCanvas').height,
    servoMounts: window.get3DRenderState?.()?.illum?.spg62Mounts?.length ?? null
  }));
  expect(view.width).toBeGreaterThan(0);
  expect(view.height).toBeGreaterThan(0);
  expect(view.servoMounts).toBe(3);
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});
