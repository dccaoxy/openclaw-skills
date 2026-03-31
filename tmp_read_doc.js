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
  } while (pageToken);
  
  return allBlocks;
}

async function getBlockContent(token, blockId) {
  const response = await fetch(`https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}/blocks/${blockId}`, {
    method: 'GET',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
}

function getTextFromBlock(block) {
  if (block.text) {
    return block.text.elements?.map(e => e.text_run?.content || '').join('') || '';
  }
  return '';
}

async function main() {
  console.log('Getting access token...');
  const token = await getAccessToken();
  console.log('Access token obtained.\n');

  console.log('=== Getting All Blocks ===');
  const allBlocks = await getAllBlocks(token);
  console.log(`Total blocks: ${allBlocks.length}\n`);

  // Print all blocks with their content
  console.log('=== All Blocks ===');
  for (const block of allBlocks) {
    const text = getTextFromBlock(block);
    const preview = text.substring(0, 80).replace(/\n/g, ' ');
    console.log(`${block.block_id} [type:${block.block_type}] "${preview}"`);
  }
}

main().catch(console.error);
