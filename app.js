/* ============================================
   NASA Space Data Explorer - Frontend Logic
   ============================================ */

const API_BASE = window.location.origin;
let asteroidData = [];
let currentSort = { column: null, direction: 'asc' };

// ================================================================
// INIT
// ================================================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initAPOD();
    initAsteroids();
    checkHealth();
    loadDashboard();

    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadDashboard();
        showToast('Data refreshed successfully');
    });
});

// ================================================================
// NAVIGATION
// ================================================================

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');
    const pageTitle = document.getElementById('pageTitle');

    const titles = {
        dashboard: 'Dashboard',
        apod: 'Astronomy Picture of the Day',
        asteroids: 'Near-Earth Asteroids'
    };

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const viewName = item.dataset.view;

            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            views.forEach(v => v.classList.remove('active'));
            document.getElementById(viewName + 'View').classList.add('active');

            pageTitle.textContent = titles[viewName];
        });
    });
}

// ================================================================
// HEALTH CHECK
// ================================================================

async function checkHealth() {
    const dot = document.getElementById('apiStatusDot');
    const text = document.getElementById('apiStatusText');

    try {
        const res = await fetch(`${API_BASE}/api/health`);
        if (res.ok) {
            dot.classList.add('online');
            text.textContent = 'API Online';
        } else {
            throw new Error('API Error');
        }
    } catch (e) {
        dot.classList.add('offline');
        text.textContent = 'API Offline';
    }
}

// ================================================================
// DASHBOARD
// ================================================================

async function loadDashboard() {
    try {
        const [asteroidsRes, statsRes] = await Promise.all([
            fetch(`${API_BASE}/api/asteroids`),
            fetch(`${API_BASE}/api/asteroids/stats`)
        ]);

        const asteroids = await asteroidsRes.json();
        const stats = await statsRes.json();

        if (asteroids.success) {
            asteroidData = asteroids.data;
            renderDashboardTable(asteroidData.slice(0, 10));
        }

        if (stats.success && stats.stats) {
            renderStats(stats.stats);
        }
    } catch (e) {
        console.error('Dashboard load error:', e);
    }
}

function renderStats(stats) {
    document.getElementById('statTotal').textContent = stats.total.toLocaleString();
    document.getElementById('statHazardous').textContent = stats.hazardous_count;
    document.getElementById('statSafe').textContent = stats.safe_count;
    document.getElementById('statAvgSpeed').textContent = stats.avg_velocity.toFixed(2);

    document.getElementById('fastestName').textContent = stats.fastest.name;
    document.getElementById('fastestSpeed').textContent = stats.fastest.speed_km_s + ' km/s';

    document.getElementById('closestName').textContent = stats.closest.name;
    document.getElementById('closestDistance').textContent = stats.closest.distance_km.toLocaleString() + ' km';

    document.getElementById('largestName').textContent = stats.largest.name;
    document.getElementById('largestSize').textContent = stats.largest.diameter_km + ' km';

    // Update donut chart
    const percent = stats.hazardous_percentage;
    const circumference = 2 * Math.PI * 50;
    const offset = circumference - (percent / 100) * circumference;
    const segment = document.getElementById('hazardSegment');
    segment.style.strokeDasharray = `${circumference - offset} ${offset}`;
    document.getElementById('hazardPercent').textContent = percent + '%';
}

function renderDashboardTable(data) {
    const tbody = document.querySelector('#dashboardTable tbody');
    tbody.innerHTML = data.map(a => `
        <tr>
            <td><strong>${a.name}</strong></td>
            <td>${a.date}</td>
            <td>${a.hazardous 
                ? '<span class="badge hazardous">Hazardous</span>' 
                : '<span class="badge safe">Safe</span>'}</td>
            <td>${a.velocity_km_s}</td>
            <td>${a.distance_km.toLocaleString()}</td>
            <td>${a.max_diameter_km}</td>
        </tr>
    `).join('');
}

// ================================================================
// APOD
// ================================================================

function initAPOD() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('apodDate').value = today;

    loadAPOD();

    document.getElementById('loadApodBtn').addEventListener('click', () => {
        const date = document.getElementById('apodDate').value;
        loadAPOD(date);
    });
}

