document.addEventListener('DOMContentLoaded',()=>{
  const sidebar=document.getElementById('appSidebar'),overlay=document.getElementById('sidebarOverlay'),mobileMenu=document.getElementById('mobileMenu'),sidebarClose=document.getElementById('sidebarClose');
  const setSidebar=open=>{if(!sidebar)return;sidebar.classList.toggle('open',open);overlay?.classList.toggle('show',open);document.body.classList.toggle('menu-open',open)};
  mobileMenu?.addEventListener('click',()=>setSidebar(true));
  sidebarClose?.addEventListener('click',()=>setSidebar(false));
  overlay?.addEventListener('click',()=>setSidebar(false));
  document.querySelectorAll('.nav-link').forEach(link=>link.addEventListener('click',()=>setSidebar(false)));

  const esc=value=>String(value??'').replace(/[&<>'\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#039;','\"':'&quot;'}[c]));
  const download=(blob,filename)=>{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
  const safeName=value=>String(value||'orange-learn-export').replace(/[^a-z0-9._-]+/gi,'-').replace(/^-+|-+$/g,'').slice(0,70)||'orange-learn-export';

  function wordExport(title,content){
    const text=String(content||'').trim();
    if(!text){alert('Tidak ada konten untuk diekspor ke Word.');return;}
    const paragraphs=text.split(/\n\s*\n/).flatMap(block=>block.split('\n')).filter(Boolean).map(line=>{
      const value=esc(line.trim());
      if(/^•\s/.test(line.trim())) return `<p style="margin:5pt 0 5pt 18pt">• ${value.slice(2)}</p>`;
      if(/^\d+[.)]\s/.test(line.trim())) return `<p style="margin:5pt 0">${value}</p>`;
      return `<p style="margin:7pt 0;line-height:1.5">${value}</p>`;
    }).join('');
    const html=`<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title><style>body{font-family:Arial,sans-serif;margin:36pt;color:#222}h1{font-size:18pt;text-align:center;margin-bottom:24pt}p{font-size:10.5pt}</style></head><body><h1>${esc(title)}</h1>${paragraphs}</body></html>`;
    download(new Blob([html],{type:'application/msword'}),safeName(title)+'.doc');
  }

  function excelExport(title,headers,rows){
    headers=(headers||[]).map(String); rows=rows||[];
    if(!headers.length){headers=['Bagian','Isi'];rows=String(title||'').split(/\n+/).filter(Boolean).map((x,i)=>[i+1,x]);}
    const escXml=v=>esc(String(v??'')).replace(/\n/g,'&#10;');
    const headerRow=headers.map(h=>`<Cell ss:StyleID="Header"><Data ss:Type="String">${escXml(h)}</Data></Cell>`).join('');
    const body=rows.slice(0,10000).map(row=>`<Row>${headers.map((_,i)=>{const v=row?.[i]??'';const numeric=v!==''&&v!==null&&!Number.isNaN(Number(v))?'Number':'String';return `<Cell><Data ss:Type="${numeric}">${escXml(v)}</Data></Cell>`}).join('')}</Row>`).join('');
    const xml=`<?xml version="1.0"?><Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"><Styles><Style ss:ID="Header"><Font ss:Bold="1"/></Style></Styles><Worksheet ss:Name="Orange Learn"><Table><Row>${headerRow}</Row>${body}</Table></Worksheet></Workbook>`;
    download(new Blob([xml],{type:'application/vnd.ms-excel'}),safeName(title)+'.xls');
  }

  function tableDataFromDom(){
    const table=document.querySelector('#result-table table');
    if(!table)return null;
    const rows=[...table.querySelectorAll('tr')].map(tr=>[...tr.querySelectorAll('th,td')].map(td=>td.innerText.trim()));
    if(!rows.length)return null;
    return {headers:rows[0],rows:rows.slice(1)};
  }

  function addButton(parent,label,kind,handler){
    if(parent.querySelector(`[data-local-export="${kind}"]`))return;
    const b=document.createElement('button');b.type='button';b.className='ai-export-btn local-export-btn';b.dataset.localExport=kind;b.textContent=label;b.addEventListener('click',handler);parent.appendChild(b);
  }

  function enhanceAiExports(){
    const chat=document.getElementById('chatMessages');if(!chat)return;
    chat.querySelectorAll('.message.bot').forEach(message=>{
      const rich=message.querySelector('.ai-rich-text');if(!rich)return;
      let actions=message.querySelector('.ai-export-actions');
      if(!actions){actions=document.createElement('div');actions.className='ai-export-actions';message.querySelector('.message-content')?.appendChild(actions);}
      const title='orange-learn • Jawaban AI';
      addButton(actions,'▣ Word','word',()=>wordExport(title,rich.innerText));
      addButton(actions,'▦ Excel','excel',()=>excelExport(title,['Bagian','Isi'],rich.innerText.split(/\n+/).filter(Boolean).map((x,i)=>[i+1,x])));
    });
  }

  function enhanceWorkflowExports(){
    const csv=document.getElementById('exportCsvBtn');if(!csv)return;
    const parent=csv.parentElement;if(!parent)return;
    if(!document.getElementById('exportWordLocalBtn')){
      const b=document.createElement('button');b.className='canvas-action export-local-action';b.id='exportWordLocalBtn';b.type='button';b.textContent='▣ Word';b.title='Unduh laporan workflow ke Word';b.addEventListener('click',()=>{
        const dataset=tableDataFromDom();
        const log=document.querySelector('#result-log')?.innerText||'';
        const overview=document.querySelector('#result-overview')?.innerText||'';
        const content=dataset?`Dataset\n${dataset.headers.join(' | ')}\n${dataset.rows.map(r=>r.join(' | ')).join('\n')}\n\nLog Workflow\n${log}`:`Workflow orange-learn\n\n${overview}\n\n${log}`;
        wordExport('orange-learn • Laporan Workflow',content);
      });
      parent.appendChild(b);
    }
    if(!document.getElementById('exportExcelLocalBtn')){
      const b=document.createElement('button');b.className='canvas-action export-local-action';b.id='exportExcelLocalBtn';b.type='button';b.textContent='▦ Excel';b.title='Unduh dataset ke Excel';b.addEventListener('click',()=>{
        const dataset=tableDataFromDom();
        if(!dataset){alert('Jalankan workflow atau buka Data Table terlebih dahulu agar data tersedia.');return;}
        excelExport('orange-learn • Dataset',dataset.headers,dataset.rows);
      });
      parent.appendChild(b);
    }
  }

  const observer=new MutationObserver(()=>{enhanceAiExports();enhanceWorkflowExports();});
  observer.observe(document.body,{childList:true,subtree:true});
  enhanceAiExports();enhanceWorkflowExports();
});

