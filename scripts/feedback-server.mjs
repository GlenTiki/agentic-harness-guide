import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const DATA_DIR = path.join(ROOT, 'data');
const INBOX_FILE = path.join(DATA_DIR, 'feedback-inbox.jsonl');
const PORT = Number(process.env.FEEDBACK_PORT || 4328);

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

const sendJson = (res, statusCode, data) => {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(JSON.stringify(data));
};

const server = http.createServer((req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    return res.end();
  }

  const url = new URL(req.url, `http://${req.headers.host || '127.0.0.1'}`);

  if (url.pathname === '/api/health' && req.method === 'GET') {
    let count = 0;
    if (fs.existsSync(INBOX_FILE)) {
      const lines = fs.readFileSync(INBOX_FILE, 'utf8').trim().split('\n').filter(Boolean);
      count = lines.length;
    }
    return sendJson(res, 200, {
      status: 'ok',
      service: 'feedback-receiver',
      totalFeedbackItems: count,
      uptimeSeconds: Math.round(process.uptime()),
    });
  }

  if (url.pathname === '/api/feedback' && req.method === 'GET') {
    if (!fs.existsSync(INBOX_FILE)) {
      return sendJson(res, 200, { feedback: [] });
    }
    const lines = fs.readFileSync(INBOX_FILE, 'utf8').trim().split('\n').filter(Boolean);
    const feedback = lines.map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return { raw: line };
      }
    });
    return sendJson(res, 200, { feedback, total: feedback.length });
  }

  if (url.pathname === '/api/feedback' && req.method === 'POST') {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
      if (body.length > 1e6) {
        req.destroy();
      }
    });

    req.on('end', () => {
      try {
        const payload = JSON.parse(body || '{}');
        const comment = (payload.feedback || payload.comment || '').trim();
        if (!comment && !payload.quote) {
          return sendJson(res, 400, { error: 'Feedback comment or quote is required.' });
        }

        const entry = {
          id: `fb_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
          timestamp: new Date().toISOString(),
          page: payload.page || 'unknown',
          section: payload.section || '',
          quote: payload.quote || '',
          category: payload.category || 'general',
          feedback: comment,
          device: payload.device || '',
          userAgent: req.headers['user-agent'] || '',
        };

        fs.appendFileSync(INBOX_FILE, `${JSON.stringify(entry)}\n`, 'utf8');
        process.stdout.write(`[FEEDBACK INBOX] Received feedback #${entry.id} for ${entry.page} (${entry.category}): "${comment.slice(0, 80)}"\n`);

        return sendJson(res, 201, {
          status: 'ok',
          id: entry.id,
          receivedAt: entry.timestamp,
        });
      } catch (err) {
        return sendJson(res, 400, { error: 'Invalid JSON payload' });
      }
    });
    return;
  }

  sendJson(res, 404, { error: 'Not found' });
});

server.listen(PORT, '0.0.0.0', () => {
  process.stdout.write(`Feedback receiver listening at http://0.0.0.0:${PORT} (local IP http://192.168.1.25:${PORT})\n`);
  process.stdout.write(`Writing incoming feedback to ${INBOX_FILE}\n`);
});
