
const API_BASE = window.CAREER_RADAR_CONFIG.fastapiBaseUrl;

let salaryChart, demandChart, skillsChart, citiesChart;

async function fetchJSON(path, params = {}) {
    const url = new URL(`${API_BASE}${path}`);
    Object.entries(params).forEach(([k, v]) => {
        if (v) url.searchParams.set(k, v);
    });
    const res = await fetch(url);
    if (!res.ok) return null;
    return res.json();
}

function upsertChart(existing, ctx, config) {
    if (existing) {
        existing.data = config.data;
        existing.update();
        return existing;
    }
    return new Chart(ctx, config);
}

async function renderDemandTrend(filters) {
    const data = await fetchJSON("/analytics/demand-trend", { ...filters, weeks: 12 }) || [];
    const ctx = document.getElementById("demandChart");
    demandChart = upsertChart(demandChart, ctx, {
        type: "line",
        data: {
            labels: data.map(d => d.week_start),
            datasets: [{
                label: "Вакансий в неделю",
                data: data.map(d => d.vacancy_count),
                borderColor: "#5b7fff",
                tension: 0.3,
            }],
        },
        options: { plugins: { legend: { display: false } } },
    });
}

async function renderSalaryOverTime(filters) {
    // Reuses the demand-trend endpoint's weekly buckets as x-axis labels,
    // paired with a single current salary snapshot per week isn't available
    // from the API yet, so we show the current median as a flat reference
    // line against vacancy counts for context.
    const stats = await fetchJSON("/analytics/salary", filters);
    const trend = await fetchJSON("/analytics/demand-trend", { ...filters, weeks: 12 }) || [];
    const ctx = document.getElementById("salaryChart");
    salaryChart = upsertChart(salaryChart, ctx, {
        type: "bar",
        data: {
            labels: trend.map(d => d.week_start),
            datasets: [{
                label: "Медианная ЗП (текущая)",
                data: trend.map(() => stats ? stats.median_salary : 0),
                backgroundColor: "#3ddc97",
            }],
        },
    });
}

async function renderTopSkills(filters) {
    const data = await fetchJSON("/analytics/top-skills", { position: filters.skill, limit: 8 }) || [];
    const ctx = document.getElementById("skillsChart");
    skillsChart = upsertChart(skillsChart, ctx, {
        type: "bar",
        data: {
            labels: data.map(d => d.skill),
            datasets: [{
                label: "% вакансий",
                data: data.map(d => d.percent_of_total),
                backgroundColor: "#f5a623",
            }],
        },
        options: { indexAxis: "y" },
    });
}

async function renderCities() {
    // Simple client-side breakdown: hit demand-trend once per known city.
    // For a small demo set of cities; a dedicated /analytics/cities
    // endpoint would be the next iteration.
    const cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург"];
    const counts = await Promise.all(
        cities.map(city => fetchJSON("/analytics/demand-trend", { city, weeks: 4 }))
    );
    const totals = counts.map(rows => (rows || []).reduce((sum, r) => sum + r.vacancy_count, 0));

    const ctx = document.getElementById("citiesChart");
    citiesChart = upsertChart(citiesChart, ctx, {
        type: "doughnut",
        data: {
            labels: cities,
            datasets: [{ data: totals, backgroundColor: ["#5b7fff", "#3ddc97", "#f5a623", "#e85d75"] }],
        },
    });
}

function getFilters() {
    return {
        skill: document.getElementById("filter-skill").value.trim(),
        city: document.getElementById("filter-city").value.trim(),
    };
}

async function renderAll() {
    const filters = getFilters();
    await Promise.all([
        renderDemandTrend(filters),
        renderSalaryOverTime(filters),
        renderTopSkills(filters),
        renderCities(),
    ]);
}

document.getElementById("apply-filters").addEventListener("click", renderAll);
renderAll();
