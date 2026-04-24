async (page) => {
  page.on('dialog', dialog => dialog.accept());
  await page.reload();
  await page.waitForLoadState('networkidle');
  await page.locator('input[type=file]').setInputFiles('{{INPUT_PATH}}');
  await page.waitForTimeout(500);
  await page.getByLabel('选择转换类型').selectOption('{{CONV_TYPE}}');
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: '开始处理' }).click();
  const download = await downloadPromise;
  await download.saveAs('{{OUTPUT_PATH}}');
  return download.suggestedFilename();
}
