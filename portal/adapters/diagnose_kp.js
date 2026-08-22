await page.goto('https://kp.christuniversity.in/KnowledgePro/StudentLogin.do', { waitUntil: 'networkidle' });

await page.evaluate(() => {
  const inputs = Array.from(document.querySelectorAll('input, button')).map(i => ({
    name: i.getAttribute('name'),
    type: i.getAttribute('type'),
    id: i.getAttribute('id'),
    value: i.getAttribute('value')
  }));
  return {
    title: document.title,
    url: window.location.href,
    inputs: inputs
  };
});
