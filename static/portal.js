document.addEventListener('DOMContentLoaded',()=>{
 const scrollKey='sefel-view-scroll';
 const saved=sessionStorage.getItem(scrollKey);
 if(saved){
  try{const state=JSON.parse(saved);const here=location.pathname+location.search;if(state.to===here&&Date.now()-state.time<30000){requestAnimationFrame(()=>window.scrollTo(0,state.y))}sessionStorage.removeItem(scrollKey)}catch{sessionStorage.removeItem(scrollKey)}
 }
 document.querySelectorAll('.filters a,.admin-menu a,.page-head + .section .grid a.card').forEach(link=>link.addEventListener('click',()=>{
  const target=new URL(link.href,location.href);sessionStorage.setItem(scrollKey,JSON.stringify({to:target.pathname+target.search,y:window.scrollY,time:Date.now()}));
 }));
 const type=document.querySelector('#type'), company=document.querySelector('.company-only');
 if(type&&company){const toggle=()=>{const show=type.value==='company';company.classList.toggle('hidden',!show);company.querySelector('input').required=show};type.addEventListener('change',toggle);toggle()}
 const filePicker=document.querySelector('[data-file-picker]'),fileList=document.querySelector('[data-file-list]'),fileError=document.querySelector('[data-file-error]'),fileSummary=document.querySelector('[data-file-summary]');
 if(filePicker&&fileList){
  let selectedFiles=[];
  const syncInput=()=>{const transfer=new DataTransfer();selectedFiles.forEach(file=>transfer.items.add(file));filePicker.files=transfer.files};
  const renderFiles=()=>{
   syncInput();fileList.replaceChildren();
   selectedFiles.forEach((file,index)=>{
    const row=document.createElement('li'),name=document.createElement('span'),remove=document.createElement('button');
    name.textContent=`${file.name} · ${(file.size/1024/1024).toFixed(2)} MB`;remove.type='button';remove.textContent='Quitar';remove.setAttribute('aria-label',`Quitar ${file.name}`);remove.addEventListener('click',()=>{selectedFiles=selectedFiles.filter((item,itemIndex)=>itemIndex!==index);fileError.textContent='';renderFiles()});row.append(name,remove);fileList.append(row)
   });
   fileList.hidden=selectedFiles.length===0;
   if(fileSummary)fileSummary.textContent=`${selectedFiles.length} de 5 archivos seleccionados`;
  };
  filePicker.addEventListener('change',()=>{
   fileError.textContent='';
   const incoming=[...filePicker.files];
   incoming.forEach(file=>{
    if(selectedFiles.length>=5){fileError.textContent='Puedes adjuntar hasta 5 archivos. Quita uno para agregar otro.';return}
    if(file.size>10*1024*1024){fileError.textContent=`${file.name} supera el límite de 10 MB y no se agregó.`;return}
    selectedFiles.push(file)
   });
   renderFiles()
  });
 }
 document.querySelectorAll('[data-carousel]').forEach(carousel=>{const slides=[...carousel.querySelectorAll('.slide')];if(slides.length<2)return;let i=0,busy=false;const show=n=>{if(busy)return;busy=true;carousel.classList.add('is-changing');window.setTimeout(()=>{slides[i].classList.remove('active');i=(n+slides.length)%slides.length;slides[i].classList.add('active');const t=carousel.querySelector('[data-indicator]');if(t)t.textContent=`${String(i+1).padStart(2,'0')} / ${String(slides.length).padStart(2,'0')}`;carousel.classList.remove('is-changing');busy=false},200)};carousel.querySelector('[data-next]')?.addEventListener('click',()=>show(i+1));carousel.querySelector('[data-prev]')?.addEventListener('click',()=>show(i-1));setInterval(()=>show(i+1),5000)})
 document.querySelectorAll('.messages .msg').forEach(m=>{if(m.textContent.includes('error'))m.classList.add('error')});
});
