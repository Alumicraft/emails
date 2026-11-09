const assert = require('node:assert/strict');
const { test } = require('node:test');

process.env.RESEND_API_KEY = 're_local_test_only';
process.env.SERVICE_API_KEY = 'local-test-only';
const handler = require('../api/send.js').default;

async function request(req) {
  const response = { status(code) { this.code = code; return this; }, json(body) { this.body = body; return this; } };
  await handler(req, response);
  return response;
}

test('deployed handler advertises the generic notification template', async () => {
  const response = await request({ method: 'GET' });
  assert.equal(response.code, 200);
  assert.ok(response.body.templates.includes('notification'));
  assert.ok(response.body.templates.includes('flooring-packet-signed'));
});

test('notification renders title, HTML body and request link without claiming an attachment', async () => {
  const originalFetch = global.fetch;
  const sends = [];
  global.fetch = async (url, options) => {
    assert.equal(String(url), 'https://api.resend.com/emails');
    sends.push(JSON.parse(options.body));
    return new Response(JSON.stringify({ id: 'local-notification-proof' }), { status: 200 });
  };
  try {
    const response = await request({
      method: 'POST', headers: { authorization: 'Bearer local-test-only' },
      body: {
        template: 'notification', to: 'test@example.com', subject: 'Request update',
        from_email: 'sender@example.com', from_name: 'DCR',
        data: { title: 'Request <updated>', message: '<p><strong>HBR-TEST</strong> is ready.</p><p><a href="https://backdesk.dealercapital.net/portal#/request/HBR-TEST">Open request</a></p>' },
        branding: { company: 'DCR', primary_color: '#000000', text_color: '#1f1f1f', background_color: '#ffffff', font_family: 'Arial, sans-serif' },
      },
    });
    assert.equal(response.code, 200);
    assert.equal(response.body.message_id, 'local-notification-proof');
    assert.equal(sends.length, 1);
    const html = sends[0].html;
    assert.match(html, /Request &lt;updated&gt;/);
    assert.match(html, /<strong>HBR-TEST<\/strong>/);
    assert.match(html, /href="https:\/\/backdesk\.dealercapital\.net\/portal#\/request\/HBR-TEST"/);
    assert.doesNotMatch(html, /Please find the attached|&lt;p&gt;/);
    assert.equal(sends[0].attachments, undefined);
  } finally {
    global.fetch = originalFetch;
  }
});
