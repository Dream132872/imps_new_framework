$(".image-box").on("mouseenter", function (e) {
    const overlay = $(this).children(".overlay");
    const actionButtons = overlay.find(".col-4");

    // Animate the overlay
    overlay.css("animation", "ShowPickImageActionButtonsAnimation forwards .3s");

    // Reset any existing button animations
    actionButtons.css("animation", "");

    // Animate each button with different delays
    actionButtons.each(function(index) {
        const delay = index * 0.05; // 0.1s delay between each button
        $(this).css("animation", `ShowActionButtonAnimation forwards .3s ${delay}s`);
    });
});

$(".image-box").on("mouseleave", function (e) {
    const overlay = $(this).children(".overlay");
    const actionButtons = overlay.find(".col-4");

    // Animate the overlay
    overlay.css("animation", "HidePickImageActionButtonsAnimation forwards .3s");

    // Reset any existing button animations
    actionButtons.css("animation", "");

    // Animate each button with different delays (reverse order)
    actionButtons.each(function(index) {
        const delay = (actionButtons.length - 1 - index) * 0.05; // Reverse order delay
        $(this).css("animation", `HideActionButtonAnimation forwards .3s ${delay}s`);
    });
});
