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

  const observer=new MutationObserver(()=>{enhanceAiExports();enhanceWorkflowExports();upgradeOrangeIcons();});
  observer.observe(document.body,{childList:true,subtree:true});
  enhanceAiExports();enhanceWorkflowExports();upgradeOrangeIcons();
});

function orangeIconSvg(name){
  const n=String(name||'').toLowerCase();
  const common='width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';
  if(n==='file') return `<svg ${common}><path d="M6 3.5h8l4 4V20.5H6z"/><path d="M14 3.5v4h4"/><path d="M8.5 12.5h7M8.5 16h7"/></svg>`;
  if(n.includes('csv')) return `<svg ${common}><rect x="4" y="3.5" width="16" height="17" rx="1.5"/><path d="M4 8h16M9 8v12.5M15 8v12.5M4 13.5h16M4 17h16"/></svg>`;
  if(n.includes('data table')) return `<svg ${common}><rect x="3.5" y="4" width="17" height="16" rx="1.5"/><path d="M3.5 9h17M3.5 14h17M9 4v16M15 4v16"/></svg>`;
  if(n.includes('scatter')) return `<svg ${common}><path d="M4 20V4M4 20h16"/><circle cx="8" cy="15" r="1" fill="currentColor"/><circle cx="11" cy="10" r="1" fill="currentColor"/><circle cx="14" cy="13" r="1" fill="currentColor"/><circle cx="18" cy="7" r="1" fill="currentColor"/></svg>`;
  if(n.includes('distribution')||n.includes('histogram')) return `<svg ${common}><path d="M4 20V4M4 20h17"/><path d="M7 20v-6h3v6M12 20V9h3v11M17 20V6h3v14"/></svg>`;
  if(n.includes('box plot')) return `<svg ${common}><path d="M4 12h4M16 12h4M8 8h8v8H8zM12 5v3M12 16v3M10 12h4"/></svg>`;
  if(n.includes('tree')) return `<svg ${common}><circle cx="12" cy="5" r="2.2"/><circle cx="7" cy="18" r="2.2"/><circle cx="17" cy="18" r="2.2"/><path d="M12 7.2v4.2M12 11.4H7v4.4M12 11.4h5v4.4"/></svg>`;
  if(n.includes('random forest')) return `<svg ${common}><path d="M12 4l-3 5h2l-3 4h3l-4 5h10l-4-5h3l-3-4h2z"/></svg>`;
  if(n.includes('pca')) return `<svg ${common}><path d="M5 19L19 5M7 7l12 12"/><circle cx="7" cy="7" r="1.4" fill="currentColor"/><circle cx="17" cy="17" r="1.4" fill="currentColor"/></svg>`;
  if(n.includes('k-means')||n.includes('knn')) return `<svg ${common}><circle cx="7" cy="8" r="2"/><circle cx="16" cy="7" r="2"/><circle cx="9" cy="17" r="2"/><circle cx="17" cy="16" r="2"/><path d="M9 9.5l5 5M15 8.5l-4 6"/></svg>`;
  if(n.includes('regression')||n.includes('svm')) return `<svg ${common}><path d="M4 19L20 5"/><circle cx="8" cy="15.5" r="1.6"/><circle cx="13" cy="11.5" r="1.6"/><circle cx="17" cy="8" r="1.6"/></svg>`;
  if(n.includes('test & score')||n.includes('evaluation')) return `<svg ${common}><circle cx="12" cy="12" r="8.5"/><path d="M8 12l2.5 2.5L16 9"/></svg>`;
  if(n.includes('confusion')) return `<svg ${common}><rect x="4" y="4" width="16" height="16" rx="1"/><path d="M12 4v16M4 12h16"/></svg>`;
  if(n.includes('select')||n.includes('transform')||n.includes('preprocess')||n.includes('normalize')) return `<svg ${common}><path d="M6 5h12M8 12h8M10 19h4"/></svg>`;
  if(n.includes('distribution')||n.includes('visual')) return `<svg ${common}><path d="M4 20V4M4 20h17M7 17l4-6 3 3 4-8"/></svg>`;
  return `<svg ${common}><circle cx="12" cy="12" r="8.5"/><path d="M8 12h8M12 8v8"/></svg>`;
}

function upgradeOrangeIcons(){
  document.querySelectorAll('.orange-tool-item').forEach(btn=>{
    const icon=btn.querySelector('.simple-tool-icon');
    const name=btn.dataset.name||btn.querySelector('.orange-tool-copy strong')?.textContent||'';
    if(icon){icon.innerHTML=orangeIconSvg(name);icon.classList.add('orange-svg-icon');}
  });
  document.querySelectorAll('.orange-node').forEach(node=>{
    const icon=node.querySelector('.orange-node-icon');
    const name=node.querySelector('.orange-node-main strong')?.textContent||'';
    if(icon){icon.innerHTML=orangeIconSvg(name);icon.classList.add('orange-svg-icon');}
  });
}

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

/* Compact Orange-inspired widget icon styling. */
const orangeIconStyle=document.createElement('style');
orangeIconStyle.textContent=`
.orange-svg-icon{width:34px!important;height:34px!important;min-width:34px!important;border-radius:8px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;background:#fff8e8!important;color:#b7791f!important;border:1px solid #efd39a!important;box-shadow:inset 0 0 0 1px rgba(255,255,255,.55)!important;font-size:0!important;flex:0 0 34px!important}
.orange-svg-icon svg{width:21px;height:21px;display:block}
.orange-tool-item{gap:10px!important;padding:9px 10px!important;min-height:58px!important}
.orange-tool-item:hover .orange-svg-icon{background:#fff1d2!important;color:#d97706!important;border-color:#e9b949!important}
.orange-tool-item .orange-tool-copy{min-width:0}
.orange-tool-item .orange-tool-copy strong{font-size:13px!important;font-weight:700!important;line-height:1.2!important}
.orange-tool-item .orange-tool-copy small{font-size:11px!important;color:#9ca3af!important;margin-top:2px!important}
.orange-node-icon.orange-svg-icon{width:40px!important;height:40px!important;min-width:40px!important;border-radius:9px!important;background:#fff8e8!important;color:#a16207!important;border-color:#e8c66a!important}
.orange-node-icon.orange-svg-icon svg{width:23px;height:23px}
@media(max-width:900px){.orange-svg-icon{width:32px!important;height:32px!important;min-width:32px!important}.orange-node-icon.orange-svg-icon{width:36px!important;height:36px!important;min-width:36px!important}}
`;
document.head.appendChild(orangeIconStyle);
upgradeOrangeIcons();