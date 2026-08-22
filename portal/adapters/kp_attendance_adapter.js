/**
 * WebCMD Adapter: Knowledge Pro (KP) Portal Attendance Extractor
 */

(async () => {
  const KP_BASE_URL = typeof process !== 'undefined' && process.env && process.env.KP_BASE_URL 
    ? process.env.KP_BASE_URL 
    : 'https://kp.christuniversity.in/KnowledgePro';

  const username = typeof process !== 'undefined' && process.env && process.env.KP_USERNAME ? process.env.KP_USERNAME : '';
  const password = typeof process !== 'undefined' && process.env && process.env.KP_PASSWORD ? process.env.KP_PASSWORD : '';

  const result = {
    timestamp: new Date().toISOString(),
    studentName: 'Student',
    studentId: username || 'Unknown',
    semester: 'Current',
    attendance: [],
    error: null
  };

  try {
    // 1. Navigate to attendance summary page
    await page.goto(
      `${KP_BASE_URL}/StudentLogin.do?method=initStudentWiseAttendanceSummary`,
      { waitUntil: 'networkidle', timeout: 30000 }
    );

    // 2. Check if redirected to login page (no active session)
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
        `${KP_BASE_URL}/StudentLogin.do?method=initStudentWiseAttendanceSummary`,
        { waitUntil: 'networkidle', timeout: 30000 }
      );
    }

    // 3. Extract metadata and attendance table
    const pageData = await page.evaluate(() => {
      let studentName = '';
      let studentId = '';
      let semester = 'Current';

      const bodyText = document.body.innerText || '';
      const nameMatch = bodyText.match(/Student\s*Name\s*:\s*([^\n\r]+)/i);
      if (nameMatch) studentName = nameMatch[1].trim();

      const idMatch = bodyText.match(/(?:Register|Roll|Student\s*ID)\s*No?\s*:\s*([A-Za-z0-9]+)/i);
      if (idMatch) studentId = idMatch[1].trim();

      const semMatch = bodyText.match(/Semester\s*:\s*([^\n\r]+)/i);
      if (semMatch) semester = semMatch[1].trim();

      const rows = Array.from(document.querySelectorAll('table tr'));
      const attendance = [];

      for (const row of rows) {
        const cells = Array.from(row.querySelectorAll('td, th')).map(c => c.innerText.trim());
        if (cells.length >= 4) {
          const firstCol = cells[0];
          const hasCourseCode = /^[A-Z0-9\-_]{3,12}$/i.test(firstCol);
          
          const numbers = [];
          for (let i = 0; i < cells.length; i++) {
            const num = parseInt(cells[i].replace(/[^\d]/g, ''), 10);
            if (!isNaN(num) && cells[i].length <= 4) {
              numbers.push({ index: i, val: num });
            }
          }

          if (hasCourseCode && numbers.length >= 2) {
            const held = numbers[0].val;
            const attended = numbers[1].val;
            const percentage = held > 0 ? parseFloat(((attended / held) * 100).toFixed(2)) : 100.0;

            attendance.push({
              subjectCode: cells[0],
              subjectName: cells[1] || 'Subject',
              classesHeld: held,
              classesAttended: attended,
              percentage: percentage,
              status: percentage < 85.0 ? 'WARNING' : 'OK'
            });
          }
        }
      }

      return { studentName, studentId, semester, attendance };
    });

    if (pageData.studentName) result.studentName = pageData.studentName;
    if (pageData.studentId) result.studentId = pageData.studentId;
    if (pageData.semester) result.semester = pageData.semester;
    result.attendance = pageData.attendance;

  } catch (err) {
    result.error = err.message || String(err);
  } finally {
    // 4. CRITICAL: Gracefully logout to avoid the 15-minute Struts account lockout
    try {
      await page.goto(`${KP_BASE_URL}/StudentLogin.do?method=logout`, { timeout: 8000 }).catch(() => {});
    } catch (e) {}
  }

  console.log(JSON.stringify(result));
})();
