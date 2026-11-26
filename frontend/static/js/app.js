// --- NAVEGACIÓN ENTRE LOGIN Y REGISTRO ---
function toggleAuthForm(formType) {
    const loginCard = document.getElementById('auth-login');
    const registerCard = document.getElementById('auth-register');
    if (formType === 'register') {
        loginCard.classList.add('hidden'); registerCard.classList.remove('hidden');
    } else {
        registerCard.classList.add('hidden'); loginCard.classList.remove('hidden');
    }
}

// --- LÓGICA DE AUTENTICACIÓN ---
async function handleAuth(endpoint, email, password, msgElement) {
    try {
        const res = await fetch(`/api/auth/${endpoint}`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (!res.ok) {
            let errorMsg = "Error de validación";
            if (data.detail && Array.isArray(data.detail)) errorMsg = data.detail.map(err => err.msg).join(". ");
            else if (data.detail) errorMsg = data.detail;
            throw new Error(errorMsg);
        }
        if (endpoint === 'login') {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('email', email);
            checkAuth();
        } else {
            msgElement.innerText = "¡Registro exitoso! Redirigiendo...";
            setTimeout(() => toggleAuthForm('login'), 1500);
        }
    } catch (e) { msgElement.innerText = e.message; }
}

document.getElementById('btn-do-login').addEventListener('click', () => handleAuth('login', document.getElementById('login-email').value, document.getElementById('login-password').value, document.getElementById('login-msg')));
document.getElementById('btn-do-register').addEventListener('click', () => handleAuth('register', document.getElementById('reg-email').value, document.getElementById('reg-password').value, document.getElementById('reg-msg')));
document.getElementById('btn-logout').addEventListener('click', () => { localStorage.removeItem('token'); localStorage.removeItem('email'); checkAuth(); });

// --- LÓGICA DEL DASHBOARD ---
const dropZone = document.getElementById('drop-zone');
const uploadText = document.getElementById('upload-text');
const fileNameDisplay = document.getElementById('file-name-display');
const fileInput = document.getElementById('file-input');
const previewImg = document.getElementById('image-preview');
const btnAnalyze = document.getElementById('btn-analyze');
const tbody = document.getElementById('events-table-body');
let selectedFile = null;
let socket = null;
let alertCount = 0;
let currentMaxRisk = 0;

dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => { 
    selectedFile = e.target.files[0]; 
    if (selectedFile) {
        const reader = new FileReader();
        reader.onload = (ev) => {
            // Mostrar imagen y ocultar texto interno
            previewImg.src = ev.target.result;
            previewImg.classList.remove('hidden');
            uploadText.classList.add('hidden');
            
            // Mostrar nombre FUERA del recuadro
            fileNameDisplay.innerText = "Archivo: " + selectedFile.name;
            fileNameDisplay.classList.remove('hidden');
            
            dropZone.style.border = "none"; // Quitar borde punteado cuando hay imagen
        };
        reader.readAsDataURL(selectedFile);
        btnAnalyze.disabled = false;
    }
});

btnAnalyze.addEventListener('click', async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('file', selectedFile);
    btnAnalyze.disabled = true; btnAnalyze.innerText = "Analizando...";
    
    try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/analyze', { method: 'POST', body: formData, headers: { 'Authorization': `Bearer ${token}` } });
        if (res.status === 401) { localStorage.removeItem('token'); checkAuth(); return; }
        loadEvents();
    } catch (e) { alert("Error de red"); } 
    finally { btnAnalyze.disabled = false; btnAnalyze.innerText = "Procesar Imagen"; }
});

async function loadEvents() {
    try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/events', { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.status === 401) { localStorage.removeItem('token'); checkAuth(); return; }
        
        const events = await res.json();
        tbody.innerHTML = '';
        alertCount = events.length;
        updateKPIs();

        if (events.length === 0) { 
            tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No hay alertas registradas.</td></tr>'; 
            return; 
        }
        events.forEach(ev => addAlertToTable(ev, false));
    } catch (e) { console.error(e); }
}

