/**
 * WebCMD Adapter: Knowledge Pro (KP) Portal GPA / Grades Extractor
 */

(async () => {
  const KP_BASE_URL = typeof process !== 'undefined' && process.env && process.env.KP_BASE_URL 
    ? process.env.KP_BASE_URL 
    : 'https://kp.christuniversity.in/KnowledgePro';

  const username = typeof process !== 'undefined' && process.env && process.env.KP_USERNAME ? process.env.KP_USERNAME : '';
  const password = typeof process !== 'undefined' && process.env && process.env.KP_PASSWORD ? process.env.KP_PASSWORD : '';

  const result = {
    timestamp: new Date().toISOString(),
    studentId: username || 'Unknown',
    cgpa: 0.0,
    sgpa: 0.0,
    error: null
  };

  try {
    // 1. Navigate to exam/marks summary page
    await page.goto(
      `${KP_BASE_URL}/StudentLogin.do?method=initStudentMarksCard`,
      { waitUntil: 'networkidle', timeout: 30000 }
    );

    // 2. Check if redirected to login page
    const currentUrl = await page.url();
    const isLoginPage = currentUrl.includes('StudentLogin.do') && (await page.$('input[name="userName"]'));
    if (isLoginPage && username && password) {
      await page.fill('input[name="userName"]', username);
      await page.fill('input[name="password"]', password);
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }).catch(() => {}),
        page.click('input[type="submit"], button[type="submit"], input[value="Login"]')
      ]);

      await page.goto(
        `${KP_BASE_URL}/StudentLogin.do?method=initStudentMarksCard`,
        { waitUntil: 'networkidle', timeout: 30000 }
      );
    }

    // 3. Extract CGPA and SGPA
    const gpaData = await page.evaluate(() => {
      let cgpa = 0.0;
      let sgpa = 0.0;
      const text = document.body.innerText || '';

      const cgpaMatch = text.match(/CGPA\s*[:=\-]?\s*([0-9]+\.[0-9]+)/i);
      if (cgpaMatch) cgpa = parseFloat(cgpaMatch[1]);

      const sgpaMatch = text.match(/SGPA\s*[:=\-]?\s*([0-9]+\.[0-9]+)/i);
      if (sgpaMatch) sgpa = parseFloat(sgpaMatch[1]);

      return { cgpa, sgpa };
    });

    result.cgpa = gpaData.cgpa;
    result.sgpa = gpaData.sgpa;

  } catch (err) {
    result.error = err.message || String(err);
  } finally {
    // Gracefully logout
    try {
      await page.goto(`${KP_BASE_URL}/StudentLogin.do?method=logout`, { timeout: 8000 }).catch(() => {});
    } catch (e) {}
  }

  console.log(JSON.stringify(result));
})();
