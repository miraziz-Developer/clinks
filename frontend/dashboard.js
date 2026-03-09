const API = 'http://localhost/api/v1';
let clinicId = null;
let allPatients = [];
let apptChart = null, statusChart = null;

const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
if (currentUser.role === 'admin' && location.pathname.endsWith('dashboard.html')) {
    location.href = 'staff.html';
}

// ═══════════════ I18N ═══════════════
const T = {
    uz: {
        nav_dashboard: "Dashboard", nav_appt: "Navbatlar", nav_doctors: "Shifokorlar", nav_patients: "Bemorlar", nav_services: "Xizmatlar", nav_staff: "Xodimlar", nav_analytics: "Analitika", nav_bot: "Telegram Bot", nav_settings: "Sozlamalar", nav_main: "ASOSIY", nav_manage: "BOSHQARUV",
        sb_logout: "Chiqish", dash_title: "Dashboard", stat_total_appt: "Jami navbatlar", stat_patients: "Jami bemorlar", stat_doctors: "Shifokorlar", stat_revenue: "Daromad (so'm)",
        chart_appt: "Navbatlar dinamikasi", chart_week: "Oxirgi 7 kun", chart_status: "Navbat holatlari", chart_revenue: "Daromad dinamikasi",
        top_doctors: "Top shifokorlar", today_appts: "Bugungi navbatlar", see_all: "Barchasini ko'rish",
        th_patient: "Bemor", th_doctor: "Shifokor", th_date: "Sana", th_time: "Vaqt", th_service: "Xizmat", th_status: "Holat", th_payment: "To'lov", th_action: "Amal",
        th_name: "Nomi", th_phone: "Telefon", th_dob: "Tug'ilgan kun", th_gender: "Jins", th_appts: "Navbatlar", th_duration: "Davomiyligi", th_price: "Narxi", th_city: "Shahar",
        btn_add: "Qo'shish", new_appt: "Yangi navbat", add_doctor: "Shifokor qo'shish", add_patient: "Bemor qo'shish", add_service: "Xizmat qo'shish", add_staff: "Xodim qo'shish",
        btn_new_appt: "Yangi navbat", btn_add_doctor: "Shifokor qo'shish", btn_add_patient: "Bemor qo'shish", btn_add_service: "Xizmat qo'shish", btn_add_staff: "Xodim qo'shish",
        btn_save: "Saqlash", btn_cancel: "Bekor", clinic_info: "Klinika ma'lumotlari", field_clinic_name: "Klinika nomi", field_phone: "Telefon", field_city: "Shahar", field_email: "Email", field_address: "Manzil",
        field_first_name: "Ism", field_last_name: "Familiya", field_username: "Tizimga kirish (Login)", field_password: "Parol", all: "Barchasi", pending: "Kutilmoqda", confirmed: "Tasdiqlangan", completed: "Tugallangan", cancelled: "Bekor qilingan",
        opt_7d: "7 kun", opt_30d: "30 kun", bot_users: "Bot foydalanuvchilari", bot_appt: "Bot orqali navbatlar", bot_visits: "Profil ko'rishlar", bot_rating: "O'rtacha reyting"
    },
    ru: {
        nav_dashboard: "Дашборд", nav_appt: "Записи", nav_doctors: "Врачи", nav_patients: "Пациенты", nav_services: "Услуги", nav_staff: "Сотрудники", nav_analytics: "Аналитика", nav_bot: "Telegram Бот", nav_settings: "Настройки", nav_main: "ГЛАВНОЕ", nav_manage: "УПРАВЛЕНИЕ",
        sb_logout: "Выйти", dash_title: "Дашборд", stat_total_appt: "Всего записей", stat_patients: "Всего пациентов", stat_doctors: "Врачи", stat_revenue: "Доход (сум)",
        chart_appt: "Динамика записей", chart_week: "Последние 7 дней", chart_status: "Статусы записей", chart_revenue: "Динамика дохода",
        top_doctors: "Топ врачи", today_appts: "Записи на сегодня", see_all: "Показать все",
        th_patient: "Пациент", th_doctor: "Врач", th_date: "Дата", th_time: "Время", th_service: "Услуга", th_status: "Статус", th_payment: "Оплата", th_action: "Действие",
        th_name: "Название", th_phone: "Телефон", th_dob: "Дата рождения", th_gender: "Пол", th_appts: "Записи", th_duration: "Длительность", th_price: "Цена",
        btn_add: "Добавить", new_appt: "Новая запись", add_doctor: "Добавить врача", add_patient: "Добавить пациента", add_service: "Добавить услугу", add_staff: "Добавить сотрудника",
        btn_new_appt: "Новая запись", btn_add_doctor: "Добавить врача", btn_add_patient: "Добавить пациента", btn_add_service: "Добавить услугу", btn_add_staff: "Добавить сотрудника",
        btn_save: "Сохранить", btn_cancel: "Отмена", clinic_info: "Данные клиники", field_clinic_name: "Название клиники", field_phone: "Телефон", field_city: "Город", field_email: "Email", field_address: "Адрес",
        field_first_name: "Имя", field_last_name: "Фамилия", field_username: "Логин", field_password: "Пароль", all: "Все", pending: "Ожидает", confirmed: "Подтверждено", completed: "Завершено", cancelled: "Отменено",
        opt_7d: "7 дней", opt_30d: "30 дней", bot_users: "Пользователи бота", bot_appt: "Записи через бот", bot_visits: "Просмотры профиля", bot_rating: "Средний рейтинг"
    },
    en: {
        nav_dashboard: "Dashboard", nav_appt: "Appointments", nav_doctors: "Doctors", nav_patients: "Patients", nav_services: "Services", nav_staff: "Staff", nav_analytics: "Analytics", nav_bot: "Telegram Bot", nav_settings: "Settings", nav_main: "MAIN", nav_manage: "MANAGEMENT",
        sb_logout: "Logout", dash_title: "Dashboard", stat_total_appt: "Total appointments", stat_patients: "Total patients", stat_doctors: "Doctors", stat_revenue: "Revenue (UZS)",
        chart_appt: "Appointments dynamics", chart_week: "Last 7 days", chart_status: "Appointment statuses", chart_revenue: "Revenue dynamics",
        top_doctors: "Top doctors", today_appts: "Today's appointments", see_all: "See all",
        th_patient: "Patient", th_doctor: "Doctor", th_date: "Date", th_time: "Time", th_service: "Service", th_status: "Status", th_payment: "Payment", th_action: "Action",
        th_name: "Name", th_phone: "Phone", th_dob: "Date of birth", th_gender: "Gender", th_appts: "Appointments", th_duration: "Duration", th_price: "Price",
        btn_add: "Add New", new_appt: "New appointment", add_doctor: "Add doctor", add_patient: "Add patient", add_service: "Add service", add_staff: "Add staff",
        btn_new_appt: "New appointment", btn_add_doctor: "Add doctor", btn_add_patient: "Add patient", btn_add_service: "Add service", btn_add_staff: "Add staff",
        btn_save: "Save", btn_cancel: "Cancel", clinic_info: "Clinic information", field_clinic_name: "Clinic name", field_phone: "Phone", field_city: "City", field_email: "Email", field_address: "Address",
        field_first_name: "First name", field_last_name: "Last name", field_username: "Username", field_password: "Password", all: "All", pending: "Pending", confirmed: "Confirmed", completed: "Completed", cancelled: "Cancelled",
        opt_7d: "7 days", opt_30d: "30 days", bot_users: "Bot users", bot_appt: "Appointments via bot", bot_visits: "Profile views", bot_rating: "Average rating"
    }
};