function addAlertToTable(ev, isNew = true) {
    if (tbody.querySelector('.empty-state')) tbody.innerHTML = '';
    const isRed = ev.score >= 0.75;
    const isWarn = ev.score >= 0.40 && ev.score < 0.75;
    let badgeClass = isRed ? 'badge-danger' : 'badge-warn';
    let estado = isRed ? 'ATAQUE 🚨' : 'MERODEO ⚠️';
    const timeStr = ev.time ? ev.time.includes("T") ? new Date(ev.time).toLocaleTimeString() : ev.time : new Date().toLocaleTimeString();

    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td class="mono">${timeStr}</td>
        <td style="font-weight:600;">${ev.bird.toUpperCase()}</td>
        <td style="font-weight:600;">${ev.fruit.toUpperCase()}</td>
        <td class="mono" style="color: ${isRed ? 'var(--danger)' : 'var(--warn)'}; font-weight:bold;">${ev.score.toFixed(2)}</td>
        <td><span class="badge ${badgeClass}">${estado}</span></td>
    `;
    if (isNew) { tr.style.animation = "pulse-red 1s ease"; tbody.prepend(tr); }
    else { tbody.appendChild(tr); }

    if (isNew) {
        alertCount++;
        if (ev.score > currentMaxRisk) currentMaxRisk = ev.score;
        updateKPIs();
    } else {
        if (ev.score > currentMaxRisk) currentMaxRisk = ev.score;
    }
}

function updateKPIs() {
    document.getElementById('kpi-total').innerText = alertCount;
    const riskEl = document.getElementById('kpi-risk');
    if (currentMaxRisk >= 0.75) { riskEl.innerText = "Alto"; riskEl.className = "kpi-value text-danger"; }
    else if (currentMaxRisk >= 0.40) { riskEl.innerText = "Medio"; riskEl.className = "kpi-value"; riskEl.style.color = "var(--warn)"; }
    else { riskEl.innerText = "Bajo"; riskEl.className = "kpi-value text-success"; }
}

function connectWebSocket() {
    if (socket) socket.close();
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${window.location.host}/api/ws/alerts`);
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "new_alert") {
            addAlertToTable({ bird: data.bird, fruit: data.fruit, score: data.score, time: new Date() }, true);
        }
    };
    socket.onclose = () => setTimeout(connectWebSocket, 3000);
}

function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        const email = localStorage.getItem('email') || 'Usuario';
        const name = email.split('@')[0];
        const formattedName = name.charAt(0).toUpperCase() + name.slice(1);
        
        // Calcular saludo según la hora del día
        const hour = new Date().getHours();
        let greeting = 'Buenas noches,';
        if (hour >= 5 && hour < 12) greeting = 'Buenos días,';
        else if (hour >= 12 && hour < 19) greeting = 'Buenas tardes,';

        // Actualizar HTML sin el emoji genérico
        document.getElementById('greeting-text').innerHTML = `${greeting} <strong>${formattedName}</strong>.`;
        document.getElementById('view-auth').classList.add('hidden');
        document.getElementById('view-dashboard').classList.remove('hidden');
        loadEvents();
        connectWebSocket();
    } else {
        document.getElementById('view-dashboard').classList.add('hidden');
        document.getElementById('view-auth').classList.remove('hidden');
        toggleAuthForm('login');
        if (socket) socket.close();
        currentMaxRisk = 0;
    }
}

checkAuth();

