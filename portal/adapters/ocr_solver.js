/**
 * CAPTCHA OCR Solver using Tesseract.js
 */
import { createWorker } from 'tesseract.js';
import fs from 'fs';

export async function solveCaptcha(imagePathOrBase64) {
  const worker = await createWorker('eng');
  try {
    // If base64 data URL
    let imageSource = imagePathOrBase64;
    if (imagePathOrBase64.startsWith('data:image')) {
      const base64Data = imagePathOrBase64.replace(/^data:image\/\w+;base64,/, '');
      imageSource = Buffer.from(base64Data, 'base64');
    }

    // Configure OCR for alphanumeric characters only
    await worker.setParameters({
      tessedit_char_whitelist: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
      tessedit_pageseg_mode: '7' // Single line text
    });

    const ret = await worker.recognize(imageSource);
    const text = ret.data.text.trim().replace(/[^a-zA-Z0-9]/g, '');
    return text;
  } finally {
    await worker.terminate();
  }
}

// If run directly via CLI
if (process.argv[1] && process.argv[1].endsWith('ocr_solver.js')) {
  const sampleBase64 = process.argv[2];
  if (sampleBase64) {
    solveCaptcha(sampleBase64).then(text => {
      console.log(JSON.stringify({ captchaText: text }));
    }).catch(err => {
      console.error(err);
      process.exit(1);
    });
  }
}