let lang = localStorage.getItem('lang') || 'uz';
function setLang(l) {
    lang = l; localStorage.setItem('lang', l);
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.lang-btn').forEach(b => { if (b.textContent.trim().toLowerCase() === l) b.classList.add('active') });
    document.querySelectorAll('[data-i18n]').forEach(el => { const k = el.getAttribute('data-i18n'); if (T[l] && T[l][k]) el.textContent = T[l][k] });
}

// ═══════════════ AUTH & API ═══════════════
const token = () => localStorage.getItem('access');
async function apiFetch(path, opts = {}) {
    const url = (path.startsWith('http') || path.startsWith('/')) ? path : API + path;
    const absUrl = path.startsWith('http') ? path : (API.endsWith('/') ? API.slice(0, -1) : API) + (path.startsWith('/') ? path : '/' + path);

    const isFormData = opts.body instanceof FormData;
    const headers = {
        'Authorization': 'Bearer ' + token(),
        ...(opts.headers || {})
    };
    if (!isFormData) headers['Content-Type'] = 'application/json';

    const res = await fetch(path.startsWith('http') ? path : absUrl, {
        ...opts,
        headers,
        body: isFormData ? opts.body : (opts.body ? (typeof opts.body === 'string' ? opts.body : JSON.stringify(opts.body)) : undefined)
    });
    if (res.status === 401) { doLogout(); return null; }
    return res.ok ? res.json() : null;
}
function doLogout() { localStorage.clear(); window.location.href = 'login.html'; }

// ═══════════════ NAVIGATION ═══════════════
const pages = ['dashboard', 'appointments', 'doctors', 'patients', 'services', 'staff', 'analytics', 'bot', 'settings'];
function goPage(name) {
    pages.forEach(p => {
        document.getElementById('page-' + p)?.classList.remove('active');
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    });
    const target = document.getElementById('page-' + name);
    if (target) target.classList.add('active');

    document.querySelectorAll('.nav-item').forEach(n => {
        if (n.getAttribute('onclick')?.includes("'" + name + "'")) n.classList.add('active')
    });

    const key = 'nav_' + name;
    document.getElementById('page-title').textContent = T[lang][key] || name;
    document.querySelector('.content').scrollTop = 0;

    if (name === 'dashboard') loadDashboard();
    if (name === 'appointments') loadAppointments();
    if (name === 'doctors') loadDoctors();
    if (name === 'patients') loadPatients();
    if (name === 'services') loadServices();
    if (name === 'analytics') loadAnalytics();
    if (name === 'bot') loadBot();
    if (name === 'staff') loadStaff();
    if (name === 'settings') loadSettings();
}

// ═══════════════ QUICK ADD & MODALS ═══════════════
function toggleQuickAdd() {
    document.getElementById('quick-add-menu').classList.toggle('active');
}

function openModal(id, isEdit = false) {
    if (!isEdit) {
        if (id === 'doctor') {
            currentEditDoctorId = null;
            document.getElementById('doc-fname').value = '';
            document.getElementById('doc-lname').value = '';
            document.getElementById('doc-specialty').value = '';
            document.getElementById('doc-phone').value = '';
            document.getElementById('doc-exp').value = '1';
            document.getElementById('doc-price').value = '';
            document.getElementById('doc-bio').value = '';
            document.getElementById('doc-edu').value = '';
            document.getElementById('doc-achievements').value = '';
            if (document.getElementById('doc-photo')) document.getElementById('doc-photo').value = '';
        } else if (id === 'patient') {
            currentEditPatientId = null;
            document.getElementById('pat-fname').value = '';
            document.getElementById('pat-lname').value = '';
            document.getElementById('pat-phone').value = '';
            document.getElementById('pat-dob').value = '';
            document.getElementById('pat-gender').value = '';
        } else if (id === 'service') {
            currentEditServiceId = null;
            document.getElementById('svc-name').value = '';
            document.getElementById('svc-price').value = '';
            document.getElementById('svc-duration').value = '30';
            document.getElementById('svc-desc').value = '';
        } else if (id === 'staff') {
            document.getElementById('stf-fname').value = '';
            document.getElementById('stf-lname').value = '';
            document.getElementById('stf-phone').value = '';
            document.getElementById('stf-username').value = '';
            document.getElementById('stf-password').value = '';
        }
    }

    // Dynamic modal title
    const titles = {
        doctor: isEdit ? "Shifokorni tahrirlash" : "Shifokor qo'shish",
        patient: isEdit ? "Bemorni tahrirlash" : "Bemor qo'shish",
        service: isEdit ? "Xizmatni tahrirlash" : "Xizmat qo'shish",
        staff: "Xodim qo'shish",
    };
    const titleEl = document.querySelector(`#modal-${id} .modal-title`);
    if (titleEl && titles[id]) titleEl.textContent = titles[id];

    document.getElementById('modal-' + id).classList.add('active');
    document.getElementById('quick-add-menu')?.classList.remove('active');
    if (id === 'appt') loadApptSelects();
}
function closeModal(id) {
    document.getElementById('modal-' + id).classList.remove('active');
}

document.addEventListener('click', (e) => {
    // Quick Add Menu close
    const qMenu = document.getElementById('quick-add-menu');
    const qBtn = document.getElementById('btn-quick-add');
    if (qMenu?.classList.contains('active') && !qMenu.contains(e.target) && !qBtn.contains(e.target)) {
        qMenu.classList.remove('active');
    }
    // Drawer/Modal Overlay close
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});

// ═══════════════ DASHBOARD ═══════════════
async function loadDashboard() {
    if (!clinicId) await loadClinicId();
    const stats = await apiFetch(`/appointments/stats/?clinic=${clinicId}`);
    if (stats) {
        document.getElementById('stat-appt-total').textContent = stats.total || 0;
        document.getElementById('stat-patients').textContent = stats.unique_patients || 0;
        document.getElementById('stat-doctors').textContent = stats.doctors_count || 0;
        document.getElementById('stat-revenue').textContent = (stats.total_revenue || 0).toLocaleString();

        // Charts - only render if we have real data
        if (stats.status_breakdown && Object.values(stats.status_breakdown).some(v => v > 0)) {
            renderStatusChart(stats.status_breakdown);
        } else {
            renderEmptyStatusChart();
        }
    }
    await loadTodayAppointments();
    await loadChart(7);
    await loadTopDoctors();
    await loadRecentActivity();
}

async function loadRecentActivity() {
    const data = await apiFetch(`/appointments/?clinic=${clinicId}`);
    const list = data?.results || data || [];
    const container = document.getElementById('recent-activity-list');
    if (!container) return;
    if (!list.length) {
        container.innerHTML = '<div class="empty">Harakatlar yo\'q</div>';
        return;
    }
    container.innerHTML = list.slice(0, 5).map(a => `
        <div class="flex items-center gap-3 p-3" style="background:var(--gray-50);border-radius:12px">
            <div class="stat-icon" style="width:36px;height:36px;font-size:14px;background:#fff">
                <i class="fas ${a.status === 'completed' ? 'fa-check' : 'fa-clock'}" style="color:var(--primary)"></i>
            </div>
            <div style="flex:1">
                <div style="font-size:13px;font-weight:700;color:var(--dark)">${a.patient_name || 'Bemor'}</div>
                <div style="font-size:11px;color:var(--gray-400)">${a.doctor_name || 'Shifokor'} • ${a.time}</div>
            </div>
            <div style="font-size:11px;font-weight:700">${statusBadge(a.status)}</div>
        </div>
    `).join('');
}

