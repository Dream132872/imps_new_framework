const SELECTOR_SIDEBAR_WRAPPER = ".sidebar-wrapper";
const Default = {
    scrollbarTheme: "os-theme-light",
    scrollbarAutoHide: "leave",
    scrollbarClickScroll: true,
};
document.addEventListener("DOMContentLoaded", function () {
    const sidebarWrapper = document.querySelector(SELECTOR_SIDEBAR_WRAPPER);
    if (
        sidebarWrapper &&
        typeof OverlayScrollbarsGlobal?.OverlayScrollbars !== "undefined"
    ) {
        OverlayScrollbarsGlobal.OverlayScrollbars(sidebarWrapper, {
            scrollbars: {
                theme: Default.scrollbarTheme,
                autoHide: Default.scrollbarAutoHide,
                clickScroll: Default.scrollbarClickScroll,
            },
        });
    }
});

// // Color Mode Toggler
// (() => {
//     "use strict";

//     const storedTheme = localStorage.getItem("theme");

//     const getPreferredTheme = () => {
//         if (storedTheme) {
//             return storedTheme;
//         }

//         return window.matchMedia("(prefers-color-scheme: dark)").matches
//             ? "dark"
//             : "light";
//     };

//     const setTheme = function (theme) {
//         if (
//             theme === "auto" &&
//             window.matchMedia("(prefers-color-scheme: dark)").matches
//         ) {
//             document.documentElement.setAttribute("data-bs-theme", "dark");
//         } else {
//             document.documentElement.setAttribute("data-bs-theme", theme);
//         }
//     };

//     setTheme(getPreferredTheme());

//     const showActiveTheme = (theme, focus = false) => {
//         const themeSwitcher = document.querySelector("#bd-theme");

//         if (!themeSwitcher) {
//             return;
//         }

//         const themeSwitcherText = document.querySelector("#bd-theme-text");
//         const activeThemeIcon = document.querySelector(".theme-icon-active i");
//         const btnToActive = document.querySelector(
//             `[data-bs-theme-value="${theme}"]`
//         );
//         const svgOfActiveBtn = btnToActive
//             .querySelector("i")
//             .getAttribute("class");

//         for (const element of document.querySelectorAll(
//             "[data-bs-theme-value]"
//         )) {
//             element.classList.remove("active");
//             element.setAttribute("aria-pressed", "false");
//         }

//         btnToActive.classList.add("active");
//         btnToActive.setAttribute("aria-pressed", "true");
//         activeThemeIcon.setAttribute("class", svgOfActiveBtn);
//         const themeSwitcherLabel = `${themeSwitcherText.textContent} (${btnToActive.dataset.bsThemeValue})`;
//         themeSwitcher.setAttribute("aria-label", themeSwitcherLabel);

//         if (focus) {
//             themeSwitcher.focus();
//         }
//     };

//     window
//         .matchMedia("(prefers-color-scheme: dark)")
//         .addEventListener("change", () => {
//             if (storedTheme !== "light" || storedTheme !== "dark") {
//                 setTheme(getPreferredTheme());
//             }
//         });

//     window.addEventListener("DOMContentLoaded", () => {
//         showActiveTheme(getPreferredTheme());

//         for (const toggle of document.querySelectorAll(
//             "[data-bs-theme-value]"
//         )) {
//             toggle.addEventListener("click", () => {
//                 const theme = toggle.getAttribute("data-bs-theme-value");
//                 localStorage.setItem("theme", theme);
//                 setTheme(theme);
//                 showActiveTheme(theme, true);
//             });
//         }
//     });
// })();

// ========== begin::common waitme functions ==========
function open_waiting(selector = "body") {
    $(selector).waitMe({
        effect: "win8",
        text: gettext("Please wait") + " ...",
        bg: "rgba(255,255,255,0.7)",
        color: "#000",
    });
}

function close_waiting(selector = "body") {
    $(selector).waitMe("hide");
}
// ========== end::common waitme functions ==========

// ========== begin::ajax form default functions ==========
function defaultAjaxFormBegin() {
    open_waiting();
}

function defaultAjaxFormCompleted() {
    close_waiting();
}
// ========== end::ajax form default functions ==========
