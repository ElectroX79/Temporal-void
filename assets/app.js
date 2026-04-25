// SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

// Configuración de gráficos
const temperatureLive = { canvas: null, chart: null, data: newChartData('orange', 'rgba(255,165,0,0.1)'), unit: '°C' };
const humidityLive = { canvas: null, chart: null, data: newChartData('teal', 'rgba(0,128,128,0.08)'), unit: '%' };
const lightLive = { canvas: null, chart: null, data: newChartData('gold', 'rgba(255,215,0,0.1)'), unit: 'lx' };

const temperature1h = { canvas: null, chart: null, data: newChartData('orange', 'rgba(255,165,0,0.1)'), unit: '°C' };
const humidity1h = { canvas: null, chart: null, data: newChartData('teal', 'rgba(0,128,128,0.08)'), unit: '%' };
const light1h = { canvas: null, chart: null, data: newChartData('gold', 'rgba(255,215,0,0.1)'), unit: 'lx' };

const temperature1d = { canvas: null, chart: null, data: newChartData('orange', 'rgba(255,165,0,0.1)'), unit: '°C' };
const humidity1d = { canvas: null, chart: null, data: newChartData('teal', 'rgba(0,128,128,0.08)'), unit: '%' };
const light1d = { canvas: null, chart: null, data: newChartData('gold', 'rgba(255,215,0,0.1)'), unit: 'lx' };

// Métricas derivadas
const dewPointLive = { canvas: null, chart: null, data: newChartData('blue', 'rgba(0,0,255,0.08)'), unit: '°C' };
const heatIndexLive = { canvas: null, chart: null, data: newChartData('red', 'rgba(255,0,0,0.08)'), unit: '°C' };
const absHumidityLive = { canvas: null, chart: null, data: newChartData('purple', 'rgba(128,0,128,0.06)'), unit: 'g/m³' };

const dewPoint1h = { canvas: null, chart: null, data: newChartData('blue', 'rgba(0,0,255,0.08)'), unit: '°C' };
const heatIndex1h = { canvas: null, chart: null, data: newChartData('red', 'rgba(255,0,0,0.08)'), unit: '°C' };
const absHumidity1h = { canvas: null, chart: null, data: newChartData('purple', 'rgba(128,0,128,0.06)'), unit: 'g/m³' };

const dewPoint1d = { canvas: null, chart: null, data: newChartData('blue', 'rgba(0,0,255,0.08)'), unit: '°C' };
const heatIndex1d = { canvas: null, chart: null, data: newChartData('red', 'rgba(255,0,0,0.08)'), unit: '°C' };
const absHumidity1d = { canvas: null, chart: null, data: newChartData('purple', 'rgba(128,0,128,0.06)'), unit: 'g/m³' };

let liveCircleTimeout = null;
const noDataTimeout = 10000;
let errorContainer;

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar Canvases
    temperatureLive.canvas = document.getElementById('temperature-live-chart');
    humidityLive.canvas = document.getElementById('humidity-live-chart');
    lightLive.canvas = document.getElementById('light-live-chart');

    temperature1h.canvas = document.getElementById('temperature-1h-chart');
    humidity1h.canvas = document.getElementById('humidity-1h-chart');
    light1h.canvas = document.getElementById('light-1h-chart');

    temperature1d.canvas = document.getElementById('temperature-1d-chart');
    humidity1d.canvas = document.getElementById('humidity-1d-chart');
    light1d.canvas = document.getElementById('light-1d-chart');

    // Canvases derivadas
    dewPointLive.canvas = document.getElementById('dew_point-live-chart');
    heatIndexLive.canvas = document.getElementById('heat_index-live-chart');
    absHumidityLive.canvas = document.getElementById('absolute_humidity-live-chart');
    dewPoint1h.canvas = document.getElementById('dew_point-1h-chart');
    heatIndex1h.canvas = document.getElementById('heat_index-1h-chart');
    absHumidity1h.canvas = document.getElementById('absolute_humidity-1h-chart');
    dewPoint1d.canvas = document.getElementById('dew_point-1d-chart');
    heatIndex1d.canvas = document.getElementById('heat_index-1d-chart');
    absHumidity1d.canvas = document.getElementById('absolute_humidity-1d-chart');

    errorContainer = document.getElementById('error-container');

    // Tab switching
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(this.dataset.tab).classList.add('active');
        });
    });

    // Carga histórica 1h
    document.querySelector('.tab[data-tab="historical-1h"]').addEventListener('click', async () => {
        renderChartData(temperature1h, await listSamples("temperature", "-1h", "5m"), 12, true, false);
        renderChartData(humidity1h, await listSamples("humidity", "-1h", "5m"), 12, true, false);
        renderChartData(light1h, await listSamples("light", "-1h", "5m"), 12, true, false);
        renderChartData(dewPoint1h, await listSamples("dew_point", "-1h", "5m"), 12, true, false);
        renderChartData(heatIndex1h, await listSamples("heat_index", "-1h", "5m"), 12, true, false);
        renderChartData(absHumidity1h, await listSamples("absolute_humidity", "-1h", "5m"), 12, true, false);
    });

    // Carga histórica 1d
    document.querySelector('.tab[data-tab="historical-1d"]').addEventListener('click', async () => {
        renderChartData(temperature1d, await listSamples("temperature", "-1d", "1h"), 24, false, false);
        renderChartData(humidity1d, await listSamples("humidity", "-1d", "1h"), 24, false, false);
        renderChartData(light1d, await listSamples("light", "-1d", "1h"), 24, false, false);
        renderChartData(dewPoint1d, await listSamples("dew_point", "-1d", "1h"), 24, false, false);
        renderChartData(heatIndex1d, await listSamples("heat_index", "-1d", "1h"), 24, false, false);
        renderChartData(absHumidity1d, await listSamples("absolute_humidity", "-1d", "1h"), 24, false, false);
    });

    // Info buttons
    const popoverTexts = {
        temp: "Shows temperature readings in °C.",
        humidity: "Shows relative humidity percentage.",
        light: "Shows ambient light intensity in Lux (lx).",
        dew: "Dew Point is the temperature at which air becomes saturated.",
        heat: "Heat Index combines air temperature and relative humidity.",
        abs: "Absolute Humidity is the total water vapor present (g/m³)."
    };

    Object.keys(popoverTexts).forEach(key => {
        document.querySelectorAll(`.info-btn.${key}`).forEach(img => {
            const popover = img.nextElementSibling;
            img.addEventListener('mouseenter', () => { popover.textContent = popoverTexts[key]; popover.style.display = 'block'; });
            img.addEventListener('mouseleave', () => { popover.style.display = 'none'; });
        });
    });

    initSocketIO();
});