async function loadTodayAppointments() {
    const rawData = await apiFetch(`/appointments/today/?clinic=${clinicId}`);
    const data = rawData?.results || rawData || [];
    const tbody = document.getElementById('today-tbody');

    if (!data || !data.length) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty"><i class="fas fa-calendar-day"></i>Bugun navbatlar yo'q</td></tr>`;
        return;
    }

    tbody.innerHTML = data.slice(0, 10).map(a => `
    <tr>
      <td><div class="flex items-center gap-2"><div class="avatar">${(a.patient_name || '?')[0]}</div>${a.patient_name || '—'}</div></td>
      <td>${a.doctor_name || '—'}</td>
      <td><strong>${a.time || '—'}</strong></td>
      <td>${statusBadge(a.status)}</td>
      <td>
        <div class="flex-gap">
            <button class="btn btn-outline btn-sm" onclick="updateApptStatus('${a.id}','confirmed')"><i class="fas fa-check"></i></button>
        </div>
      </td>
    </tr>`).join('');
}

async function loadChart(days) {
    if (!clinicId) await loadClinicId();
    const data = await apiFetch(`/analytics/clinic/?period=${days}&clinic=${clinicId}`);
    if (!data || !data.daily_stats) {
        renderEmptyChart();
        return;
    }

    const dates = data.daily_stats.map(s => {
        const d = new Date(s.date);
        return d.toLocaleDateString(lang, { month: 'short', day: 'numeric' });
    });
    const counts = data.daily_stats.map(s => s.total || 0);
    
    // Check if we have any real data
    if (counts.every(c => c === 0)) {
        renderEmptyChart();
        return;
    }

    const ctx = document.getElementById('apptChart').getContext('2d');
    if (apptChart) apptChart.destroy();


    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.2)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');

    apptChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates, datasets: [{
                label: 'Navbatlar',
                data: counts,
                borderColor: '#6366F1',
                borderWidth: 3,
                backgroundColor: gradient,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#6366F1',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.03)' }, border: { display: false } },
                x: { grid: { display: false }, border: { display: false } }
            }
        }
    });
}

function renderEmptyChart() {
    const canvas = document.getElementById('apptChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (apptChart) apptChart.destroy();

    // Show empty state message
    ctx.font = '14px Inter';
    ctx.fillStyle = '#9CA3AF';
    ctx.textAlign = 'center';
    ctx.fillText("Ma'lumotlar mavjud emas", canvas.width / 2, canvas.height / 2);
}

function renderEmptyStatusChart() {
    const canvas = document.getElementById('statusChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (statusChart) statusChart.destroy();

    // Show empty state message
    ctx.font = '14px Inter';
    ctx.fillStyle = '#9CA3AF';
    ctx.textAlign = 'center';
    ctx.fillText("Ma'lumotlar mavjud emas", canvas.width / 2, canvas.height / 2);
}

function renderStatusChart(breakdown) {
    const canvas = document.getElementById('statusChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (statusChart) statusChart.destroy();

    // Only render if we have real data
    if (!breakdown || Object.values(breakdown).every(v => v === 0)) {
        renderEmptyStatusChart();
        return;
    }

    const labels = Object.keys(breakdown).map(k => T[lang][k] || k);
    const values = Object.values(breakdown);

    statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values.every(v => v === 0) ? [1] : values,
                backgroundColor: ['#F59E0B', '#6366F1', '#EF4444', '#10B981', '#94A3B8'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right', labels: { boxWidth: 12, font: { size: 12, weight: '600' }, padding: 15 } }
            },
            cutout: '75%',
            animation: { animateScale: true }
        }
    });
}

async function loadTopDoctors() {
    const data = await apiFetch(`/analytics/clinic/?clinic=${clinicId}`);
    const list = document.getElementById('top-doctors-list');
    if (!data || !data.top_doctors?.length) {
        list.innerHTML = '<div class="empty">Top shifokorlar mavjud emas</div>';
        return;
    }
    list.innerHTML = data.top_doctors.slice(0, 5).map((d, i) => `
        <div class="flex items-center gap-3" style="padding:15px 0;border-bottom:1px solid var(--gray-100)">
          <div style="font-weight:800;color:var(--gray-400);font-size:14px;width:24px">#${i + 1}</div>
          <div class="avatar">${(d.name || 'D')[0]}</div>
          <div style="flex:1">
            <div style="font-size:14px;font-weight:700;color:var(--dark)">${d.name || '—'}</div>
            <div style="font-size:12px;color:var(--gray-600)">${d.appointments || 0} navbat</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:14px;font-weight:800;color:var(--primary)">${(d.revenue || 0).toLocaleString()}</div>
            <div style="font-size:10px;color:var(--success);font-weight:700">Tasdiqlangan</div>
          </div>
        </div>`).join('');
}
let revenueChart;

async function loadAnalytics() {
    const period = document.getElementById('analytics-period').value || '30';
    // Using actual backend API structure
    const data = await apiFetch(`/analytics/clinic/?period=${period}&clinic=${clinicId}`);
    if (!data || !data.summary) return;

    const summary = data.summary;

    const statsContainer = document.getElementById('analytics-stats');
    if (statsContainer) {
        statsContainer.innerHTML = `
            <div class="stat-card" style="background:var(--card);box-shadow:var(--shadow)">
                <div class="stat-top">
                    <i class="fas fa-money-bill-wave" style="font-size:24px;color:var(--success)"></i>
                </div>
                <div class="stat-val" style="font-size:24px">${(summary.total_revenue || 0).toLocaleString()} <span style="font-size:14px;color:var(--gray-400);font-weight:600">so'm</span></div>
                <div class="stat-label" data-i18n="total_revenue">Jami daromad</div>
            </div>
            <div class="stat-card" style="background:var(--card);box-shadow:var(--shadow)">
                <div class="stat-top">
                    <i class="fas fa-calendar-check" style="font-size:24px;color:var(--primary)"></i>
                </div>
                <div class="stat-val">${summary.completed || 0}</div>
                <div class="stat-label">Yakunlangan navbatlar</div>
            </div>
            <div class="stat-card" style="background:var(--card);box-shadow:var(--shadow)">
                <div class="stat-top">
                    <i class="fas fa-users" style="font-size:24px;color:#8B5CF6"></i>
                </div>
                <div class="stat-val">${summary.total_patients || 0}</div>
                <div class="stat-label">Bemorlar soni</div>
            </div>
            <div class="stat-card" style="background:var(--card);box-shadow:var(--shadow)">
                <div class="stat-top">
                    <i class="fas fa-user-plus" style="font-size:24px;color:#F59E0B"></i>
                </div>
                <div class="stat-val">+${summary.new_patients_period || 0}</div>
                <div class="stat-label">Yangi bemorlar</div>
            </div>
        `;
    }

    const list = document.getElementById('analytics-top-doctors-list');
    if (list) {
        if (!data.top_doctors || !data.top_doctors.length) {
            list.innerHTML = '<div class="empty" style="padding:40px 0;text-align:center;color:var(--gray-400)"><i class="fas fa-user-md fa-3x mb-3" style="opacity:0.2"></i><br>Top shifokorlar mavjud emas</div>';
        } else {
            list.innerHTML = data.top_doctors.slice(0, 5).map((d, i) => `
                <div class="flex items-center gap-3" style="padding:15px 0;border-bottom:1px solid var(--gray-100)">
                <div style="font-weight:800;color:var(--gray-400);font-size:14px;width:24px">#${i + 1}</div>
                <div class="avatar">${(d.name || 'D')[0]}</div>
                <div style="flex:1">
                    <div style="font-size:14px;font-weight:700;color:var(--dark)">${d.name || '—'}</div>
                    <div style="font-size:12px;color:var(--gray-600)">${d.appointments || 0} navbat</div>
                </div>
                <div style="text-align:right">
                    <div style="font-size:13px;font-weight:700;color:var(--gray-700)">${d.specialty || 'Mutaxassis'}</div>
                </div>
                </div>`).join('');
        }
    }

    const ctxEl = document.getElementById('revenueChart');
    if (!ctxEl) return;
    if (revenueChart) revenueChart.destroy();

    // Parse daily stats from backend
    const dates = [];
    const revs = [];
    if (data.daily_stats && data.daily_stats.length > 0) {
        data.daily_stats.forEach(s => {
            const dateObj = new Date(s.date);
            dates.push(dateObj.toLocaleDateString(lang, { month: 'short', day: 'numeric' }));
            revs.push(s.revenue || 0);
        });
    }

    const ctx = ctxEl.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.2)');
    gradient.addColorStop(1, 'rgba(16, 185, 129, 0)');

    revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: "Daromad (so'm)",
                data: revs,
                borderColor: '#10B981',
                borderWidth: 3,
                backgroundColor: gradient,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#10B981',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.03)' }, border: { display: false } },
                x: { grid: { display: false }, border: { display: false } }
            }
        }
    });
}

