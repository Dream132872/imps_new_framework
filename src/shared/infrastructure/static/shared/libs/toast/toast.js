function showToast(
    title,
    message,
    type = "info",
    duration = 5000
) {
    // Validate dependencies
    if (typeof $ === "undefined") {
        console.error("jQuery is required for showToast");
        return;
    }
    if (typeof bootstrap === "undefined") {
        console.error("Bootstrap is required for showToast");
        return;
    }

    // Ensure toast container exists
    let toastContainer = $("#toast-container");
    if (toastContainer.length === 0) {
        toastContainer = $(
            '<div id="toast-container" class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1055;"></div>'
        );
        $("body").append(toastContainer);
    }

    const toastId = "toast-" + Date.now();
    const iconClass = getIconClass(type);
    const toastClass = getToastClass(type);

    let toastEl =
        $(`<div id="${toastId}" class="toast ${toastClass}" role="alert" aria-live="assertive" aria-atomic="true">
          <div class="toast-header">
            <i class="bi ${iconClass} me-2"></i>
            <strong class="me-auto text-white">${title}</strong>
            <small class="text-white">${new Date().toLocaleTimeString()}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
          </div>
          <div class="toast-body">${message}</div>
        </div>`);

    toastContainer.append(toastEl);

    // Create and show toast
    const toastBootstrap = new bootstrap.Toast(toastEl[0], {
        delay: duration,
    });
    toastBootstrap.show();

    // Auto-remove from DOM after animation
    toastEl.on("hidden.bs.toast", function () {
        $(this).remove();
    });
}

function getIconClass(type) {
    const icons = {
        success: "bi-check-circle-fill text-white",
        error: "bi-exclamation-triangle-fill text-white",
        warning: "bi-exclamation-triangle-fill text-white",
        info: "bi-info-circle-fill text-white",
    };
    return icons[type] || icons["info"];
}

function getToastClass(type) {
    const toastClass = {
        success: "toast-success",
        error: "toast-danger",
        warning: "toast-warning",
        info: "toast-info",
    };
    return toastClass[type] || toastClass["info"];
}

function testToast(){
    showToast('موفقیت', 'عملیات با موفقیت انجام شد', 'success', 100000);
    showToast('اعلان', 'پردازش مورد نظر در حال اجرا می باشد', 'info', 100000);
    showToast('اخطار', 'اطلاعات مورد نظر کامل نیست', 'warning', 100000);
    showToast('موفقیت', 'عملیات با خطا مواجه شد', 'error', 100000);
}