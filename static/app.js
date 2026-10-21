const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const state = { goal: '种草', platforms: ['小红书', '抖音'], results: {}, activePlatform: '小红书', version: 0, versions: [], viewingVersion: -1, optimization: null, providers: {} };
const providerNames = { gpt: 'GPT', deepseek: 'DeepSeek', doubao: '豆包' };
const trialCase = { productName: 'Luma 智能运动手环', sellingPoints: '14 天超长续航\n全天候健康监测\n100+ 运动模式\n轻薄无感设计', audience: '20–30 岁注重健康的城市职场人' };
const loadingMessages = ['正在分析产品卖点...', '正在匹配目标用户...', '正在适配平台内容策略...', '正在生成平台内容...'];

function getPayload() {
  return {
    productName: $('#productName').value.trim(), sellingPoints: $('#sellingPoints').value.trim(),
    audience: $('#audience').value.trim(), goal: state.goal, platforms: state.platforms, provider: $('#modelProvider').value,
    version: state.version + 1, optimization: state.optimization,
  };
}

function updateCount() { $('#select-count').textContent = `已选 ${state.platforms.length} 个`; }
function showToast(message) { const toast = $('#toast'); toast.textContent = message; toast.classList.add('show'); setTimeout(() => toast.classList.remove('show'), 2100); }
function syncProviderUi() {
  const selected = $('#modelProvider').value; const current = state.providers[selected];
  $('#model-note').textContent = current?.message || '模型状态暂时无法读取';
  $$('#modelProvider option').forEach(option => {
    const provider = state.providers[option.value];
    if (!provider) return;
    const suffix = provider.state === 'configured' ? '' : provider.state === 'demo' ? ' · 演示' : ' · 未配置';
    option.textContent = `${provider.label}${suffix}`;
  });
}
async function loadProviders() {
  try { const response = await fetch('/api/providers'); const data = await response.json(); data.providers.forEach(provider => { state.providers[provider.id] = provider; }); syncProviderUi(); }
  catch { $('#model-note').textContent = '模型状态暂时无法读取'; }
}
function clearValidation() { $('#form-error').classList.add('hidden'); $$('.input-invalid').forEach(item => item.classList.remove('input-invalid')); }
function showValidation(message, fields = []) { $('#form-error').textContent = message; $('#form-error').classList.remove('hidden'); fields.forEach(id => $(`#${id}`)?.classList.add('input-invalid')); }
function validateBrief(payload) {
  clearValidation();
  const missing = [['productName', '产品名称'], ['sellingPoints', '核心卖点'], ['audience', '目标人群']].filter(([id]) => !payload[id]);
  if (missing.length) { showValidation(`请补充${missing.map(([, name]) => `「${name}」`).join('、')}后再生成。`, missing.map(([id]) => id)); return false; }
  if (payload.productName.length > 60 || payload.audience.length > 100 || payload.sellingPoints.length > 800) { showValidation('产品信息过长，请精简后再生成（产品名称 60 字、目标人群 100 字、核心卖点 800 字以内）。'); return false; }
  if (!payload.platforms.length) { showValidation('请至少选择一个发布平台。'); return false; }
  return true;
}
function setLoading(loading) {
  $('#empty-state').classList.toggle('hidden', loading || state.version > 0);
  $('#result-state').classList.toggle('hidden', loading || state.version === 0);
  $('#loading-state').classList.toggle('hidden', !loading);
  $('#generate-button').classList.toggle('is-loading', loading);
  $('#generate-button').disabled = loading;
}
function bodyToHtml(value) { return value.split('\n').map(line => line.startsWith('## ') ? `<h4>${escapeHtml(line.slice(3))}</h4>` : `<p>${escapeHtml(line) || '&nbsp;'}</p>`).join(''); }
function escapeHtml(value) { return value.replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char])); }
function selectedResult() { return state.results[state.activePlatform]; }