function initSocketIO() {
    socket.on('connect', () => { if (errorContainer) errorContainer.style.display = 'none'; });
    socket.on('disconnect', () => { if (errorContainer) { errorContainer.textContent = 'Connection lost.'; errorContainer.style.display = 'block'; } });

    socket.on('temperature', m => renderChartData(temperatureLive, [m]));
    socket.on('humidity', m => renderChartData(humidityLive, [m]));
    socket.on('light', m => renderChartData(lightLive, [m]));
    socket.on('dew_point', m => renderChartData(dewPointLive, [m]));
    socket.on('heat_index', m => renderChartData(heatIndexLive, [m]));
    socket.on('absolute_humidity', m => renderChartData(absHumidityLive, [m]));
}

async function listSamples(resource, start, aggr_window) {
    try {
        const response = await fetch(`http://${window.location.host}/get_samples/${resource}/${start}/${aggr_window}`);
        const data = await response.json();
        return data.error ? [] : data;
    } catch (e) { console.log(e); return []; }
}

function renderChartData(obj, messages, maxPoints = 20, showMinutes = true, showSeconds = true) {
    if (!messages || messages.length === 0) return;
    const isLive = obj.canvas && obj.canvas.id && obj.canvas.id.endsWith('-live-chart');
    if (!isLive) { obj.data.labels = []; obj.data.datasets[0].data = []; }

    messages.forEach(message => {
        let date = new Date(message.ts);
        const options = { hour: '2-digit' };
        if (showMinutes) options.minute = '2-digit';
        if (showSeconds) options.second = '2-digit';
        
        obj.data.labels.push(date.toLocaleTimeString([], options));
        obj.data.datasets[0].data.push(message.value);
        if (obj.data.labels.length > maxPoints) { obj.data.labels.shift(); obj.data.datasets[0].data.shift(); }
    });

    const noDataDiv = document.getElementById((obj.canvas && obj.canvas.id) + '-nodata');
    if (obj.canvas) obj.canvas.style.display = 'block';
    if (noDataDiv) noDataDiv.style.display = 'none';
    
    if (!obj.chart) obj.chart = newChart(obj.canvas.getContext('2d'), obj);
    else obj.chart.update();
}

function newChart(ctx, obj) {
    return new Chart(ctx, {
        type: 'line',
        data: obj.data,
        options: {
            responsive: true,
            animation: false,
            scales: { y: obj.unit === '%' ? { min: 0, max: 100 } : {} },
            plugins: { 
                legend: { display: false },
                tooltip: { callbacks: { label: c => `${c.label} - ${c.parsed.y.toFixed(1)} ${obj.unit}` } }
            }
        }
    });
}

function newChartData(borderColor, backgroundColor) {
    return { labels: [], datasets: [{ data: [], borderColor, backgroundColor, fill: true }] };
}