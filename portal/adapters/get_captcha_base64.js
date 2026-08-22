await page.goto('https://kp.christuniversity.in/KnowledgePro/StudentLogin.do', { waitUntil: 'networkidle' });

const captchaData = await page.evaluate(async () => {
  const img = document.querySelector('#captcha_img');
  if (!img) return null;

  const canvas = document.createElement('canvas');
  canvas.width = img.naturalWidth || img.width;
  canvas.height = img.naturalHeight || img.height;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0);
  return {
    src: img.src,
    width: canvas.width,
    height: canvas.height,
    dataUrl: canvas.toDataURL('image/png')
  };
});

console.log(JSON.stringify(captchaData, null, 2));