function renderTabs() {
  $('#tabs').innerHTML = state.platforms.map(platform => `<button class="tab ${platform === state.activePlatform ? 'active' : ''}" data-tab="${platform}">${platform}<span>${state.results[platform]?.scores.platform || ''}</span></button>`).join('');
  $$('#tabs button').forEach(button => button.addEventListener('click', () => { state.activePlatform = button.dataset.tab; renderResult(); }));
}
function renderVersions() {
  $('#version-list').innerHTML = state.versions.map((_, index) => `<button class="version-button ${index === state.viewingVersion ? 'active' : ''}" data-version="${index}">V${index + 1}</button>`).join('');
  $$('#version-list button').forEach(button => button.addEventListener('click', () => {
    state.viewingVersion = Number(button.dataset.version);
    const archived = state.versions[state.viewingVersion]; state.results = structuredClone(archived.results); state.activePlatform = archived.activePlatform; renderResult();
  }));
}
function renderResult() {
  const result = selectedResult(); if (!result) return;
  renderTabs();
  $('#content-platform').textContent = state.activePlatform;
  $('#content-subtitle').textContent = result.subtitle;
  $('#version-tag').textContent = `V${result.version}`;
  $('#content-title').textContent = result.title;
  $('#content-body').innerHTML = bodyToHtml(result.body);
  $('#hashtags').innerHTML = result.hashtags.map(tag => `<span>${tag}</span>`).join('');
  $('#insight-text').textContent = result.insight;
  const labels = [['platform', '平台适配度'], ['selling_point', '卖点表达度'], ['appeal', '用户吸引力'], ['naturalness', '自然度']];
  $('#scores').innerHTML = labels.map(([key, label]) => `<div class="score"><div><span>${label}</span><b>${result.scores[key]}</b></div><div class="progress"><i style="width:${result.scores[key]}%"></i></div></div>`).join('');
  renderVersions();
}

async function generate({ optimization = null, keepOptimization = false } = {}) {
  const payload = getPayload(); payload.optimization = optimization; state.optimization = keepOptimization ? optimization : null;
  if (!validateBrief(payload)) return;
  const provider = state.providers[payload.provider];
  if (provider && !provider.configured && payload.provider !== 'gpt') { showValidation(`${provider.label} 未配置 API，未发送生成请求。请切换到 GPT 演示生成器，或配置该 Provider。`); return; }
  const previousPlatform = state.activePlatform;
  setLoading(true); let index = 0;
  const timer = setInterval(() => { index = (index + 1) % loadingMessages.length; $('#loading-copy').textContent = loadingMessages[index]; }, 650);
  try {
    const response = await fetch('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const data = await response.json(); if (!response.ok) throw new Error(data.error || '生成失败，请再试一次');
    state.version += 1; state.results = data.results; state.activePlatform = state.platforms.includes(previousPlatform) ? previousPlatform : state.platforms[0];
    state.versions.push({ results: structuredClone(data.results), activePlatform: state.activePlatform });
    state.viewingVersion = state.versions.length - 1;
    $('.output-mode').innerHTML = `<span></span>${providerNames[payload.provider]} · ${data.source === 'llm' ? 'LIVE API' : 'DEMO GENERATOR'}`;
    renderResult(); setLoading(false);
  } catch (error) { setLoading(false); showToast(error.message); }
  finally { clearInterval(timer); state.optimization = null; }
}

$$('.goal').forEach(button => button.addEventListener('click', () => { $$('.goal').forEach(item => item.classList.remove('selected')); button.classList.add('selected'); state.goal = button.dataset.goal; }));
$$('.platform').forEach(button => button.addEventListener('click', () => {
  const platform = button.dataset.platform; const exists = state.platforms.includes(platform);
  if (exists && state.platforms.length === 1) { showToast('至少保留一个发布平台'); return; }
  state.platforms = exists ? state.platforms.filter(item => item !== platform) : [...state.platforms, platform]; button.classList.toggle('selected', !exists); updateCount();
}));
$('#try-case-button').addEventListener('click', () => {
  Object.entries(trialCase).forEach(([id, value]) => { $(`#${id}`).value = value; });
  state.goal = '种草'; $$('.goal').forEach(item => item.classList.toggle('selected', item.dataset.goal === state.goal));
  state.platforms = ['小红书', '抖音', '微博', '公众号', '朋友圈'];
  $$('.platform').forEach(item => item.classList.add('selected')); updateCount(); clearValidation();
  showToast('已填入试用案例：可直接生成 5 平台内容');
});
$('#modelProvider').addEventListener('change', syncProviderUi);
$$('#productName, #sellingPoints, #audience').forEach(input => input.addEventListener('input', () => { input.classList.remove('input-invalid'); if ($$('.input-invalid').length === 0) $('#form-error').classList.add('hidden'); }));
$('#generator-form').addEventListener('submit', event => { event.preventDefault(); generate(); });
$('#regenerate-button').addEventListener('click', () => generate());
$('#copy-button').addEventListener('click', async () => { const item = selectedResult(); const text = [item.title, item.body, item.hashtags.join(' ')].filter(Boolean).join('\n\n'); try { await navigator.clipboard.writeText(text); showToast('文案已复制到剪贴板'); } catch { showToast('复制失败，请手动选择文案'); } });
$('#optimise-chips').addEventListener('click', event => { const button = event.target.closest('button'); if (!button) return; $$('#optimise-chips button').forEach(item => item.classList.remove('active')); button.classList.add('active'); generate({ optimization: button.dataset.optimization, keepOptimization: true }); });
document.addEventListener('keydown', event => { if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') { event.preventDefault(); $('#generator-form').requestSubmit(); } });
loadProviders();
