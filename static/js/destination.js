document.addEventListener("DOMContentLoaded", function () {

    function initCarousel(containerId) {
        const container = document.getElementById(containerId);
        const track = container.querySelector(".carousel-track");
        const cards = Array.from(track.children);
        const prevBtn = container.querySelector(".carousel-btn.prev");
        const nextBtn = container.querySelector(".carousel-btn.next");
        const pagination = container.querySelector(".carousel-pagination");

        let centerIndex = 0;

        // Create pagination dots
        cards.forEach((_, i) => {
            const dot = document.createElement("span");
            dot.classList.add("dot");
            if (i === centerIndex) dot.classList.add("active");
            pagination.appendChild(dot);

            dot.addEventListener("click", () => {
                centerIndex = i;
                updateCarousel();
            });
        });

        function updateCarousel() {
            const len = cards.length;
            cards.forEach(card => card.classList.remove("left", "center", "right"));

            cards[centerIndex].classList.add("center");
            cards[(centerIndex - 1 + len) % len].classList.add("left");
            cards[(centerIndex + 1) % len].classList.add("right");

            pagination.querySelectorAll(".dot").forEach((dot, i) => {
                dot.classList.toggle("active", i === centerIndex);
            });
        }

        function moveNext() {
            centerIndex = (centerIndex + 1) % cards.length;
            updateCarousel();
        }

        function movePrev() {
            centerIndex = (centerIndex - 1 + cards.length) % cards.length;
            updateCarousel();
        }

        prevBtn.addEventListener("click", movePrev);
        nextBtn.addEventListener("click", moveNext);

        // Card click
        cards.forEach(card => {
            card.addEventListener("click", () => {
                const link = card.dataset.link;
                if (link) window.location.href = link;
            });
        });

        updateCarousel();
    }

    // Initialize both sliders independently
    initCarousel("popular-carousel");
    initCarousel("mustvisit-carousel");
    initCarousel("clickable-carousel");
});