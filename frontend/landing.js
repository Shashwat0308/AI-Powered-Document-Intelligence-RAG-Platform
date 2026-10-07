function openApp() {
    window.location.href = "app.html";
}


/* =========================
   THEME SYSTEM
========================= */

function setTheme(theme) {

    if (theme === "system") {

        localStorage.removeItem("documind-theme");

        applySystemTheme();

        return;
    }

    localStorage.setItem(
        "documind-theme",
        theme
    );

    document.documentElement.setAttribute(
        "data-theme",
        theme
    );
}


/* =========================
   APPLY SYSTEM THEME
========================= */

function applySystemTheme() {

    const savedTheme =
        localStorage.getItem("documind-theme");

    if (savedTheme) {

        document.documentElement.setAttribute(
            "data-theme",
            savedTheme
        );

        return;
    }

    const prefersDark =
        window.matchMedia(
            "(prefers-color-scheme: dark)"
        ).matches;

    document.documentElement.setAttribute(
        "data-theme",
        prefersDark ? "dark" : "light"
    );
}


/* =========================
   INITIALIZE THEME
========================= */

applySystemTheme();


/* =========================
   SYSTEM THEME CHANGES
========================= */

window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {

        if (!localStorage.getItem("documind-theme")) {

            applySystemTheme();

        }

    });


    document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener("click", function (event) {
        const targetId = this.getAttribute("href");

        if (targetId === "#") return;

        const target = document.querySelector(targetId);

        if (target) {
            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    });
});