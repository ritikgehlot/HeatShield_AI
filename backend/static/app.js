const state = { wards: [], selectedWard: null, summary: null };
const $ = (selector) => document.querySelector(selector);

function formatRisk(score) { return `${Number(score).toFixed(1)}/100`; }
function levelClass(level) { return String(level || '').toLowerCase(); }
function formatDate(value) { return new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }); }

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Something went wrong.');
  }
  return response.json();
}

function renderMetrics(summary) {
  $('#cityName').textContent = `${summary.city}, Rajasthan`;
  $('#avgLst').textContent = `${summary.average_lst_c}°C`;
  $('#highRisk').textContent = summary.high_risk_wards;
  $('#avgNdvi').textContent = summary.green_cover_average;
  $('#avgRisk').textContent = `${summary.average_risk_score}/100`;
  $('#updatedAt').textContent = 'Live prototype session';
}

function renderMap() {
  const markerHost = $('#wardMarkers');
  markerHost.innerHTML = '';
  state.wards.forEach((ward) => {
    const marker = document.createElement('button');
    marker.type = 'button';
    marker.className = `ward-marker ${levelClass(ward.risk_level)} ${ward.id === state.selectedWard?.id ? 'selected' : ''}`;
    marker.style.left = `${ward.map_x}%`;
    marker.style.top = `${ward.map_y}%`;
    marker.setAttribute('aria-label', `${ward.name}, risk ${formatRisk(ward.risk_score)}`);
    marker.innerHTML = `<b>${Math.round(ward.risk_score)}</b><span class="ward-tooltip"><strong>${ward.name}</strong> · ${formatRisk(ward.risk_score)}<br>${ward.risk_level} risk</span>`;
    marker.addEventListener('click', () => selectWard(ward.id));
    markerHost.appendChild(marker);
  });
}

function renderWard(ward) {
  $('#wardName').textContent = ward.name;
  $('#wardScore').textContent = formatRisk(ward.risk_score);
  $('#scenarioWard').textContent = ward.name;
  $('#wardLst').textContent = `${ward.lst_c.toFixed(1)}°C`;
  $('#wardNdvi').textContent = ward.ndvi.toFixed(2);
  $('#wardBuilt').textContent = `${ward.built_up_pct.toFixed(0)}%`;
  $('#wardVulnerability').textContent = ward.vulnerability_index.toFixed(2);
  const pill = $('#riskPill');
  pill.textContent = `${ward.risk_level} risk`;
  pill.className = `risk-pill ${levelClass(ward.risk_level)}`;
  const circle = $('#scoreCircle');
  circle.style.background = `conic-gradient(${riskColor(ward.risk_level)} ${Math.round(ward.risk_score * 3.6)}deg, #e9edf3 0deg)`;
  $('#scoreCircleText').textContent = Math.round(ward.risk_score);
  $('#driverList').innerHTML = ward.top_drivers.map((driver) => `<li>${escapeHtml(driver)}</li>`).join('');
  $('#recommendationList').innerHTML = ward.recommendation.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  $('#baselineScore').textContent = formatRisk(ward.risk_score);
  $('#baselineLevel').textContent = `${ward.risk_level} risk`;
  $('#baselineLevel').style.color = riskColor(ward.risk_level);
  $('#projectedScore').textContent = '—';
  $('#projectedLevel').textContent = 'Run simulation';
  $('#riskReduction').textContent = '—';
  $('#projectedLst').textContent = '—';
  $('#impactList').innerHTML = '<li>Run the simulation to generate an intervention package.</li>';
  $('#actionBrief').textContent = 'Choose intervention coverage and run the simulator to receive a concise implementation plan.';
}

function riskColor(level) {
  const colors = { Low: '#22a85a', Medium: '#d79500', High: '#f97316', Extreme: '#ef4444' };
  return colors[level] || '#687689';
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
}

function selectWard(id) {
  const ward = state.wards.find((item) => item.id === id);
  if (!ward) return;
  state.selectedWard = ward;
  renderMap();
  renderWard(ward);
}

function bindRange(input, output, suffix = '') {
  const update = () => { output.textContent = `${input.value}${suffix}`; };
  input.addEventListener('input', update);
  update();
}

async function runSimulation() {
  if (!state.selectedWard) return;
  const button = $('#runSimulation');
  button.disabled = true;
  button.textContent = 'Calculating impact...';
  $('#calcStatus').textContent = 'Calculating';
  try {
    const payload = {
      ward_id: state.selectedWard.id,
      cool_roof_coverage: Number($('#coolRoof').value),
      tree_cover_gain: Number($('#treeCover').value),
      shade_units: Number($('#shadeUnits').value),
      budget_lakh: Number($('#budget').value),
    };
    const result = await api('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    $('#baselineScore').textContent = formatRisk(result.baseline_score);
    $('#baselineLevel').textContent = `Baseline`;
    $('#projectedScore').textContent = formatRisk(result.projected_score);
    $('#projectedLevel').textContent = `${result.risk_level} risk`;
    $('#projectedLevel').style.color = riskColor(result.risk_level);
    $('#riskReduction').textContent = `−${result.risk_reduction} points`;
    $('#projectedLst').textContent = `${result.projected_lst_c}°C`;
    $('#impactList').innerHTML = result.intervention_summary.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
    $('#actionBrief').textContent = result.action_brief;
    $('#modelNote').textContent = result.model_note;
    $('#calcStatus').textContent = 'Scenario complete';
  } catch (error) {
    $('#calcStatus').textContent = 'Could not calculate';
    $('#actionBrief').textContent = error.message;
  } finally {
    button.disabled = false;
    button.innerHTML = 'Run impact simulation <span>↻</span>';
  }
}

async function uploadCsv() {
  const file = $('#csvUpload').files[0];
  const message = $('#uploadMessage');
  if (!file) { message.textContent = 'Choose a CSV file first.'; return; }
  const form = new FormData();
  form.append('file', file);
  message.textContent = 'Importing and recomputing risk scores...';
  try {
    const result = await api('/api/data/upload', { method: 'POST', body: form });
    message.textContent = `${result.message} Imported: ${result.imported}, updated: ${result.updated}, skipped: ${result.skipped}.`;
    await loadDashboard();
  } catch (error) {
    message.textContent = error.message;
  }
}

async function loadDashboard() {
  const [summary, wards] = await Promise.all([api('/api/summary'), api('/api/wards')]);
  state.summary = summary;
  state.wards = wards;
  renderMetrics(summary);
  selectWard(state.selectedWard?.id && wards.some((ward) => ward.id === state.selectedWard.id) ? state.selectedWard.id : wards[0].id);
}

function initialiseEvents() {
  bindRange($('#coolRoof'), $('#roofValue'), '%');
  bindRange($('#treeCover'), $('#treeValue'), '%');
  bindRange($('#shadeUnits'), $('#shadeValue'));
  bindRange($('#budget'), $('#budgetValue'), 'L');
  $('#runSimulation').addEventListener('click', runSimulation);
  $('#jumpToSimulator').addEventListener('click', () => $('#simulator').scrollIntoView({ behavior: 'smooth' }));
  $('#downloadTemplate').addEventListener('click', () => { window.location.href = '/api/data/template'; });
  $('#uploadButton').addEventListener('click', uploadCsv);
}

(async function boot() {
  initialiseEvents();
  try {
    await loadDashboard();
  } catch (error) {
    document.body.innerHTML = `<div style="padding:40px;font-family:Arial;color:#122137"><h1>HeatShield AI could not start</h1><p>${escapeHtml(error.message)}</p><p>Check that the FastAPI server is running and reload the page.</p></div>`;
  }
})();
