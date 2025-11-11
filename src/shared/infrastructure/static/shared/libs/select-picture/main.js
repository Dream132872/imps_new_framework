$(".image-box").on("mouseenter", function (e) {
    const overlay = $(this).children(".overlay");
    const actionButtons = overlay.find(".action-button");

    // Animate the overlay
    overlay.css(
        "animation",
        "ShowPickImageActionButtonsAnimation forwards .3s"
    );

    // Reset any existing button animations
    actionButtons.css("animation", "");

    // Animate each button with different delays
    actionButtons.each(function (index) {
        const delay = index * 0.05; // 0.1s delay between each button
        $(this).css(
            "animation",
            `ShowActionButtonAnimation forwards .3s ${delay}s`
        );
    });
});

$(".image-box").on("mouseleave", function (e) {
    const overlay = $(this).children(".overlay");
    const actionButtons = overlay.find(".action-button");

    // Animate the overlay
    overlay.css(
        "animation",
        "HidePickImageActionButtonsAnimation forwards .3s"
    );

    // Reset any existing button animations
    actionButtons.css("animation", "");

    // Animate each button with different delays (reverse order)
    actionButtons.each(function (index) {
        const delay = (actionButtons.length - 1 - index) * 0.05; // Reverse order delay
        $(this).css(
            "animation",
            `HideActionButtonAnimation forwards .3s ${delay}s`
        );
    });
});

// get picture box based on id
function getPicturesBox(pictureBoxId) {
    let picturesBoxes = $(`[pictures-box='${pictureBoxId}']`);
    if (picturesBoxes.length > 0) {
        return picturesBoxes[0];
    }
}

function addPictureBox(res) {
    let picturesBox = getPicturesBox(res.popupData.pictures_box_id);
    let pictureEl = `
        <div class="me-3 mb-3">
          <div class="image-box rounded-3">
            <img src="${res.picture.image.url}" data-popup-open="${res.picture.image.url}" data-popup-name="select_picture_popup" data-popup-features="width=${res.picture.image.width},height=${res.picture.image.height}" width="150" height="150" alt="" />
            <div class="overlay d-flex flex-column justify-content-end align-items-center w-100 h-100">
              <div class="actions d-flex justify-content-evenly align-items-center w-100 mb-3">
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center" data-popup-open="{{ pic.image.url }}" data-popup-name="picture_preview_popup" data-popup-features="width={{ pic.image.width }},height={{ pic.image.height }}"><i class="bi bi-eye"></i></a>
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center"><i class="bi bi-pen"></i></a>
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center"><i class="bi bi-trash"></i></a>
              </div>
            </div>
          </div>
        </div>
    `;
}

// manage response of the select picture popup
window.PopupManager_onReply = function (res) {
    if (res.popupData.many) {
        addPictureBox(res);
    }
};
