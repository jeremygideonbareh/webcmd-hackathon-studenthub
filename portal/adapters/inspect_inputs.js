await page.goto('https://kp.christuniversity.in/KnowledgePro/StudentLogin.do', { waitUntil: 'networkidle' });

const allInputs = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('input')).map(i => ({
    name: i.name,
    id: i.id,
    type: i.type,
    value: i.value,
    placeholder: i.placeholder,
    outerHTML: i.outerHTML
  }));
});

console.log(JSON.stringify(allInputs, null, 2));
