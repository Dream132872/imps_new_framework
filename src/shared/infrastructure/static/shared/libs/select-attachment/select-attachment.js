$(document).on("mouseenter", ".attachment-box", function (e) {
    const overlay = $(this).children(".overlay");
    const actionButtons = overlay.find(".action-button");

    // Animate the overlay
    overlay.css(
        "animation",
        "ShowPickAttachmentActionButtonsAnimation forwards .3s"
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

$(document).on("mouseleave", ".attachment-box", function (e) {
    const overlay = $(this).children(".overlay");
    const actionButtons = overlay.find(".action-button");

    // Animate the overlay
    overlay.css(
        "animation",
        "HidePickAttachmentActionButtonsAnimation forwards .3s"
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

// get attachments box based on id
function getAttachmentsBox(attachmentBoxId) {
    return $(`[attachments-box='${attachmentBoxId}']`).first();
}

// get attachment html element
function getAttachmentElement(attachment, popupData) {
    let updateAttachmentUrl = DjangoUrls["media:attachment:update"]({
        attachment_id: attachment.id,
    });
    let deleteAttachmentUrl = DjangoUrls["media:attachment:delete"]({
        pk: attachment.id,
    });

    let deleteScenario = "";
    if (popupData.many) {
        deleteScenario = `data-delete-element="#${attachment.id}"`;
    } else {
        deleteScenario = `data-delete-callback="singleAttachmentRemovalCallback"`;
    }

    const fileName = attachment.file.name ? attachment.file.name.split('/').pop() : 'file';

    return $(`
        <div class="me-3 mb-3" id="${attachment.id}">
          <div class="attachment-box rounded-3">
            <div class="attachment-icon d-flex justify-content-center align-items-center">
              <i class="bi bi-file-earmark"></i>
            </div>
            <div class="attachment-name">${fileName}</div>
            <div class="overlay d-flex flex-column justify-content-end align-items-center w-100 h-100">
              <div class="actions d-flex justify-content-evenly align-items-center w-100 mb-3">
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center" href="${attachment.file.url}" target="_blank"><i class="bi bi-eye"></i></a>
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center" data-popup-open="${updateAttachmentUrl}" data-popup-name="select_attachment_popup" data-popup-data="${JSON.stringify(
        popupData
    )}"><i class="bi bi-pen"></i></a>
                <a class="action-button cursor-pointer d-flex justify-content-center align-items-center" data-delete-url="${deleteAttachmentUrl}" ${deleteScenario}><i class="bi bi-trash"></i></a>
              </div>
            </div>
          </div>
        </div>
    `);
}

// add managed attachment to the desired box
function addAttachmentBox(res) {
    const attachmentsBox = getAttachmentsBox(res.popupData.attachment_box_id);
    const attachment = res?.res?.attachment;

    if (!attachment) {
        console.warn("Missing attachment data in popup reply:", res);
        return;
    }

    if (!attachmentsBox.length) {
        console.warn(
            `No attachments box found for id '${res.popupData.attachment_box_id}'.`
        );
        return;
    }

    const attachmentEl = getAttachmentElement(attachment, res.popupData);
    const children = attachmentsBox.children();
    if (children.length) {
        children.last().before(attachmentEl);
    } else {
        attachmentsBox.append(attachmentEl);
    }
}

// update single attachment
function updateSingleAttachment(res) {
    const attachment = res?.res?.attachment;
    let attachmentEl = getAttachmentElement(attachment, res.popupData);
    $(`[single-attachment-box="${res.popupData.attachment_box_id}"]`).html(attachmentEl);
}

// replace the attachment box with new uploaded one
function replaceUpdatedAttachment(res) {
    const attachment = res?.res?.attachment;
    let attachmentEl = getAttachmentElement(attachment, res.popupData);
    $("#" + attachment.id).replaceWith(attachmentEl);
}

// callback method name that should be called after singular attachment is removed
function singleAttachmentRemovalCallback(el, res) {
    let createAttachmentUrl = DjangoUrls["media:attachment:create"]({
        content_type: res.details.content_type,
        object_id: res.details.object_id,
    });

    let attachmentBoxId = $("#" + res.details.id)
        .parent()
        .attr("single-attachment-box");

    let attachmentPopupData = {
        attachment_box_id: attachmentBoxId,
        many: false,
        object_id: res.details.object_id,
    };

    let selectAttachmentEl = $(`
    <div class="me-3 mb-3">
        <div class="attachment-box add-attachment rounded-3 cursor-pointer">
          <div class="attachment-icon d-flex justify-content-center align-items-center">
            <i class="bi bi-file-earmark-plus"></i>
          </div>
          <div class="overlay d-flex flex-column justify-content-end align-items-center w-100 h-100" data-popup-open="${createAttachmentUrl}" data-popup-name="select_attachment_popup" data-popup-data="${JSON.stringify(
        attachmentPopupData
    )}">
            <div class="actions d-flex justify-content-evenly align-items-center w-100 mb-3">
              <a class="action-button cursor-pointer d-flex justify-content-center align-items-center"><i class="bi bi-plus-lg"></i></a>
            </div>
          </div>
        </div>
      </div>
    `);

    $("#" + res.details.id).replaceWith(selectAttachmentEl);
}

// manage response of the select attachment popup
window.PopupManager_onReply = function (res) {
    if (res.popupData && res.popupData.attachment_box_id) {
        if (res.popupData.many) {
            if (res.res.is_update) {
                replaceUpdatedAttachment(res);
            } else {
                addAttachmentBox(res);
            }
        } else {
            if (res.res.is_update) {
                replaceUpdatedAttachment(res);
            } else {
                updateSingleAttachment(res);
            }
        }
    }
};

