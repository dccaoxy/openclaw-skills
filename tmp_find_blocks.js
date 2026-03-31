const APP_ID = 'cli_a93d390a55f99cca';
const APP_SECRET = 'hnXqsu6Y4stY2FQMh0AIEBRNzu5q1ijN';
const DOC_TOKEN = 'ABcEdeFvDolz0TxEmoBcX2umnfh';

const TARGET_BLOCKS = [
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

async function getAllBlocks(token) {
  const allBlocks = [];
  let pageToken = '';
  
  do {
    const url = pageToken 
      ? `https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}/blocks?page_size=500&page_token=${pageToken}`
      : `https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}/blocks?page_size=500`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    
    if (data.code !== 0) {
      throw new Error(`Failed to get blocks: ${JSON.stringify(data)}`);
    }
    
    allBlocks.push(...data.data.items);
    pageToken = data.data.has_more ? data.data.page_token : '';
    
    console.log(`Fetched ${data.data.items.length} blocks, has_more: ${data.data.has_more}`);
  } while (pageToken);
  
  return allBlocks;
}

async function getBlock(token, blockId) {
  const response = await fetch(`https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}/blocks/${blockId}`, {
    method: 'GET',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const text = await response.text();
  return { status: response.status, data: JSON.parse(text) };
}

async function main() {
  console.log('Getting access token...');
  const token = await getAccessToken();
  console.log('Access token obtained.\n');

  console.log('=== Getting All Blocks ===');
  const allBlocks = await getAllBlocks(token);
  console.log(`Total blocks: ${allBlocks.length}\n`);

  // Create a map for quick lookup
  const blockMap = new Map();
  for (const block of allBlocks) {
    blockMap.set(block.block_id, block);
  }

  console.log('=== Checking Target Blocks ===');
  for (const blockId of TARGET_BLOCKS) {
    if (blockMap.has(blockId)) {
      const block = blockMap.get(blockId);
      console.log(`FOUND: ${blockId} (type: ${block.block_type})`);
    } else {
      console.log(`NOT FOUND: ${blockId}`);
    }
  }
}

main().catch(console.error);
