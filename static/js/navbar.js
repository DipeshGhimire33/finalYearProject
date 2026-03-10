const hamburger = document.querySelector(".hamburger");
const mobileMenu = document.querySelector(".mobile-menu");

hamburger.addEventListener("click", () => {
    mobileMenu.classList.toggle("active");
});

// Close menu if screen is resized to desktop
window.addEventListener("resize", () => {
    if (window.innerWidth >= 992) {
        mobileMenu.classList.remove("active");
    }
});