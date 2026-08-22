await page.goto('https://kp.christuniversity.in/KnowledgePro/StudentLogin.do', { waitUntil: 'networkidle' });

const formFields = await page.evaluate(() => {
  const form = document.querySelector('form[action*="StudentLogin.do"]');
  if (!form) return null;
  return Array.from(form.querySelectorAll('input, select, textarea')).map(i => ({
    name: i.name,
    id: i.id,
    type: i.type,
    value: i.value,
    placeholder: i.placeholder
  }));
});

console.log(JSON.stringify(formFields, null, 2));
