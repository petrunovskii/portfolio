'use strict';
(()=>{
  const data=JSON.parse(document.getElementById('site-data').textContent);
  const params=new URLSearchParams(location.search);
  const legacy=new URLSearchParams(location.hash.slice(1));
  if(legacy.get('lang')==='ru' && document.documentElement.lang!=='ru'){
    const target=new URL(document.querySelector('.languages a[lang="ru"]').href);
    if(legacy.get('role'))target.searchParams.set('role',legacy.get('role'));
    location.replace(target.href);
    return;
  }
  let role=params.get('role')||legacy.get('role')||'all';
  if(!data.roles[role])role='all';
  const cards=[...document.querySelectorAll('.case')];
  function render(next,update=true){
    role=next;
    const selection=data.roles[role];
    document.getElementById('role').textContent=selection.title;
    document.getElementById('lead').textContent=selection.lead;
    document.getElementById('cv').href=data.prefix+data.cv[role];
    const order=data.order[role];
    for(const card of cards)card.hidden=!order.includes(card.id);
    const box=document.getElementById('cases');
    for(const id of order)box.append(document.getElementById(id));
    document.getElementById('case-count').textContent=order.length;
    document.querySelectorAll('[data-role]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.role===role)));
    document.querySelectorAll('.languages a').forEach(a=>{const u=new URL(a.href);if(role!=='all')u.searchParams.set('role',role);else u.searchParams.delete('role');a.href=u.href;});
    document.querySelectorAll('.case-link').forEach(a=>{const u=new URL(location.href);u.search=role==='all'?'':'?role='+role;u.hash=a.closest('.case').id;a.href=u.href;});
    if(update){const u=new URL(location.href);u.search=role==='all'?'':'?role='+role;history.replaceState(null,'',u);}
  }
  document.getElementById('filter').addEventListener('click',event=>{const button=event.target.closest('[data-role]');if(button)render(button.dataset.role);});
  function openLinkedCase(){const id=decodeURIComponent(location.hash.slice(1));const card=cards.find(c=>c.id===id);if(card){if(card.hidden)render('all');card.querySelector('details').open=true;card.scrollIntoView();}}
  addEventListener('hashchange',openLinkedCase);
  render(role,false);
  openLinkedCase();
})();
