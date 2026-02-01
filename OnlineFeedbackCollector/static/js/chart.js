console.log("chart.js file loaded");

document.addEventListener("DOMContentLoaded", function () {

    const canvas = document.getElementById("ratingChart");

    if (!canvas) {
        console.error("Canvas not found");
        return;
    }

    const labels = JSON.parse(canvas.dataset.labels);
    const counts = JSON.parse(canvas.dataset.counts);

    console.log("Labels:", labels);
    console.log("Counts:", counts);

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Number of Feedbacks",
                data: counts,
                backgroundColor: "rgba(75, 192, 192, 0.7)"
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
