// Initialize charts after DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  // Income vs Expense Chart
  const incomeExpenseCanvas = document.getElementById("incomeExpenseChart");
  if (incomeExpenseCanvas) {
    new Chart(incomeExpenseCanvas.getContext("2d"), {
      type: "bar",
      data: {
        labels: ["Income", "Expenses"],
        datasets: [
          {
            label: "Ksh",
            data: window.analyticsData.incomeExpense,
            backgroundColor: ["#198754", "#dc3545"],
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  // Spending by Category Chart
  const categoryCanvas = document.getElementById("categoryChart");
  if (categoryCanvas) {
    new Chart(categoryCanvas.getContext("2d"), {
      type: "pie",
      data: {
        labels: window.analyticsData.categories,
        datasets: [
          {
            data: window.analyticsData.categoryAmounts,
            backgroundColor: [
              "#007bff", "#6610f2", "#6f42c1", "#d63384",
              "#dc3545", "#fd7e14", "#ffc107", "#198754",
              "#20c997", "#0dcaf0",
            ],
          },
        ],
      },
      options: {
        responsive: true,
      },
    });
  }

  // spending over time chart
const ctx3 = document.getElementById("timeChart");
    if (ctx3 && window.analyticsData.dates.length) {
        new Chart(ctx3, {
            type: "line",
            data: {
                labels: window.analyticsData.dates,
                datasets: [{
                    label: "Net Spending (Ksh)",
                    data: window.analyticsData.dailyTotals,
                    borderColor: "rgba(13, 110, 253, 0.1)",
                    fill: true,
                    tension: 0.3,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    x: { title: { display: true, text: "Date" } },
                    y: { title: { display: true, text: "Amount (Ksh)"} }
                }
            }
        });
    }

});


