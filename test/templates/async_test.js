async (page) => {
  page.on('dialog', dialog => dialog.accept());
  await page.reload();
  await page.waitForLoadState('networkidle');
  await page.locator('input[type=file]').setInputFiles('{{INPUT_PATH}}');
  await page.waitForTimeout(500);
  await page.getByLabel('选择转换类型').selectOption('{{CONV_TYPE}}');
  await page.getByRole('button', { name: '开始处理' }).click();
  const maxWait = 600000;
  const start = Date.now();
  while (Date.now() - start < maxWait) {
    await page.waitForTimeout(5000);
    const success = await page.locator('.alert-success').count();
    const error = await page.locator('.alert-danger').count();
    if (success > 0) break;
    if (error > 0) {
      const errorText = await page.locator('.alert-danger').textContent();
      return 'ERROR:' + errorText.trim();
    }
  }
  if (Date.now() - start >= maxWait) return 'TIMEOUT';
  const elapsed = Math.round((Date.now() - start) / 1000);
  return 'SUCCESS:' + elapsed + 's';
}
