(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let state = null;
  let currentView = 'studio';
  let filter = 'all';
  let busy = false;
  let split = 50;
  let toastTimer;
  const messages = {
    zh: {
      local:'本地运行',settings:'设置',preferences:'偏好设置',settingsTitle:'让工作台适合你',language:'界面语言',languageHelp:'选择界面文字',appearance:'外观',appearanceHelp:'适应不同的编辑环境',light:'浅色',dark:'深色',motion:'界面动效',motionHelp:'切换和悬停时的过渡',on:'开启',off:'关闭',libraryLocation:'LUT 库位置',libraryLocationHelp:'查看已导入的文件',settingsFoot:'设置保存在本机，重启后仍会生效。',minimize:'最小化',maximize:'最大化',close:'关闭',
      workspace:'工作空间',studio:'工作台',library:'LUT 资料库',history:'转换记录',recent:'最近使用',importFile:'导入 LUT 文件',localPrivacy:'文件与照片仅在本机处理',studioEyebrow:'色彩工作台',studioTitle:'让色彩，回到画面。',studioDescription:'载入一份 LUT，在照片中观察差异，然后转换为下一次创作所需的格式。',changePhoto:'更换预览照片',original:'← 原片',compareHelp:'拖动或使用方向键比较',applied:'应用 LUT →',builtInSix:'六款内置风格',filmInspiration:'胶片灵感',viewLibrary:'查看完整资料库',libraryEyebrow:'你的 LUT 资料库',libraryTitle:'收集你的色彩语言。',libraryDescription:'六款内置胶片风格，与自己导入的 LUT 放在同一处。点击即可在照片上预览。',importLut:'导入 LUT',searchPlaceholder:'搜索名称、格式…',all:'全部',builtIn:'内置',imported:'我的导入',historyEyebrow:'本次转换',historyTitle:'每一次转换，都有迹可循。',historyDescription:'这里展示本次运行期间实际写入的文件。',currentLut:'当前 LUT',conversion:'转换',sourceFormat:'源格式',targetFormat:'输出格式',outputGrid:'输出网格',xmpGroup:'XMP 分组',description:'描述',optional:'可选',descriptionPlaceholder:'记录这份风格的用途…',
      demoPhoto:'内置演示照片',originalPreview:'原片 / 预览',originalApplied:'原片 / {name}',emptyLut:'尚未选择 LUT',emptyLutHelp:'点击下方预设，或导入自己的文件开始。',grid:'{size}³ 网格',samples:'{count} 采样点',export:'导出 {format}',exportDisabled:'选择 LUT 后可导出',sizeEmpty:'选择 LUT 后可设置',sizeXmp:'最高 32³',sizeCube:'2–65³ 输入 · 16–65³ 输出',noteXmp:'XMP 输出最高 32³；更大网格会重采样。',noteCube:'CUBE 输出支持最高 65³ 网格。',previewAlt:'{name} 风格预览',preview:'预览',builtinTag:'内置',importedTag:'已导入',applyStudio:'应用到工作台 ↗',remove:'从库中移除',noLut:'没有找到 LUT',noLutHelp:'试试其他关键词，或导入自己的 CUBE / XMP 文件。',openFolder:'打开文件夹 ↗',noHistory:'还没有转换记录',noHistoryHelp:'选择 LUT 并导出后，结果会显示在这里。',connecting:'正在连接本地转换服务…',operationFailed:'本地操作失败',selectedToast:'已应用 LUT，可预览并转换。',importedToast:'已导入 {count} 份 LUT。',photoToast:'预览照片已更新。',exportToast:'已导出 {name} · {size}³',removedToast:'已从资料库移除。',settingsSaved:'设置已保存。',
      filmNotes:['柔和人像','克制纪实','复古负片','黑白层次','自然标准','鲜明风景']
    },
    en: {
      local:'On-device',settings:'Settings',preferences:'PREFERENCES',settingsTitle:'Make it yours',language:'Language',languageHelp:'Choose interface text',appearance:'Appearance',appearanceHelp:'Set the editing atmosphere',light:'Light',dark:'Dark',motion:'Motion',motionHelp:'Transitions and hover effects',on:'On',off:'Off',libraryLocation:'LUT library',libraryLocationHelp:'View imported files',settingsFoot:'Preferences are saved on this device.',minimize:'Minimize',maximize:'Maximize',close:'Close',
      workspace:'WORKSPACE',studio:'Studio',library:'LUT library',history:'Export history',recent:'RECENT',importFile:'Import LUT',localPrivacy:'Photos and files stay on this device',studioEyebrow:'COLOR STUDIO',studioTitle:'See color in context.',studioDescription:'Load a LUT, compare it on a photo, then convert it for your next project.',changePhoto:'Change preview photo',original:'← Original',compareHelp:'Drag or use arrow keys to compare',applied:'LUT applied →',builtInSix:'SIX BUILT-IN LOOKS',filmInspiration:'Film collection',viewLibrary:'View full library',libraryEyebrow:'YOUR LUT LIBRARY',libraryTitle:'Collect your color language.',libraryDescription:'Six built-in film looks and your imported LUTs, ready to preview on a photo.',importLut:'Import LUT',searchPlaceholder:'Search name or format…',all:'All',builtIn:'Built-in',imported:'Imported',historyEyebrow:'THIS SESSION',historyTitle:'Your conversions, in one place.',historyDescription:'Files exported during this session appear here.',currentLut:'CURRENT LUT',conversion:'CONVERT',sourceFormat:'Source',targetFormat:'Output',outputGrid:'Output grid',xmpGroup:'XMP group',description:'Description',optional:'Optional',descriptionPlaceholder:'Describe how you use this look…',
      demoPhoto:'Built-in sample photo',originalPreview:'Original / Preview',originalApplied:'Original / {name}',emptyLut:'No LUT selected',emptyLutHelp:'Choose a look below or import your own file.',grid:'{size}³ grid',samples:'{count} samples',export:'Export {format}',exportDisabled:'Select a LUT to export',sizeEmpty:'Select a LUT first',sizeXmp:'Up to 32³',sizeCube:'2–65³ input · 16–65³ output',noteXmp:'XMP output supports up to 32³. Larger grids are resampled.',noteCube:'CUBE output supports grids up to 65³.',previewAlt:'{name} look preview',preview:'Preview',builtinTag:'Built-in',importedTag:'Imported',applyStudio:'Apply in studio ↗',remove:'Remove from library',noLut:'No LUT found',noLutHelp:'Try another search or import a CUBE / XMP file.',openFolder:'Open folder ↗',noHistory:'No exports yet',noHistoryHelp:'Choose a LUT and export it to see the result here.',connecting:'Connecting to the local converter…',operationFailed:'Local operation failed',selectedToast:'LUT applied. Preview and convert when ready.',importedToast:'Imported {count} LUT(s).',photoToast:'Preview photo updated.',exportToast:'Exported {name} · {size}³',removedToast:'Removed from the library.',settingsSaved:'Settings saved.',
      filmNotes:['Soft portraits','Restrained documentary','Vintage negative','Monochrome depth','Natural color','Vivid landscapes']
    }
  };
  const language = () => state?.settings?.language === 'en' ? 'en' : 'zh';
  const tr = (key, values = {}) => String(messages[language()][key] ?? key).replace(/\{(\w+)\}/g, (_, name) => values[name] ?? '');
  function noteFor(item) {
    if (!item.builtin) return item.note || item.filename;
    const index = ['Astia','Classic Chrome','Classic Negative','Monochrome','Provia','Velvia'].indexOf(item.name);
    return messages[language()].filmNotes[index] || item.note;
  }
  function applySettings() {
    const settings = state?.settings || {language:'zh', theme:'light', motion:true};
    document.documentElement.lang = settings.language === 'en' ? 'en' : 'zh-CN';
    document.documentElement.dataset.theme = settings.theme;
    document.documentElement.dataset.motion = settings.motion ? 'on' : 'off';
    document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = tr(el.dataset.i18n); });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => { el.placeholder = tr(el.dataset.i18nPlaceholder); });
    document.querySelectorAll('[data-i18n-aria]').forEach(el => { el.setAttribute('aria-label', tr(el.dataset.i18nAria)); });
    $('settings-toggle').setAttribute('aria-label', tr('settings'));
    $('settings-toggle').title = tr('settings');
    $('settings-panel').setAttribute('aria-label', tr('settings'));
    $('settings-close').setAttribute('aria-label', tr('close'));
    $('compare').setAttribute('aria-label', language() === 'en' ? 'Compare original and LUT result' : '原片和 LUT 效果对比');
    document.querySelectorAll('.setting-options').forEach(group => group.querySelectorAll('button').forEach(button => {
      const selected = String(settings[group.dataset.setting]) === button.dataset.value;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    }));
  }
  function setSettingsOpen(open) {
    $('settings-panel').hidden = !open;
    $('settings-toggle').setAttribute('aria-expanded', String(open));
    $('settings-toggle').classList.toggle('active', open);
  }

  function toast(message, error = false) {
    const el = $('toast');
    el.textContent = message;
    el.classList.toggle('error', error);
    el.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('visible'), 3600);
  }
  async function call(method, ...args) {
    if (!window.pywebview?.api) { toast(tr('connecting'), true); return null; }
    if (busy) return null;
    busy = true;
    document.body.classList.add('working');
    try {
      const response = await window.pywebview.api[method](...args);
      if (!response?.ok) throw new Error(response?.error || tr('operationFailed'));
      return response.data;
    } catch (error) {
      toast(error.message || String(error), true);
      return null;
    } finally {
      busy = false;
      document.body.classList.remove('working');
    }
  }
  function setSplit(value) {
    split = Math.max(0, Math.min(100, value));
    $('processed-image').style.clipPath = `inset(0 0 0 ${split}%)`;
    $('divider').style.left = `${split}%`;
    $('compare').setAttribute('aria-valuenow', String(Math.round(split)));
  }
  function setView(view) {
    currentView = view;
    document.querySelectorAll('.view').forEach(el => el.classList.toggle('active', el.id === `${view}-view`));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.view === view));
    document.querySelector('.main-area').scrollTop = 0;
    if (view === 'library') renderLibrary();
    if (view === 'history') renderHistory();
  }
  function render(data) {
    if (!data) return;
    const previous = state?.selected;
    state = data;
    applySettings();
    $('library-count').textContent = String(data.items.length).padStart(2, '0');
    $('history-count').textContent = String(data.history.length).padStart(2, '0');
    $('photo-name').textContent = data.photoName === '内置演示照片' ? tr('demoPhoto') : data.photoName;
    $('original-image').src = data.original;
    $('processed-image').src = data.processed;
    $('compare-caption').textContent = data.document ? tr('originalApplied', {name:data.document.displayName}) : tr('originalPreview');
    $('selected-card').innerHTML = data.document ?
      `<p class="selected-type">${escapeHtml(data.document.source)} · 3D LUT</p><h3>${escapeHtml(data.document.displayName)}</h3><p>${escapeHtml(data.document.filename)}</p><div class="selected-meta"><span>${tr('grid',{size:data.document.size})}</span><span>${tr('samples',{count:(data.document.size ** 3).toLocaleString()})}</span></div>` :
      `<div class="empty-orb">◈</div><h3>${tr('emptyLut')}</h3><p>${tr('emptyLutHelp')}</p>`;
    $('source-format').textContent = data.document?.source || '—';
    $('target-format').textContent = data.document?.target || '—';
    $('export').disabled = !data.document;
    $('export').firstElementChild.textContent = data.document ? tr('export',{format:data.document.target}) : tr('exportDisabled');
    $('xmp-options').hidden = data.document?.target !== 'XMP';
    $('size-hint').textContent = !data.document ? tr('sizeEmpty') : data.document.target === 'XMP' ? tr('sizeXmp') : tr('sizeCube');
    $('conversion-note').textContent = data.document?.target === 'XMP' ?
      tr('noteXmp') : tr('noteCube');
    if (data.selected !== previous && data.document) {
      const values = [...$('output-size').options].map(o => Number(o.value));
      $('output-size').value = String(values.includes(data.document.size) ? data.document.size : 16);
    }
    renderRecent(); renderFilm();
    if (currentView === 'library') renderLibrary();
    if (currentView === 'history') renderHistory();
    setSplit(split);
  }
  function renderRecent() {
    const items = state.items.filter(item => item.id === state.selected || !item.builtin).slice(0, 5);
    const shown = items.length ? items : state.items.slice(0, 5);
    $('recent-list').innerHTML = shown.map(item => `<button class="recent-item ${item.id === state.selected ? 'active' : ''}" data-select="${escapeHtml(item.id)}"><span class="recent-swatch"></span><span>${escapeHtml(item.name)}</span></button>`).join('');
  }
  function renderFilm() {
    $('film-strip').innerHTML = state.items.filter(item => item.builtin).map(item =>
      `<button class="film-card ${item.id === state.selected ? 'active' : ''}" data-select="${escapeHtml(item.id)}"><img src="${item.thumbnail}" alt="${escapeHtml(tr('previewAlt',{name:item.name}))}"><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(noteFor(item))}</small></button>`).join('');
  }
  function renderLibrary() {
    const term = $('library-search').value.trim().toLowerCase();
    const items = state.items.filter(item => (filter === 'all' || (filter === 'builtin') === item.builtin)
      && `${item.name} ${item.source} ${item.filename}`.toLowerCase().includes(term));
    $('library-grid').innerHTML = items.length ? items.map(item =>
      `<article class="library-tile ${item.id === state.selected ? 'active' : ''}"><button class="tile-preview" data-select="${escapeHtml(item.id)}" aria-label="${escapeHtml(tr('previewAlt',{name:item.name}))}"><img class="tile-art" src="${item.thumbnail || state.original}" alt="" decoding="async"></button><div class="tile-details"><div class="tile-top"><strong title="${escapeHtml(item.name)}">${escapeHtml(item.name)}</strong><small>${tr(item.builtin ? 'builtinTag' : 'importedTag')}</small></div><p>${escapeHtml(item.source)} · ${item.size}³ · ${escapeHtml(noteFor(item))}</p><div class="tile-actions"><button data-select="${escapeHtml(item.id)}">${tr('applyStudio')}</button>${item.builtin ? '' : `<button class="remove" data-remove="${escapeHtml(item.id)}">${tr('remove')}</button>`}</div></div></article>`).join('') :
      `<div class="empty-state"><strong>${tr('noLut')}</strong>${tr('noLutHelp')}</div>`;
  }
  function renderHistory() {
    $('history-list').innerHTML = state.history.length ? state.history.map((item, index) =>
      `<div class="history-row"><div><strong>${escapeHtml(item.filename)}</strong><small>${escapeHtml(item.path)}</small></div><span class="format-value">${escapeHtml(item.source)} → ${escapeHtml(item.target)}</span><span>${item.size}³ · ${escapeHtml(item.createdAt)}</span><button data-folder="${index}">${tr('openFolder')}</button></div>`).join('') :
      `<div class="empty-state"><strong>${tr('noHistory')}</strong>${tr('noHistoryHelp')}</div>`;
  }
  async function chooseItem(id) {
    const data = await call('select', id);
    if (data) { render(data); setView('studio'); toast(tr('selectedToast')); }
  }
  async function importLuts() {
    const count = state?.items.length || 0;
    const data = await call('import_luts');
    if (data) { render(data); if (data.items.length > count) { setView('studio'); toast(tr('importedToast',{count:data.items.length-count})); } }
  }
  async function changePhoto() {
    const name = state?.photoName;
    const data = await call('choose_photo');
    if (data) { render(data); if (data.photoName !== name) toast(tr('photoToast')); }
  }
  async function exportLut() {
    if (!state?.document) return;
    const size = Number($('output-size').value);
    const result = await call('export', size, $('group').value, $('description').value);
    if (!result || result.cancelled) return;
    const updated = await call('state');
    if (updated) render(updated);
    toast(tr('exportToast',{name:result.filename,size:result.size}));
  }
  $('settings-toggle').onclick = () => setSettingsOpen($('settings-panel').hidden);
  $('settings-close').onclick = () => { setSettingsOpen(false); $('settings-toggle').focus(); };
  $('open-library-folder').onclick = () => call('open_library_folder');
  document.querySelectorAll('.setting-options button').forEach(button => button.onclick = async () => {
    if (!state) return;
    const key = button.parentElement.dataset.setting;
    const value = key === 'motion' ? button.dataset.value === 'true' : button.dataset.value;
    if (state.settings[key] === value) return;
    const updated = await call('update_settings', {[key]:value});
    if (updated) { state.settings = updated; render(state); toast(tr('settingsSaved')); }
  });
  document.addEventListener('click', async event => {
    if (!$('settings-panel').hidden && !event.target.closest('.settings-wrap')) setSettingsOpen(false);
    const action = event.target.closest('[data-select],[data-remove],[data-folder],[data-view],[data-window]');
    if (!action) return;
    if (action.dataset.view) setView(action.dataset.view);
    if (action.dataset.select) chooseItem(action.dataset.select);
    if (action.dataset.remove) {
      const data = await call('remove', action.dataset.remove);
      if (data) { render(data); toast(tr('removedToast')); }
    }
    if (action.dataset.folder) {
      const row = state.history[Number(action.dataset.folder)];
      if (row) call('open_folder', row.path);
    }
    if (action.dataset.window) {
      if (action.dataset.window === 'maximize') {
        const maximized = document.body.classList.toggle('maximized');
        call('window_action', maximized ? 'maximize' : 'restore');
      } else call('window_action', action.dataset.window);
    }
  });
  $('import-side').onclick = $('import-main').onclick = importLuts;
  $('import-hero').onclick = importLuts;
  $('change-photo').onclick = changePhoto;
  $('open-library').onclick = () => setView('library');
  $('export').onclick = exportLut;
  $('library-search').oninput = () => state && renderLibrary();
  document.querySelectorAll('[data-filter]').forEach(button => button.onclick = () => {
    filter = button.dataset.filter;
    document.querySelectorAll('[data-filter]').forEach(other => other.classList.toggle('active', other === button));
    if (state) renderLibrary();
  });
  const compare = $('compare');
  function point(event) { const box = compare.getBoundingClientRect(); setSplit((event.clientX - box.left) / box.width * 100); }
  compare.addEventListener('pointerdown', event => { compare.setPointerCapture(event.pointerId); point(event); compare.focus(); });
  compare.addEventListener('pointermove', event => { if (compare.hasPointerCapture(event.pointerId)) point(event); });
  compare.addEventListener('keydown', event => {
    const delta = event.key === 'ArrowLeft' ? -5 : event.key === 'ArrowRight' ? 5 : null;
    if (delta !== null) { setSplit(split + delta); event.preventDefault(); }
    if (event.key === 'Home') { setSplit(0); event.preventDefault(); }
    if (event.key === 'End') { setSplit(100); event.preventDefault(); }
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !$('settings-panel').hidden) { setSettingsOpen(false); $('settings-toggle').focus(); return; }
    if (!(event.ctrlKey || event.metaKey) || ['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) return;
    if (event.key.toLowerCase() === 'o') { event.preventDefault(); importLuts(); }
    if (event.key.toLowerCase() === 'p') { event.preventDefault(); changePhoto(); }
    if (event.key.toLowerCase() === 's') { event.preventDefault(); exportLut(); }
  });
  async function initialize() {
    try { const data = await call('state'); if (data) render(data); }
    finally { document.body.classList.add('app-ready'); }
  }
  if (window.pywebview?.api) initialize(); else window.addEventListener('pywebviewready', initialize, {once:true});
})();