async function loadBot() {
    if (!clinicId) await loadClinicId();
    const res = await apiFetch(`/clinics/${clinicId}/bot_stats/`);
    if (!res) return;

    document.getElementById('bot-users-count').textContent = res.bot_users;
    document.getElementById('bot-appt-count').textContent = res.bot_appts;
    document.getElementById('bot-visit-count').textContent = res.visits;
    document.getElementById('bot-rating').textContent = res.rating > 0 ? res.rating.toFixed(1) : '—';

    const badge = document.getElementById('bot-status-badge');
    badge.textContent = (res.status === 'active' || res.status === 'trial') ? 'Faol' : 'Nofaol';
    badge.className = 'badge ' + ((res.status === 'active' || res.status === 'trial') ? 'badge-green' : 'badge-gray');

    const linkEl = document.getElementById('share-link');
    linkEl.value = res.deep_link_url || (clinicId ? `https://t.me/ClinckoUzBot?start=clinic_${clinicId}` : '');
}

function copyLink() {
    const el = document.getElementById('share-link');
    if (!el.value || el.value.includes('Yuklanmoqda')) return;
    el.select();
    document.execCommand('copy');
    showToast('Havola ko\'chirildi!', 'success');
}

async function sendBroadcast() {
    const msg = document.getElementById('broadcast-msg').value;
    if (!msg) { showToast('Xabar matnini kiriting', 'error'); return; }

    if (!confirm('Barcha mijozlarga xabar yuborilsinmi?')) return;

    showToast('Xabar yuborilmoqda...', 'info');
    const res = await apiFetch(`/clinics/${clinicId}/send_broadcast/`, {
        method: 'POST',
        body: JSON.stringify({ message: msg })
    });

    if (res && res.sent !== undefined) {
        showToast(`Xabar yuborildi! (${res.sent} ta yetkazildi)`, 'success');
        document.getElementById('broadcast-msg').value = '';
    } else {
        showToast('Xatolik yuz berdi', 'error');
    }
}

async function downloadQR() {
    const link = document.getElementById('share-link').value;
    if (!link || link.includes('Yuklanmoqda')) { showToast('Havola tayyor emas', 'error'); return; }

    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        const clinicName = document.getElementById('sb-clinic-name').textContent || 'Klinika';

        showToast('PDF tayyorlanmoqda...', 'info');

        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=400x400&data=${encodeURIComponent(link)}`;
        const img = new Image();
        img.crossOrigin = "Anonymous";
        img.src = qrUrl;

        img.onload = () => {
            doc.setFontSize(22);
            doc.text(clinicName, 105, 40, { align: 'center' });

            doc.setFontSize(14);
            doc.text("Telegram Bot ro'yxatdan o'tish", 105, 50, { align: 'center' });

            doc.addImage(img, 'PNG', 55, 70, 100, 100);

            doc.setFontSize(11);
            doc.setTextColor(100);
            doc.text(link, 105, 185, { align: 'center' });
            doc.text("CLINKO Tizimi", 105, 280, { align: 'center' });

            doc.save(`QR_Code_${clinicName.replace(/\s+/g, '_')}.pdf`);
            showToast('PDF yuklab olindi!', 'success');
        };
        img.onerror = () => {
            showToast('QR Kod yuklashda xatolik yuz berdi', 'error');
        };
    } catch (e) {
        console.error(e);
        showToast('Kutubxona yuklanmadi. Qayta urinib ko\'ring.', 'error');
    }
}

// ═══════════════ APPOINTMENTS ═══════════════
async function loadAppointments(url = '/appointments/') {
    const status = g('appt-status-filter');
    let fetchUrl = url;
    if (status && !url.includes('status=')) {
        fetchUrl += (fetchUrl.includes('?') ? '&' : '?') + 'status=' + status;
    }
    const data = await apiFetch(fetchUrl);
    const list = data?.results || data || [];
    const tbody = document.getElementById('appt-tbody');
    if (!list.length) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty">Navbatlar topilmadi</td></tr>`;
        document.getElementById('appt-pagination').innerHTML = '';
        return;
    }

    tbody.innerHTML = list.map(a => `
    <tr>
      <td><div class="flex items-center gap-2"><div class="avatar">${(a.patient_name || '?')[0]}</div>${a.patient_name || '—'}</div></td>
      <td>${a.doctor_name || '—'}</td>
      <td>${a.date || '—'}</td>
      <td><strong>${a.time || '—'}</strong></td>
      <td>${a.service_name || '—'}</td>
      <td>${statusBadge(a.status)}</td>
      <td>${a.is_paid ? '<span class="badge badge-green"><i class="fas fa-check"></i> To\'langan</span>' : '<span class="badge badge-gray">Kutilmoqda</span>'}</td>
      <td>
        <div class="flex-gap">
          ${a.status === 'pending' ? `<button class="btn btn-success btn-sm" onclick="updateApptStatus('${a.id}','confirmed')"><i class="fas fa-check"></i></button>` : ''}
          ${a.status !== 'cancelled' && a.status !== 'completed' ? `<button class="btn btn-danger btn-sm" onclick="updateApptStatus('${a.id}','cancelled')"><i class="fas fa-times"></i></button>` : ''}
        </div>
      </td>
    </tr>`).join('');

    renderPagination('appt-pagination', data, loadAppointments);
}

function renderPagination(id, data, callback) {
    const container = document.getElementById(id);
    if (!container || !data || !data.count) {
        if (container) container.innerHTML = '';
        return;
    }

    const { count, next, previous } = data;
    container.innerHTML = `
        <div class="pagination-info">Jami: ${count} ta</div>
        <div class="pagination-btns">
            <button class="btn btn-outline btn-sm" ${!previous ? 'disabled' : ''} onclick="${callback.name}('${previous || ''}')">
                <i class="fas fa-chevron-left"></i> Oldingi
            </button>
            <button class="btn btn-outline btn-sm" ${!next ? 'disabled' : ''} onclick="${callback.name}('${next || ''}')">
                Keyingi <i class="fas fa-chevron-right"></i>
            </button>
        </div>
    `;
}