// ==========================================
// LÓGICA DEL MODAL DE REPORTES (Añadido)
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    const modalReports = document.getElementById('modal-reports');
    const btnOpenReports = document.getElementById('btn-open-reports');
    const btnCloseReports = document.getElementById('btn-close-reports');
    const reportsTableBody = document.getElementById('reports-table-body');
    const btnExport = document.getElementById('btn-export-excel');

    // Si los elementos existen en el DOM, activamos los eventos
    if (btnOpenReports) {
        btnOpenReports.addEventListener('click', async () => {
            modalReports.classList.remove('hidden');
            reportsTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Cargando historial...</td></tr>';
            
            try {
                const token = localStorage.getItem('token');
                const res = await fetch('/api/reports/data', { headers: { 'Authorization': `Bearer ${token}` } });
                if(!res.ok) throw new Error("Error API");
                
                const data = await res.json();
                reportsTableBody.innerHTML = '';
                
                if (data.length === 0) {
                    reportsTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No hay datos.</td></tr>';
                    return;
                }
                
                data.forEach(row => {
                    const isRed = row["Estado"].includes("ATAQUE");
                    const color = isRed ? '#ef4444' : '#f59e0b';
                    reportsTableBody.innerHTML += `
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <td style="padding:10px;">${row["Hora"]}</td>
                            <td style="padding:10px; font-weight:bold; color: var(--accent-primary);">${row["Bloque"]}</td>
                            <td style="padding:10px;">${row["Especie"]}</td>
                            <td style="padding:10px;">${row["Cultivo"]}</td>
                            <td style="padding:10px; color:${color}; font-weight:bold;">${row["Riesgo"]}</td>
                            <td style="padding:10px; color:${color};">${row["Estado"]}</td>
                        </tr>`;
                });
            } catch (e) {
                reportsTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Error al cargar datos.</td></tr>';
            }
        });
    }

    if (btnCloseReports) {
        btnCloseReports.addEventListener('click', () => modalReports.classList.add('hidden'));
    }

    if (btnExport) {
        btnExport.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                const token = localStorage.getItem('token');
                const res = await fetch('/api/reports/export/excel', { headers: { 'Authorization': `Bearer ${token}` } });
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'Reporte_Fruitit.xlsx';
                document.body.appendChild(a);
                a.click();
                a.remove();
            } catch (error) { alert("Error descargando el Excel"); }
        });
    }
});

// ==========================================
// LÓGICA DE CONTROL DE CÁMARA
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    const btnToggleCam = document.getElementById('btn-toggle-cam');
    const camIpInput = document.getElementById('cam-ip');
    const camPortInput = document.getElementById('cam-port');
    
    let isCamActive = false;

    // Verificar estado inicial
    fetch('/api/camera/status').then(res => res.json()).then(data => {
        isCamActive = data.active;
        updateCamButton();
        if (data.url) {
            const parts = data.url.replace('http://', '').replace('/video', '').split(':');
            camIpInput.value = parts[0];
            camPortInput.value = parts[1];
        }
    });

    btnToggleCam.addEventListener('click', async () => {
        const ip = camIpInput.value.trim();
        const port = camPortInput.value.trim();
        
        if (!isCamActive && (!ip || !port)) {
            alert("Por favor ingresa la IP y el puerto.");
            return;
        }

        btnToggleCam.innerText = "Procesando...";
        btnToggleCam.disabled = true;

        try {
            const action = isCamActive ? "stop" : "start";
            const res = await fetch('/api/camera/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ip: ip, port: port, action: action })
            });
            
            if (res.ok) {
                isCamActive = !isCamActive;
                updateCamButton();
            }
        } catch (e) {
            alert("Error de conexión");
        } finally {
            btnToggleCam.disabled = false;
        }
    });

    function updateCamButton() {
        if (isCamActive) {
            btnToggleCam.innerText = "Apagar Cámara";
            btnToggleCam.style.background = "linear-gradient(180deg, #ef4444 0%, #dc2626 100%)"; // Rojo
        } else {
            btnToggleCam.innerText = "Encender Cámara";
            btnToggleCam.style.background = "linear-gradient(180deg, #10B981 0%, #059669 100%)"; // Verde
        }
    }
});
