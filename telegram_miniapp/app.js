
const tg = window.Telegram?.WebApp;
if (tg) {
    tg.ready();
    tg.expand();
}

async function fetchJSON(path, params = {}) {
    const url = new URL(path, window.location.origin);
    Object.entries(params).forEach(([k, v]) => v && url.searchParams.set(k, v));
    const res = await fetch(url);
    if (!res.ok) return null;
    return res.json();
}

async function render() {
    const salary = await fetchJSON("/analytics-api/analytics/salary");
    if (salary && salary.median_salary) {
        document.getElementById("median-salary").textContent =
            `${Math.round(salary.median_salary).toLocaleString("ru-RU")} ₽`;
    }

    const trend = await fetchJSON("/analytics-api/analytics/demand-trend", { weeks: 8 }) || [];
    if (trend.length) {
        document.getElementById("weekly-count").textContent = trend[trend.length - 1].vacancy_count;
    }

    new Chart(document.getElementById("trendChart"), {
        type: "line",
        data: {
            labels: trend.map(d => d.week_start),
            datasets: [{
                data: trend.map(d => d.vacancy_count),
                borderColor: "#5b7fff",
                tension: 0.3,
                pointRadius: 0,
            }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { x: { display: false } },
        },
    });

    const skills = await fetchJSON("/analytics-api/analytics/top-skills", { limit: 6 }) || [];
    const list = document.getElementById("skills-list");
    list.innerHTML = skills.map(s => `<li><span>${s.skill}</span><span>${s.percent_of_total}%</span></li>`).join("");
}

render();