async function createAppointment() {
    const body = {
        doctor: g('appt-doctor-sel'),
        patient: g('appt-patient-sel'),
        date: g('appt-date'),
        time: g('appt-time-sel'),
        service: g('appt-service-sel') || null,
        clinic: clinicId
    };
    if (!body.doctor || !body.patient || !body.date || !body.time) { showToast('Barcha maydonlarni to\'ldiring', 'error'); return }

    const res = await apiFetch('/appointments/', { method: 'POST', body: JSON.stringify(body) });
    if (res) {
        showToast('Navbat yaratildi!', 'success');
        closeModal('appt');
        goPage('appointments');
    } else {
        showToast('Xato yuz berdi', 'error');
    }
}

async function updateApptStatus(id, status) {
    const res = await apiFetch('/appointments/' + id + '/update_status/', {
        method: 'POST', body: JSON.stringify({ status })
    });
    if (res) {
        showToast('Status yangilandi', 'success');
        if (document.getElementById('page-dashboard').classList.contains('active')) loadDashboard();
        else loadAppointments();
    }
}

// ═══════════════ DOCTORS ═══════════════
let allDoctors = [];
let currentEditDoctorId = null;

function showCredentialsModal(username, password) {
    if (!document.getElementById('modal-credentials')) {
        document.body.insertAdjacentHTML('beforeend', `
        <div class="modal-overlay" id="modal-credentials" style="z-index:99999;">
            <div class="modal" style="max-width:400px; text-align:center;">
                <div style="font-size:48px; color:var(--success); margin-bottom:15px;"><i class="fas fa-check-circle"></i></div>
                <h3 style="margin-bottom:10px; font-size:20px;">Shifokor profili ochildi!</h3>
                <p style="font-size:14px; color:var(--gray-500); margin-bottom:20px;">Shifokor ushbu ma'lumotlar orqali tizimga kirishi mumkin:</p>
                
                <div style="background:var(--gray-50); padding:15px; border-radius:12px; text-align:left; margin-bottom:20px; border:1px solid var(--gray-100)">
                    <div style="margin-bottom:10px;">
                        <span style="font-size:12px;color:var(--gray-500);display:block;">Login:</span>
                        <strong style="font-size:16px;color:var(--dark);" id="cred-login"></strong>
                    </div>
                    <div>
                        <span style="font-size:12px;color:var(--gray-500);display:block;">Vaqtinchalik parol:</span>
                        <strong style="font-size:16px;color:var(--dark);" id="cred-pass"></strong>
                    </div>
                </div>
                
                <button class="btn btn-primary" style="width:100%; justify-content:center;" onclick="document.getElementById('modal-credentials').classList.remove('active')">Tushunarli</button>
            </div>
        </div>`);
    }

    document.getElementById('cred-login').textContent = username;
    document.getElementById('cred-pass').textContent = password;
    document.getElementById('modal-credentials').classList.add('active');
}

async function loadDoctors() {
    const data = await apiFetch('/doctors/');
    const container = document.getElementById('doctors-grid');
    const list = data?.results || data || [];
    allDoctors = list;
    if (!list.length) {
        container.innerHTML = `<div class="empty" style="grid-column:1/-1"><i class="fas fa-user-md"></i><h3>Shifokorlar yo'q</h3><p>Birinchi shifokorni qo'shing</p></div>`;
        return;
    }
    container.innerHTML = list.map(d => `
    <div class="section-card" style="padding:28px; display:flex; flex-direction:column; height:100%;">
      <div style="display:flex; align-items:center; gap:20px; margin-bottom:24px">
        ${d.photo
            ? `<div class="avatar" style="min-width:64px;width:64px;height:64px;border-radius:18px;background-image:url(${d.photo.startsWith('http') ? d.photo : API.replace('/api/v1', '') + d.photo});background-size:cover;background-position:center;box-shadow:0 4px 12px rgba(99,102,241,0.2);"></div>`
            : `<div class="avatar" style="display:flex;align-items:center;justify-content:center;min-width:64px;width:64px;height:64px;font-size:32px;border-radius:18px;background:var(--primary);color:#fff;text-transform:uppercase;font-weight:700;box-shadow:0 4px 12px rgba(99,102,241,0.2);">${(d.first_name || 'D')[0]}</div>`
        }
        <div style="flex:1; min-width:0;">
          <div style="font-weight:800;font-size:18px;color:var(--dark);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${d.first_name || ''} ${d.last_name || ''}">${d.first_name || ''} ${d.last_name || ''}</div>
          <div style="font-size:14px;color:var(--primary);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${d.specialty || '—'}</div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:24px; flex-grow:1;">
        <div style="font-size:13px;color:var(--gray-600);display:flex;align-items:center;gap:8px;"><i class="fas fa-phone" style="width:16px;color:var(--primary);text-align:center;"></i> <span>${d.phone || '—'}</span></div>
        <div style="font-size:13px;color:var(--gray-600);display:flex;align-items:center;gap:8px;"><i class="fas fa-briefcase" style="width:16px;color:var(--primary);text-align:center;"></i> <span>${d.experience_years || 0} yil tajriba</span></div>
        <div style="font-size:13px;color:var(--gray-600);display:flex;align-items:center;gap:8px;"><i class="fas fa-money-bill" style="width:16px;color:var(--primary);text-align:center;"></i> <span>${Number(d.consultation_price || 0).toLocaleString()} so'm</span></div>
      </div>
      <div style="display:flex; align-items:center; justify-content:space-between; margin-top:auto; padding-top:16px; border-top:1px solid var(--gray-100)">
        <span onclick="toggleDoctorStatus('${d.id}', ${d.is_active})" class="badge ${d.is_active ? 'badge-green' : 'badge-gray'}" style="display:inline-flex; align-items:center; justify-content:center; padding:6px 12px; font-weight:700; font-size:11px; cursor:pointer;" title="Holatni o'zgartirish">${d.is_active ? 'Faol' : 'Nofaol'}</span>
        <div style="display:flex; gap:8px;">
            <button class="btn btn-outline btn-sm" style="display:inline-flex; align-items:center; padding:8px 12px;" onclick="editDoctor('${d.id}')"><i class="fas fa-pen"></i></button>
            <button class="btn btn-outline btn-sm" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; font-size:13px;" onclick="viewDoctor('${d.id}')">Profil <i class="fas fa-arrow-right"></i></button>
        </div>
      </div>
    </div>`).join('');
}

function editDoctor(id) {
    const d = allDoctors.find(x => x.id == id);
    if (!d) return;
    openModal('doctor', true);
    currentEditDoctorId = id;
    document.getElementById('doc-fname').value = d.first_name || '';
    document.getElementById('doc-lname').value = d.last_name || '';
    document.getElementById('doc-specialty').value = d.specialty || '';
    document.getElementById('doc-phone').value = d.phone || '';
    document.getElementById('doc-exp').value = d.experience_years || 0;
    document.getElementById('doc-price').value = parseInt(d.consultation_price) || 0;
    document.getElementById('doc-bio').value = d.bio || '';
    document.getElementById('doc-edu').value = d.education || '';
    document.getElementById('doc-achievements').value = d.achievements || '';
}

