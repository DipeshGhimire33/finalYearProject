/* ================= UPDATE FEATURE BLOCK ================= */

function updateRatingFeatureBlock() {

    const comments = JSON.parse(localStorage.getItem("comments")) || [];

    const avgEl = document.getElementById("averageRating");
    const topTextEl = document.getElementById("topReviewText");
    const topReviewerEl = document.getElementById("topReviewer");

    if (!avgEl || !topTextEl || !topReviewerEl) return;

    if (comments.length === 0) {
        avgEl.textContent = "0";
        topTextEl.textContent = "No reviews yet.";
        topReviewerEl.textContent = "";
        return;
    }

    // Calculate average
    const total = comments.reduce((sum, c) => sum + Number(c.rating), 0);
    const average = (total / comments.length).toFixed(1);

    avgEl.textContent = average;

    // Find highest rated comment
    const topComment = comments.reduce((prev, current) => 
        (current.rating > prev.rating) ? current : prev
    );

    topTextEl.textContent = `"${topComment.text}"`;
    topReviewerEl.textContent = `– ${topComment.name}`;
}

// Call on page load
document.addEventListener("DOMContentLoaded", updateRatingFeatureBlock);
