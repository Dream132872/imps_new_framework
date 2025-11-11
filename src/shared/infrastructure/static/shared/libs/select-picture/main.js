$(document).on("mouseenter", ".image-box", function (e) {
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

$(document).on("mouseleave", ".image-box", function (e) {
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
    return $(`[pictures-box='${pictureBoxId}']`).first();
}

// get picture html element
function getPictureElement(picture) {
    return $(`
        <div class="me-3 mb-3" id="${picture.id}">
          <div class="image-box rounded-3">
            <img src="${picture.image.url}" width="150" height="150" alt="${
        picture.alt || ""
    }" />
            <div class="overlay d-flex flex-column justify-content-end align-items-center w-100 h-100">
              <div class="actions d-flex justify-content-evenly align-items-center w-100 mb-3">
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center" data-popup-open="${
                    picture.image.url
                }" data-popup-name="picture_preview_popup" data-popup-features="width=${
        picture.image.width
    },height=${picture.image.height}"><i class="bi bi-eye"></i></a>
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center"><i class="bi bi-pen"></i></a>
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center"><i class="bi bi-trash"></i></a>
              </div>
            </div>
          </div>
        </div>
    `);
}

// add managed picture to the desigred box
function addPictureBox(res) {
    const picturesBox = getPicturesBox(res.popupData.pictures_box_id);
    const picture = res?.res?.picture;

    if (!picture) {
        console.warn("Missing picture data in popup reply:", res);
        return;
    }

    if (!picturesBox.length) {
        console.warn(
            `No pictures box found for id '${res.popupData.pictures_box_id}'.`
        );
        return;
    }

    const pictureEl = getPictureElement(picture);
    const children = picturesBox.children();
    if (children.length) {
        children.last().before(pictureEl);
    } else {
        picturesBox.append(pictureEl);
    }
}

// manage response of the select picture popup
window.PopupManager_onReply = function (res) {
    if (res.popupData.many) {
        addPictureBox(res);
    } else {
    }
};
