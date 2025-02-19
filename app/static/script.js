document.addEventListener("DOMContentLoaded", function () {
    const toggleSwitch = document.getElementById("theme-toggle");
    const body = document.body;
    const updateNewsBtn = document.getElementById("update-news");
    const moonIcon = document.querySelector(".moon");
    const sunIcon = document.querySelector(".sun");

 // Default to dark mode
 if (localStorage.getItem("theme") !== "light") {
    body.classList.add("dark-mode");
    toggleSwitch.checked = true;
    moonIcon.style.opacity = "1";
    sunIcon.style.opacity = "0.3";
} else {
    moonIcon.style.opacity = "0.3";
    sunIcon.style.opacity = "1";
}

toggleSwitch.addEventListener("change", function () {
    if (this.checked) {
        body.classList.add("dark-mode");
        localStorage.setItem("theme", "dark");
        moonIcon.style.opacity = "1";
        sunIcon.style.opacity = "0.3";
    } else {
        body.classList.remove("dark-mode");
        localStorage.setItem("theme", "light");
        moonIcon.style.opacity = "0.3";
        sunIcon.style.opacity = "1";
    }
});

updateNewsBtn.addEventListener("click", function () {
    fetch("/update_news").then(response => response.json()).then(data => {
        alert("News Updated!");
        location.reload();
    });
});
});
