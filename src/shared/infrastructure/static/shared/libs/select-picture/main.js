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

// get pictures box based on id
function getPicturesBox(pictureBoxId) {
    return $(`[pictures-box='${pictureBoxId}']`).first();
}

// get picture html element
function getPictureElement(picture, popupData) {
    let updatePictureUrl = DjangoUrls["core:picture:update"]({
        picture_id: picture.id,
    });
    let deletePictureUrl = DjangoUrls["core:picture:delete"]({
        pk: picture.id,
    });

    let deleteScenario = "";
    if (popupData.many) {
        deleteScenario = `data-delete-element="#${picture.id}"`;
    } else {
        deleteScenario = `data-delete-callbacl="singlePictureRemovalCallback"`;
    }

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
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center" data-popup-open="${updatePictureUrl}" data-popup-name="select_picture_popup" data-popup-data="${JSON.stringify(
        popupData
    )}"><i class="bi bi-pen"></i></a>
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center" data-delete-url="${deletePictureUrl}" ${deleteScenario}><i class="bi bi-trash"></i></a>
              </div>
            </div>
          </div>
        </div>
    `);
}

// add managed picture to the desigred box
function addPictureBox(res) {
    const picturesBox = getPicturesBox(res.popupData.picture_box_id);
    const picture = res?.res?.picture;

    if (!picture) {
        console.warn("Missing picture data in popup reply:", res);
        return;
    }

    if (!picturesBox.length) {
        console.warn(
            `No pictures box found for id '${res.popupData.picture_box_id}'.`
        );
        return;
    }

    const pictureEl = getPictureElement(picture, res.popupData);
    const children = picturesBox.children();
    if (children.length) {
        children.last().before(pictureEl);
    } else {
        picturesBox.append(pictureEl);
    }
}

// update single picture
function updateSinglePicture(res) {
    const picture = res?.res?.picture;
    let pictureEl = getPictureElement(picture, res.popupData);
    $(`[single-picture-box="${res.popupData.picture_box_id}"]`).html(pictureEl);
}

function replaceUpdatedPicture(res) {
    const picture = res?.res?.picture;
    let pictureEl = getPictureElement(picture, res.popupData);
    $("#" + picture.id).replaceWith(pictureEl);
}

function singlePictureRemovalCallback(el, res) {
    let createPictureUrl = DjangoUrls["core:picture:create"]({
        picture_type: res.details.picture_type,
        content_type: res.details.content_type,
        object_id: res.details.object_id,
    });

    let pictureBoxId = $("#" + res.details.id)
        .parent()
        .attr("single-picture-box");

    let picturePopupData = {
        picture_box_id: pictureBoxId,
        many: false,
        picture_type: res.details.picture_type,
        object_id: res.details.object_id,
    };

    let selectPictureEl = $(`
    <div class="me-3 mb-3">
        <div class="image-box add-image rounded-3 cursor-pointer">
          <img src="/static/shared/images/defaults/dummy_150x150.jpg" width="150" height="150" alt="Add new image" />
          <div class="overlay d-flex flex-column justify-content-end align-items-center w-100 h-100" data-popup-open="${createPictureUrl}" data-popup-name="select_picture_popup" data-popup-data="${JSON.stringify(
        picturePopupData
    )}">
            <div class="actions d-flex justify-content-evenly align-items-center w-100 mb-3">
              <a class="action-button cursor-pointer d-flex justify-content-center align-items-center"><i class="bi bi-plus-lg"></i></a>
            </div>
          </div>
        </div>
      </div>
    `);

    $("#" + res.details.id).replaceWith(selectPictureEl);
}

// manage response of the select picture popup
window.PopupManager_onReply = function (res) {
    if (res.popupData.many) {
        if (res.res.is_update) {
            replaceUpdatedPicture(res);
        } else {
            addPictureBox(res);
        }
    } else {
        if (res.res.is_update) {
            replaceUpdatedPicture(res);
        } else {
            updateSinglePicture(res);
        }
    }
};