function viewDoctor(id) {
    const d = allDoctors.find(x => x.id == id);
    if (!d) return;

    const photoUrl = d.photo ? (d.photo.startsWith('http') ? d.photo : API.replace('/api/v1', '') + d.photo) : '';
    const avatarHtml = photoUrl
        ? `<div style="width:100px; height:100px; border-radius:30px; background-image:url(${photoUrl}); background-size:cover; background-position:center; margin: 0 auto; box-shadow:0 10px 25px rgba(99,102,241,0.3);"></div>`
        : `<div style="width:100px; height:100px; border-radius:30px; background:var(--primary); color:#fff; display:flex; align-items:center; justify-content:center; font-size:40px; font-weight:800; margin: 0 auto; box-shadow:0 10px 25px rgba(99,102,241,0.3);">${(d.first_name || 'D')[0]}</div>`;

    document.getElementById('doctor-profile-content').innerHTML = `
        <div style="text-align:center; margin-bottom: 24px;">
            ${avatarHtml}
            <h3 style="margin-top: 16px; font-size: 22px; color: var(--dark);">${d.first_name || ''} ${d.last_name || ''}</h3>
            <div style="color: var(--primary); font-weight:600; font-size: 15px;">${d.specialty || '—'}</div>
        </div>
        
        <div style="display:flex; flex-direction:column; gap:12px;">
            <div style="background:var(--gray-50); padding: 12px 16px; border-radius: 12px; display:flex; align-items:center; gap: 12px;">
                <div style="width: 36px; height: 36px; border-radius: 10px; background:var(--primary-light); color:var(--primary); display:flex; align-items:center; justify-content:center;"><i class="fas fa-phone"></i></div>
                <div>
                    <div style="font-size:12px; color:var(--gray-500); font-weight:600;">Telefon</div>
                    <div style="font-weight:600; color:var(--dark);">${d.phone || '—'}</div>
                </div>
            </div>
            
            <div style="display:flex; gap:12px;">
                <div style="flex:1; background:var(--gray-50); padding: 12px 16px; border-radius: 12px; display:flex; align-items:center; gap: 12px;">
                    <div style="width: 36px; height: 36px; border-radius: 10px; background:#f0fdf4; color:#16a34a; display:flex; align-items:center; justify-content:center;"><i class="fas fa-briefcase"></i></div>
                    <div>
                        <div style="font-size:12px; color:var(--gray-500); font-weight:600;">Tajriba</div>
                        <div style="font-weight:600; color:var(--dark);">${d.experience_years || 0} yil</div>
                    </div>
                </div>
                <div style="flex:1; background:var(--gray-50); padding: 12px 16px; border-radius: 12px; display:flex; align-items:center; gap: 12px;">
                    <div style="width: 36px; height: 36px; border-radius: 10px; background:#eef2ff; color:var(--primary); display:flex; align-items:center; justify-content:center;"><i class="fas fa-money-bill"></i></div>
                    <div>
                        <div style="font-size:12px; color:var(--gray-500); font-weight:600;">Narxi</div>
                        <div style="font-weight:600; color:var(--dark);">${Number(d.consultation_price || 0).toLocaleString()} so'm</div>
                    </div>
                </div>
            </div>
            
            ${d.bio ? `<div style="margin-top: 8px;">
                <div style="font-weight:700; color:var(--dark); margin-bottom:6px; font-size:14px;">Shifokor haqida</div>
                <div style="font-size:14px; color:var(--gray-600); line-height:1.5;">${d.bio}</div>
            </div>` : ''}
            
            ${d.education ? `<div style="margin-top: 8px;">
                <div style="font-weight:700; color:var(--dark); margin-bottom:6px; font-size:14px;">Ta'lim</div>
                <div style="font-size:14px; color:var(--gray-600); line-height:1.5;">${d.education}</div>
            </div>` : ''}
            
            ${d.achievements ? `<div style="margin-top: 8px;">
                <div style="font-weight:700; color:var(--dark); margin-bottom:6px; font-size:14px;">Yutuqlar</div>
                <div style="font-size:14px; color:var(--gray-600); line-height:1.5;">${d.achievements}</div>
            </div>` : ''}
        </div>
    `;

    openModal('doctor-profile');
}

