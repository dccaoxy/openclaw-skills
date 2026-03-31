const APP_ID = 'cli_a93d390a55f99cca';
const APP_SECRET = 'hnXqsu6Y4stY2FQMh0AIEBRNzu5q1ijN';
const DOC_TOKEN = 'ABcEdeFvDolz0TxEmoBcX2umnfh';

async function getAccessToken() {
  const response = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: APP_ID, app_secret: APP_SECRET })
  });
  const data = await response.json();
  if (data.code !== 0) {
    throw new Error(`Failed to get access token: ${JSON.stringify(data)}`);
  }
  return data.tenant_access_token;
}

async function getDocumentInfo(token) {
  const response = await fetch(`https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}`, {
    method: 'GET',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const text = await response.text();
  console.log(`Status: ${response.status}`);
  console.log(`Response: ${text}`);
  return { status: response.status, data: JSON.parse(text) };
}

async function getBlockList(token) {
  const response = await fetch(`https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}/blocks?page_size=50`, {
    method: 'GET',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const text = await response.text();
  console.log(`Status: ${response.status}`);
  console.log(`Response: ${text.substring(0, 2000)}`);
  return { status: response.status, data: JSON.parse(text) };
}

async function main() {
  console.log('Getting access token...');
  const token = await getAccessToken();
  console.log('Access token obtained.\n');

  console.log('=== Getting Document Info ===');
  await getDocumentInfo(token);
  
  console.log('\n=== Getting Block List ===');
  await getBlockList(token);
}

main().catch(console.error);
