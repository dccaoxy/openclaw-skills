const APP_ID = 'cli_a93d390a55f99cca';
const APP_SECRET = 'hnXqsu6Y4stY2FQMh0AIEBRNzu5q1ijN';
const DOC_TOKEN = 'ABcEdeFvDolz0TxEmoBcX2umnfh';

const BLOCK_IDS = [
  'doxcnPrl1VywCOcS8LrsDvgO9Vb',
  'doxcnV1gc2NIXgrhS7ws4HCAhXg',
  'doxcn33SzbfPpDt2YMW5PphoRVh',
  'doxcncUOJNT72dsAz9FJW6K94Zc',
  'doxcnsslPRkEr5eVUycqsO60y9e',
  'doxcn4deMOgyW2FZYu5iDeaxC0c',
  'doxcnxwzu37XZrnqeVkfs5Lswwb',
  'doxcnic40nJuWBw9GPBW7C4I9Ya',
  'doxcnmHiJQ4Y087KrOJQLyGHtDd',
  'doxcnB6Do9jWN0ABh3yMAReNoRe',
  'doxcn3EPgEre6G67khh7Hr3nmJd',
  'doxcn1xn1Io2MXv089i3TUat5EZ'
];

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

async function deleteBlock(token, blockId) {
  const response = await fetch(`https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}/blocks/${blockId}`, {
    method: 'DELETE',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text, status: response.status };
  }
  return { ok: response.ok, status: response.status, data };
}

async function main() {
  console.log('Getting access token...');
  const token = await getAccessToken();
  console.log('Access token obtained.\n');

  const results = [];
  for (const blockId of BLOCK_IDS) {
    console.log(`Deleting block: ${blockId}`);
    const result = await deleteBlock(token, blockId);
    console.log(`  Status: ${result.status}, OK: ${result.ok}`);
    console.log(`  Response: ${JSON.stringify(result.data)}`);
    results.push({ blockId, result });
    
    // Add a small delay between requests
    await new Promise(resolve => setTimeout(resolve, 300));
  }

  console.log('\n=== Summary ===');
  for (const { blockId, result } of results) {
    const status = result.ok ? 'SUCCESS' : 'FAILED';
    console.log(`${status} (${result.status}): ${blockId}`);
  }
}

main().catch(console.error);