async function toggleDoctorStatus(id, currentStatus) {
    if (!confirm("Shifokor holatini o'zgartirmoqchimisiz?")) return;
    const res = await apiFetch(`/doctors/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify({ is_active: !currentStatus })
    });
    if (res) {
        showToast('Holat muvaffaqiyatli saqlandi', 'success');
        loadDoctors();
    }
}
async function createDoctor() {
    if (!g('doc-fname') || !g('doc-specialty')) {
        showToast('Ism va mutaxassislik majburiy (yulduzcha bilan belgilangan)', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('first_name', g('doc-fname'));
    formData.append('last_name', g('doc-lname'));
    formData.append('specialty', g('doc-specialty'));
    formData.append('phone', g('doc-phone'));
    formData.append('experience_years', parseInt(g('doc-exp')) || 0);
    formData.append('consultation_price', parseInt(g('doc-price')) || 0);
    formData.append('bio', g('doc-bio'));
    formData.append('education', g('doc-edu'));
    formData.append('achievements', g('doc-achievements'));
    formData.append('clinic', clinicId);

    const checkLogin = document.getElementById('doc-create-login');
    if (checkLogin && checkLogin.checked && !currentEditDoctorId) {
        formData.append('create_login', 'true');
    }

    const fileInput = document.getElementById('doc-photo');
    if (fileInput && fileInput.files.length > 0) {
        formData.append('photo', fileInput.files[0]);
    }

    const url = currentEditDoctorId ? `/doctors/${currentEditDoctorId}/` : '/doctors/';
    const method = currentEditDoctorId ? 'PUT' : 'POST';

    const res = await fetch((API.endsWith('/') ? API.slice(0, -1) : API) + url, {
        method: method,
        headers: { 'Authorization': 'Bearer ' + token() },
        body: formData
    });

    if (res.ok) {
        const data = await res.json();
        showToast(currentEditDoctorId ? 'Shifokor tahrirlandi!' : 'Shifokor muvaffaqiyatli qo\'shildi!', 'success');
        closeModal('doctor');
        currentEditDoctorId = null;
        loadDoctors();

        if (data.generated_username && data.generated_password) {
            showCredentialsModal(data.generated_username, data.generated_password);
        }
    } else {
        const data = await res.json().catch(() => ({}));
        showToast('Saqlashda xatolik yuz berdi: ' + (data.detail || JSON.stringify(data)), 'error');
    }
}

// ═══════════════ PATIENTS ═══════════════
let currentEditPatientId = null;

async function loadPatients(url = '/patients/') {
    const data = await apiFetch(url);
    allPatients = data?.results || data || [];
    renderPatients(allPatients);
    renderPagination('patient-pagination', data, loadPatients);
}
function renderPatients(list) {
    const tbody = document.getElementById('patients-tbody');
    if (!list.length) { tbody.innerHTML = `<tr><td colspan="6" class="empty">Bemorlar topilmadi</td></tr>`; return }
    tbody.innerHTML = list.map(p => `
    <tr>
      <td><div class="flex items-center gap-2"><div class="avatar">${(p.first_name || '?')[0]}</div>${p.first_name || ''} ${p.last_name || ''}</div></td>
      <td>${p.phone || '—'}</td>
      <td>${p.date_of_birth || '—'}</td>
      <td>${p.gender === 'M' ? 'Erkak' : p.gender === 'F' ? 'Ayol' : '—'}</td>
      <td><span class="badge badge-blue">${p.total_appointments || 0}</span></td>
      <td>
        <button class="btn btn-outline btn-sm" onclick="editPatient('${p.id}')"><i class="fas fa-pen"></i></button>
        <button class="btn btn-outline btn-sm"><i class="fas fa-eye"></i></button>
      </td>
    </tr>`).join('');
}
function filterPatients(q) { renderPatients(allPatients.filter(p => (p.first_name + ' ' + p.last_name + ' ' + (p.phone || '')).toLowerCase().includes(q.toLowerCase()))) }

function editPatient(id) {
    const p = allPatients.find(x => x.id == id);
    if (!p) return;
    openModal('patient', true);
    currentEditPatientId = id;
    document.getElementById('pat-fname').value = p.first_name || '';
    document.getElementById('pat-lname').value = p.last_name || '';
    document.getElementById('pat-phone').value = p.phone || '';
    document.getElementById('pat-dob').value = p.date_of_birth || '';
    document.getElementById('pat-gender').value = p.gender || '';
}


async function createPatient() {
    const body = { first_name: g('pat-fname'), last_name: g('pat-lname'), phone: g('pat-phone'), date_of_birth: g('pat-dob') || null, gender: g('pat-gender'), clinic: clinicId };
    if (!body.first_name || !body.phone) { showToast('Ism va telefon kiriting', 'error'); return }

    const url = currentEditPatientId ? `/patients/${currentEditPatientId}/` : '/patients/';
    const method = currentEditPatientId ? 'PUT' : 'POST';

    const res = await apiFetch(url, { method: method, body: JSON.stringify(body) });
    if (res) { showToast(currentEditPatientId ? 'Bemor tahrirlandi!' : 'Bemor qo\'shildi!', 'success'); currentEditPatientId = null; closeModal('patient'); loadPatients(); }
}

// ═══════════════ SERVICES ═══════════════
let allServices = [];
let currentEditServiceId = null;

async function loadServices() {
    if (!clinicId) return;
    const data = await apiFetch('/clinics/' + clinicId + '/services/');
    allServices = data?.results || data || [];
    const tbody = document.getElementById('services-tbody');
    if (!tbody) return;
    if (!allServices.length) { tbody.innerHTML = `<tr><td colspan="5" class="empty">Xizmatlar topilmadi</td></tr>`; return; }

    tbody.innerHTML = allServices.map(s => `
    <tr>
        <td style="font-weight:600">${s.name}</td>
        <td>${s.duration_minutes} daqiqa</td>
        <td>${parseInt(s.price || 0).toLocaleString()} so'm</td>
        <td><span onclick="toggleServiceStatus('${s.id}', ${s.is_active})" class="badge ${s.is_active ? 'badge-green' : 'badge-gray'}" style="cursor:pointer;" title="Holatni o'zgartirish">${s.is_active ? 'Faol' : 'Nofaol'}</span></td>
        <td>
            <button class="btn btn-outline btn-sm" onclick="editService('${s.id}')"><i class="fas fa-pen"></i></button>
        </td>
    </tr>
    `).join('');
}

function editService(id) {
    const s = allServices.find(x => x.id == id);
    if (!s) return;
    openModal('service', true);
    currentEditServiceId = id;
    document.getElementById('svc-name').value = s.name || '';
    document.getElementById('svc-price').value = parseInt(s.price) || 0;
    document.getElementById('svc-duration').value = s.duration_minutes || s.duration || 30;
    document.getElementById('svc-desc').value = s.description || '';
}

async function createService() {
    if (!clinicId) return;
    const body = {
        name: g('svc-name'),
        price: parseInt(g('svc-price')) || 0,
        duration: parseInt(g('svc-duration')) || 30,
        description: g('svc-desc')
    };
    if (!body.name) { showToast('Xizmat nomini kiriting', 'error'); return; }

    const url = currentEditServiceId ? `/clinics/${clinicId}/services/${currentEditServiceId}/` : `/clinics/${clinicId}/services/`;
    const method = currentEditServiceId ? 'PUT' : 'POST';

    const res = await apiFetch(url, { method: method, body: JSON.stringify(body) });
    if (res) {
        showToast(currentEditServiceId ? 'Xizmat tahrirlandi!' : 'Xizmat saqlandi!', 'success');
        currentEditServiceId = null;
        closeModal('service');
        loadServices();
    }
}

// ═══════════════ STAFF (ADMINS) ═══════════════
async function loadStaff() {
    if (!clinicId) return;
    const body = document.getElementById('staff-tbody');
    if (!body) return;

    // Using standard fetch since this is a new endpoint
    const res = await apiFetch(`/clinics/${clinicId}/staff/`);
    const staffList = res || [];

    if (!staffList.length) {
        body.innerHTML = `<tr><td colspan="4" class="empty">Xodimlar topilmadi</td></tr>`;
        return;
    }

    body.innerHTML = staffList.map(s => `
        <tr class="hover-row">
            <td>
                <div class="flex items-center gap-3">
                    <div class="avatar" style="background:var(--primary-light);color:var(--white);font-weight:700;">${(s.first_name || 'X')[0]}</div>
                    <div>
                        <div style="font-weight:700; color:var(--dark); font-size:14px;">${s.first_name || ''} ${s.last_name || ''}</div>
                        <div style="font-size:11px;color:var(--gray-400);">ID: ${s.id?.slice(0, 8) || ''}</div>
                    </div>
                </div>
            </td>
            <td><code style="background:var(--gray-50);padding:2px 6px;border-radius:4px;color:var(--primary);font-size:12px;">@${s.username || ''}</code></td>
            <td style="font-size:13px;color:var(--gray-600);"><i class="fas fa-phone-alt" style="margin-right:6px;opacity:0.5;"></i> ${s.phone || '—'}</td>
            <td><span class="badge ${s.role === 'Asoschi' ? 'badge-blue' : 'badge-green'}"><i class="fas ${s.role === 'Asoschi' ? 'fa-crown' : 'fa-user-tie'}"></i> ${s.role || 'Admin'}</span></td>
            <td style="text-align:right;">
                <button class="btn btn-outline btn-sm action-btn" onclick="editStaffPassword('${s.id}', '${s.username}')" title="Parolni o'zgartirish">
                    <i class="fas fa-key" style="color:var(--warning)"></i>
                </button>
                <button class="btn btn-outline btn-sm action-btn" onclick="deleteStaff('${s.id}')" title="O'chirish">
                    <i class="fas fa-trash-alt" style="color:var(--danger)"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

async function createStaff() {
    if (!clinicId) return;
    const body = {
        first_name: g('stf-fname'),
        last_name: g('stf-lname'),
        phone: g('stf-phone'),
        username: g('stf-username'),
        password: g('stf-password')
    };

    if (!body.first_name || !body.username || !body.password) {
        showToast('Ism, login va parol majburiy!', 'error');
        return;
    }

    if (body.password.length < 8) {
        showToast("Parol kamida 8 ta belgi bo'lishi kerak!", 'error');
        return;
    }

    const btn = document.querySelector('#modal-staff .btn-primary');
    const oldHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Kuting...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API.endsWith('/') ? API.slice(0, -1) : API}/clinics/${clinicId}/staff/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });

        const data = await res.json();

        if (res.ok) {
            showToast("Yangi xodim qo'shildi!", 'success');
            closeModal('staff');
            loadStaff();
        } else {
            showToast(data.error || 'Xatolik yuz berdi. Balki login banddir?', 'error');
        }
    } catch (e) {
        showToast('Server bilan xatolik!', 'error');
    } finally {
        btn.innerHTML = oldHtml;
        btn.disabled = false;
    }
}

async function deleteStaff(id) {
    if (!confirm("Haqiqatan ham bu xodimni o'chirmoqchimisiz?")) return;
    try {
        const res = await apiFetch(`/clinics/${clinicId}/staff/${id}/`, { method: 'DELETE' });
        showToast('Xodim o\'chirildi', 'success');
        loadStaff();
    } catch (e) {
        showToast('Xatolik yuz berdi', 'error');
    }
}

let currentEditStaffId = null;

async function editStaffPassword(id, username) {
    currentEditStaffId = id;
    document.getElementById('edit-staff-username').value = username;
    document.getElementById('edit-staff-name').value = username; // You can enhance this to show full name
    document.getElementById('edit-staff-password').value = '';
    document.getElementById('edit-staff-password-confirm').value = '';
    openModal('edit-password');
}

