let lastScrollY = window.scrollY;
const header = document.getElementById("main-header");

window.addEventListener("scroll", () => {
    if (window.scrollY > lastScrollY) {
        // Scrolling Down → Hide Header
        header.classList.add("header-hidden");
    } else {
        // Scrolling Up → Show Header
        header.classList.remove("header-hidden");
    }
    lastScrollY = window.scrollY;
});