/* File widget UX: double-click the File node to open the CSV picker.
   This capture handler intentionally runs before the workflow page's own
   bubble handler so the action is reliable even after canvas re-renders. */
document.addEventListener('dblclick',event=>{
  const node=event.target.closest?.('.orange-node');
  if(!node) return;
  const name=node.querySelector('.orange-node-main strong')?.textContent?.trim().toLowerCase();
  if(name!=='file') return;
  const input=document.getElementById('csvInput');
  if(!input) return;
  event.preventDefault();
  event.stopPropagation();
  if(typeof event.stopImmediatePropagation==='function') event.stopImmediatePropagation();
  input.value='';
  input.click();
},{capture:true});

/* Google Sheets export fix: the Sheets values.update API expects
   valueInputOption as a query parameter, not inside the JSON body. */
async function orangeLearnGoogleSheetsDirect(kind,content){
  if(kind!=='sheets') return false;
  const token=await window.googleAccessToken();
  const title='orange-learn • Catatan AI';
  const lines=String(content||'').trim().split(/\n+/).filter(Boolean);
  const values=[['Bagian','Isi'],...lines.map((line,i)=>[String(i+1),line])];
  const createResponse=await fetch('https://sheets.googleapis.com/v4/spreadsheets',{
    method:'POST',
    headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},
    body:JSON.stringify({properties:{title}})
  });
  const created=await createResponse.json();
  if(!createResponse.ok) throw new Error(created?.error?.message||'Gagal membuat Google Sheets.');
  const spreadsheetId=created.spreadsheetId;
  const range=`Sheet1!A1:B${Math.max(values.length,1)}`;
  const updateUrl='https://sheets.googleapis.com/v4/spreadsheets/'+encodeURIComponent(spreadsheetId)+'/values/'+encodeURIComponent(range)+'?valueInputOption=USER_ENTERED';
  const updateResponse=await fetch(updateUrl,{
    method:'PUT',
    headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},
    body:JSON.stringify({range,majorDimension:'ROWS',values})
  });
  const updated=await updateResponse.json();
  if(!updateResponse.ok) throw new Error(updated?.error?.message||'Gagal mengisi data Google Sheets.');
  const url='https://docs.google.com/spreadsheets/d/'+encodeURIComponent(spreadsheetId)+'/edit';
  window.open(url,'_blank','noopener');
  return true;
}

document.addEventListener('DOMContentLoaded',()=>{
  if(typeof window.exportAiToGoogle!=='function') return;
  const original=window.exportAiToGoogle;
  window.exportAiToGoogle=async function(kind,content){
    if(kind==='sheets'){
      try{
        await orangeLearnGoogleSheetsDirect(kind,content);
      }catch(err){
        const chatMessages=document.getElementById('chatMessages');
        const message=document.createElement('div');message.className='message bot';
        message.innerHTML='<div class="message-avatar">🤖</div><div class="message-content"><strong>orange-learn AI</strong><div class="ai-rich-text"><p>Ekspor Google Sheets gagal: '+escGoogle(err?.message||err)+'</p></div></div>';
        chatMessages?.appendChild(message);
      }
      return;
    }
    return original(kind,content);
  };
});

function escGoogle(value){return String(value??'').replace(/[&<>'\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#039;','\"':'&quot;'}[c]));}