async function loadAPOD(date = null) {
    const container = document.getElementById('apodContent');
    container.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading Astronomy Picture of the Day...</p>
        </div>
    `;

    try {
        const url = date 
            ? `${API_BASE}/api/apod?date=${date}` 
            : `${API_BASE}/api/apod`;

        const res = await fetch(url);
        const data = await res.json();

        if (!data.success) {
            throw new Error(data.error);
        }

        const apod = data.data;
        const mediaHtml = apod.media_type === 'video'
            ? `<iframe src="${apod.url}" allowfullscreen></iframe>`
            : `<img src="${apod.hdurl || apod.url}" alt="${apod.title}" loading="lazy">`;

        container.innerHTML = `
            <div class="apod-media">${mediaHtml}</div>
            <div class="apod-info">
                <h2>${apod.title}</h2>
                <span class="date">${apod.date} ${apod.copyright ? '• © ' + apod.copyright : ''}</span>
                <p class="explanation">${apod.explanation}</p>
            </div>
        `;
    } catch (e) {
        container.innerHTML = `
            <div class="error-state">
                <h3>Failed to load APOD</h3>
                <p>${e.message}</p>
            </div>
        `;
    }
}

// ================================================================
// ASTEROIDS
// ================================================================

function initAsteroids() {
    const today = new Date();
    const twoDaysLater = new Date(today);
    twoDaysLater.setDate(today.getDate() + 2);

    document.getElementById('startDate').value = today.toISOString().split('T')[0];
    document.getElementById('endDate').value = twoDaysLater.toISOString().split('T')[0];

    document.getElementById('filterDateBtn').addEventListener('click', loadAsteroids);
    document.getElementById('hazardFilter').addEventListener('change', filterAsteroids);
    document.getElementById('searchFilter').addEventListener('input', debounce(filterAsteroids, 300));

    // Sort handlers
    document.querySelectorAll('#asteroidsTable th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.dataset.sort;
            if (currentSort.column === column) {
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.column = column;
                currentSort.direction = 'asc';
            }
            sortAndRender();
        });
    });

    loadAsteroids();
}

async function loadAsteroids() {
    const start = document.getElementById('startDate').value;
    const end = document.getElementById('endDate').value;

    const tbody = document.querySelector('#asteroidsTable tbody');
    tbody.innerHTML = `
        <tr><td colspan="7" style="text-align:center;padding:40px;">
            <div class="spinner" style="margin:0 auto 16px;"></div>
            Loading asteroid data...
        </td></tr>
    `;

    try {
        const url = `${API_BASE}/api/asteroids?start_date=${start}&end_date=${end}`;
        const res = await fetch(url);
        const data = await res.json();

        if (!data.success) {
            throw new Error(data.error);
        }

        asteroidData = data.data;
        filterAsteroids();
    } catch (e) {
        tbody.innerHTML = `
            <tr><td colspan="7" class="error-state">
                <h3>Failed to load data</h3>
                <p>${e.message}</p>
            </td></tr>
        `;
    }
}

function filterAsteroids() {
    const hazardFilter = document.getElementById('hazardFilter').value;
    const searchQuery = document.getElementById('searchFilter').value.toLowerCase();

    let filtered = asteroidData;

    if (hazardFilter === 'hazardous') {
        filtered = filtered.filter(a => a.hazardous);
    } else if (hazardFilter === 'safe') {
        filtered = filtered.filter(a => !a.hazardous);
    }

    if (searchQuery) {
        filtered = filtered.filter(a => a.name.toLowerCase().includes(searchQuery));
    }

    sortAndRender(filtered);
}

function sortAndRender(data = null) {
    let toRender = data || asteroidData;

    if (currentSort.column) {
        toRender = [...toRender].sort((a, b) => {
            let valA = a[currentSort.column];
            let valB = b[currentSort.column];

            if (typeof valA === 'string') {
                valA = valA.toLowerCase();
                valB = valB.toLowerCase();
            }

            if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
            if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
            return 0;
        });
    }

    renderAsteroidsTable(toRender);
}

function renderAsteroidsTable(data) {
    const tbody = document.querySelector('#asteroidsTable tbody');

    if (data.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="7" style="text-align:center;padding:40px;color:var(--text-tertiary);">
                No asteroids found matching your criteria.
            </td></tr>
        `;
        return;
    }

    tbody.innerHTML = data.map(a => `
        <tr>
            <td><strong>${a.name}</strong></td>
            <td>${a.date}</td>
            <td>${a.hazardous 
                ? '<span class="badge hazardous">Hazardous</span>' 
                : '<span class="badge safe">Safe</span>'}</td>
            <td>${a.velocity_km_s}</td>
            <td>${a.distance_km.toLocaleString()}</td>
            <td>${a.max_diameter_km}</td>
            <td>${a.min_diameter_km}</td>
        </tr>
    `).join('');
}

// ================================================================
// UTILS
// ================================================================

function debounce(fn, ms) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), ms);
    };
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: var(--bg-elevated);
        color: var(--text-primary);
        padding: 14px 24px;
        border-radius: var(--radius-sm);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add keyframes for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(style);
