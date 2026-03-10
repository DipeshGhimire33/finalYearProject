document.addEventListener("DOMContentLoaded", function () {

    const bookingModal = document.getElementById("bookingModal");
    const confirmModal = document.getElementById("confirmModal");

    const openBtn = document.querySelector(".book-now-btn");
    const closeBtn = document.querySelector(".close-modal");
    const cancelBtn = document.querySelector(".cancel-btn");

    const form = document.getElementById("bookingForm");
    const confirmDetails = document.getElementById("confirmDetails");

    const confirmBtn = document.querySelector(".confirm-btn");
    const backBtn = document.querySelector(".back-btn");

    if (!bookingModal || !openBtn) return;

    // Open booking modal
    openBtn.addEventListener("click", () => {
        bookingModal.style.display = "flex";
    });

    // Close booking modal
    function closeBooking() {
        bookingModal.style.display = "none";
    }

    closeBtn.addEventListener("click", closeBooking);
    cancelBtn.addEventListener("click", closeBooking);

    bookingModal.addEventListener("click", function (e) {
        if (e.target === bookingModal) closeBooking();
    });

    // Submit form (Step 1)
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const data = {
            fullname: form.fullname.value,
            email: form.email.value,
            pickup: form.pickup.value,
            destination: form.destination.value,
            people: form.people.value,
            days: form.days.value
        };

        // Show confirmation details
        confirmDetails.innerHTML = `
            <strong>Full Name:</strong> ${data.fullname} <br>
            <strong>Email:</strong> ${data.email} <br>
            <strong>Pickup Location:</strong> ${data.pickup} <br>
            <strong>Destination:</strong> ${data.destination} <br>
            <strong>No. of People:</strong> ${data.people} <br>
            <strong>No. of Tour Days:</strong> ${data.days}
        `;

        confirmModal.style.display = "flex";
    });

    // Confirm submission (Step 2)
    confirmBtn.addEventListener("click", function () {
        confirmModal.style.display = "none";
        bookingModal.style.display = "none";

        alert("Booking Confirmed Successfully!");

        form.reset();

        // Here is where you connect to Django backend later
        // form.submit();  <-- uncomment when backend is ready
    });

    // Cancel confirmation
    backBtn.addEventListener("click", function () {
        confirmModal.style.display = "none";
    });

});