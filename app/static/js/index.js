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

document.querySelectorAll('.info-box').forEach(box => {
box.addEventListener('mousemove', function(e) {
const rect = this.getBoundingClientRect();
const x = e.clientX - rect.left;
const y = e.clientY - rect.top;
this.style.setProperty('--x', x + 'px');
this.style.setProperty('--y', y + 'px');
});
});