async function updateStaffPassword() {
    const password = document.getElementById('edit-staff-password').value;
    const confirmPassword = document.getElementById('edit-staff-password-confirm').value;

    if (!password || !confirmPassword) {
        showToast('Ikkala maydonni ham to\'ldiring', 'error');
        return;
    }

    if (password.length < 8) {
        showToast('Parol kamida 8 ta belgi bo\'lishi kerak!', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showToast('Parollar mos kelmadi!', 'error');
        return;
    }

    const btn = document.querySelector('#modal-edit-password .btn-primary');
    const oldHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Kuting...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API.endsWith('/') ? API.slice(0, -1) : API}/clinics/${clinicId}/staff/${currentEditStaffId}/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
        });

        if (res.ok) {
            showToast('Parol muvaffaqiyatli o\'zgartirildi!', 'success');
            closeModal('edit-password');
            loadStaff();
        } else {
            const data = await res.json();
            showToast(data.error || 'Xatolik yuz berdi', 'error');
        }
    } catch (e) {
        showToast('Server bilan xatolik!', 'error');
    } finally {
        btn.innerHTML = oldHtml;
        btn.disabled = false;
    }
}

async function toggleServiceStatus(id, currentStatus) {
    if (!confirm("Xizmat holatini o'zgartirmoqchimisiz?")) return;
    const res = await apiFetch(`/clinics/${clinicId}/services/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify({ is_active: !currentStatus })
    });
    if (res) {
        showToast('Holat muvaffaqiyatli saqlandi', 'success');
        loadServices();
    }
}

// ═══════════════ ANALYTICS ═══════════════
function g(id) { return document.getElementById(id)?.value || '' }
function statusBadge(s) {
    const map = { pending: 'badge-yellow', confirmed: 'badge-blue', completed: 'badge-green', cancelled: 'badge-red', no_show: 'badge-gray' };
    const labels = { pending: 'Kutilmoqda', confirmed: 'Tasdiqlangan', completed: 'Tugallangan', cancelled: 'Bekor', no_show: 'Kelmadi' };
    return `<span class="badge ${map[s] || 'badge-gray'}">${labels[s] || s}</span>`;
}
function showToast(msg, type = '') {
    const t = document.getElementById('toast');
    t.querySelector('#toast-msg').textContent = msg;
    t.className = 'toast show ' + type;
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.remove('show'), 3000);
}

async function loadClinicId() {
    const data = await apiFetch('/clinics/');
    const list = data?.results || data || [];
    if (list.length) {
        clinicId = list[0].id;
        document.getElementById('sb-clinic-name').textContent = list[0].name;
        document.getElementById('sb-plan').textContent = list[0].subscription_plan_display || 'Sinov';
    }
}

// ═══════════════ SETTINGS ═══════════════
async function loadSettings() {
    if (!clinicId) await loadClinicId();
    const c = await apiFetch('/clinics/' + clinicId + '/');
    if (!c) return;

    document.getElementById('s-clinic-name').value = c.name || '';
    document.getElementById('s-clinic-phone').value = c.phone || '';
    document.getElementById('s-clinic-city').value = c.city || '';
    document.getElementById('s-clinic-email').value = c.email || '';
    document.getElementById('s-clinic-address').value = c.address || '';
    document.getElementById('s-clinic-lat').value = c.latitude || '';
    document.getElementById('s-clinic-lng').value = c.longitude || '';
    document.getElementById('s-work-start').value = c.work_start || '09:00';
    document.getElementById('s-work-end').value = c.work_end || '18:00';

    // Show current images if they exist
    const serverUrl = API.replace('/api/v1', '');
    if (c.logo) {
        const logoPreview = document.getElementById('s-clinic-logo-preview');
        logoPreview.src = c.logo.startsWith('http') ? c.logo : serverUrl + c.logo;
        logoPreview.style.display = 'block';
    }
    if (c.cover_image) {
        const coverPreview = document.getElementById('s-clinic-cover-preview');
        coverPreview.src = c.cover_image.startsWith('http') ? c.cover_image : serverUrl + c.cover_image;
        coverPreview.style.display = 'block';
    }
}

function previewFile(input, previewId) {
    const preview = document.getElementById(previewId);
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

async function saveSettings() {
    const fd = new FormData();
    fd.append('name', g('s-clinic-name'));
    fd.append('phone', g('s-clinic-phone'));
    fd.append('city', g('s-clinic-city'));
    fd.append('email', g('s-clinic-email'));
    fd.append('address', g('s-clinic-address'));
    fd.append('latitude', g('s-clinic-lat'));
    fd.append('longitude', g('s-clinic-lng'));
    fd.append('work_start', g('s-work-start'));
    fd.append('work_end', g('s-work-end'));

    const logo = document.getElementById('s-clinic-logo-file').files[0];
    const cover = document.getElementById('s-clinic-cover-file').files[0];
    if (logo) fd.append('logo', logo);
    if (cover) fd.append('cover_image', cover);

    const res = await apiFetch('/clinics/' + clinicId + '/', {
        method: 'PATCH',
        body: fd
    });

    if (res) {
        showToast('Sozlamalar saqlandi!', 'success');
        document.getElementById('sb-clinic-name').textContent = res.name;
        // Clear file inputs
        document.getElementById('s-clinic-logo-file').value = '';
        document.getElementById('s-clinic-cover-file').value = '';
    } else {
        showToast('Xatolik yuz berdi', 'error');
    }
}

function autoDetectLocation() {
    if (!navigator.geolocation) {
        showToast("Brauzeringiz geolokatsiyani qo'llab-quvvatlamaydi", "error");
        return;
    }
    showToast("Joylashuv aniqlanmoqda...", "info");
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            document.getElementById('s-clinic-lat').value = pos.coords.latitude.toFixed(6);
            document.getElementById('s-clinic-lng').value = pos.coords.longitude.toFixed(6);
            showToast("Joylashuv aniqlandi!", "success");
        },
        (err) => {
            console.error(err);
            showToast("Ruxsat berilmadi yoki xatolik yuz berdi", "error");
        }
    );
}

async function loadApptSelects() {
    const [docsRaw, patsRaw, svcsRaw] = await Promise.all([apiFetch('/doctors/'), apiFetch('/patients/'), apiFetch('/clinics/' + clinicId + '/services/')]);

    // Check if the response is paginated or returning a direct array.
    const docs = docsRaw?.results || docsRaw || [];
    const pats = patsRaw?.results || patsRaw || [];
    const svcs = svcsRaw?.results || svcsRaw || [];

    document.getElementById('appt-doctor-sel').innerHTML = docs.map(d => `<option value="${d.id}">${d.first_name} ${d.last_name}</option>`).join('');
    document.getElementById('appt-patient-sel').innerHTML = pats.map(p => `<option value="${p.id}">${p.first_name} ${p.last_name}</option>`).join('');
    document.getElementById('appt-service-sel').innerHTML = '<option value="">Xizmat tanlang...</option>' + svcs.map(s => `<option value="${s.id}">${s.name} (${(s.price || 0).toLocaleString()} so'm)</option>`).join('');
    document.getElementById('appt-date').value = new Date().toISOString().slice(0, 10);
}

// ═══════════════ INIT ═══════════════
async function init() {
    if (!token()) { window.location.href = 'login.html'; return }
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    document.getElementById('sb-username').textContent = user.username || 'Admin';
    document.getElementById('sb-avatar').textContent = (user.username || 'A')[0].toUpperCase();
    setLang(lang);
    await loadClinicId();
    loadDashboard();
}
init();
