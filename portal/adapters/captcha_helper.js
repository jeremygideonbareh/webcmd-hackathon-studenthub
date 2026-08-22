/**
 * Full Automated KP Login with CAPTCHA OCR Solver
 */

import { createWorker } from 'tesseract.js';

export async function solveCaptchaFromDataUrl(dataUrl) {
  const worker = await createWorker('eng');
  try {
    const base64Data = dataUrl.replace(/^data:image\/\w+;base64,/, '');
    const buffer = Buffer.from(base64Data, 'base64');
    
    await worker.setParameters({
      tessedit_char_whitelist: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
      tessedit_pageseg_mode: '7'
    });

    const ret = await worker.recognize(buffer);
    const text = ret.data.text.trim().replace(/[^a-zA-Z0-9]/g, '');
    return text;
  } finally {
    await worker.terminate();
  }
}
