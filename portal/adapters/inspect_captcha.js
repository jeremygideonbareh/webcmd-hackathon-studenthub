await page.goto('https://kp.christuniversity.in/KnowledgePro/StudentLogin.do', { waitUntil: 'networkidle' });

const captchaInfo = await page.evaluate(() => {
  const images = Array.from(document.querySelectorAll('img')).map(img => ({
    src: img.src,
    id: img.id,
    name: img.name,
    className: img.className,
    width: img.width,
    height: img.height,
    alt: img.alt
  }));
  
  const captchaInput = document.querySelector('input[placeholder*="Type the text"], input[name*="captcha" i], input[name*="code" i]');
  
  return {
    images: images,
    captchaInput: captchaInput ? {
      name: captchaInput.getAttribute('name'),
      id: captchaInput.getAttribute('id'),
      placeholder: captchaInput.getAttribute('placeholder')
    } : null
  };
});

console.log(JSON.stringify(captchaInfo, null, 2));
