/* GenericDeletion: attribute-driven deletion system with SweetAlert confirmation */
(function ($) {
    const GenericDeletion = {
        init: function () {
            this._bindAttributeHandlers();
        },

        _bindAttributeHandlers: function () {
            const self = this;
            $(document).on("click", "[data-delete-url]", function (evt) {
                evt.preventDefault();
                self.handleDeleteClick(this);
            });
        },

        handleDeleteClick: function (el) {
            const $el = $(el);
            const deleteUrl = $el.attr("data-delete-url");
            const deleteTitle =
                $el.attr("data-delete-title") || gettext("Are you sure?");
            const infoMessage =
                $el.attr("data-delete-info-message") ||
                gettext("Are you sure you want to delete this information?");
            const successMessage =
                $el.attr("data-delete-success-message") ||
                gettext("Information deleted successfully");

            if (!deleteUrl) {
                console.warn("data-delete-url attribute is required");
                return;
            }

            // Check if SweetAlert2 is available
            if (typeof Swal !== "undefined") {
                this._showSweetAlertConfirmation(
                    deleteUrl,
                    deleteTitle,
                    infoMessage,
                    successMessage,
                    $el
                );
            } else {
                // Fallback to native confirm
                this._showNativeConfirmation(
                    deleteUrl,
                    infoMessage,
                    successMessage,
                    $el
                );
            }
        },

        _showSweetAlertConfirmation: function (
            deleteUrl,
            deleteTitle,
            infoMessage,
            successMessage,
            $el
        ) {
            const self = this;
            Swal.fire({
                title: deleteTitle,
                text: infoMessage,
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: gettext("Yes, delete it!"),
                cancelButtonText: gettext("Cancel"),
                showClass: {
                    popup: `animate__animated animate__zoomIn animate__faster`,
                },
                hideClass: {
                    popup: `animate__animated animate__zoomOut`,
                },
            }).then(function (result) {
                if (result.isConfirmed) {
                    self._performDelete(deleteUrl, successMessage, $el);
                }
            });
        },

        _showNativeConfirmation: function (
            deleteUrl,
            infoMessage,
            successMessage,
            $el
        ) {
            const self = this;
            if (confirm(infoMessage)) {
                this._performDelete(deleteUrl, successMessage, $el);
            }
        },

        _performDelete: function (deleteUrl, successMessage, $el) {
            const self = this;

            /* // Show loading state if SweetAlert is available
            if (typeof Swal !== "undefined") {
                Swal.fire({
                    title: gettext("Processing..."),
                    text: gettext("Please wait"),
                    allowOutsideClick: false,
                    showClass: {
                        popup: `animate__animated animate__zoomIn animate__faster`,
                    },
                    hideClass: {
                        popup: `animate__animated animate__zoomOut`,
                    },
                    didOpen: function () {
                        Swal.showLoading();
                    },
                });
            } */

            // Make the delete request
            $.ajax({
                url: deleteUrl,
                method: "POST",
                data: {
                    csrfmiddlewaretoken: this._getCsrfToken(),
                },
                success: function (response) {
                    if (typeof Swal !== "undefined") {
                        Swal.fire({
                            icon: "success",
                            title: gettext("Success!"),
                            text: successMessage,
                            timer: 2000,
                            showConfirmButton: false,
                            showClass: {
                                popup: `animate__animated animate__zoomIn animate__faster`,
                            },
                            hideClass: {
                                popup: `animate__animated animate__zoomOut`,
                            },
                        }).then(function () {
                            self._handleDeleteSuccess($el, response);
                        });
                    } else {
                        alert(successMessage);
                        self._handleDeleteSuccess($el, response);
                    }
                },
                error: function (xhr, status, error) {
                    const errorMessage =
                        xhr.responseJSON?.message ||
                        xhr.responseText ||
                        gettext("An error occurred while deleting");

                    if (typeof Swal !== "undefined") {
                        Swal.fire({
                            showClass: {
                                popup: `animate__animated animate__zoomIn animate__faster`,
                            },
                            hideClass: {
                                popup: `animate__animated animate__zoomOut`,
                            },
                            icon: "error",
                            title: gettext("Error!"),
                            text: errorMessage,
                        });
                    } else {
                        alert(gettext("Error: ") + errorMessage);
                    }
                },
            });
        },

        _getCsrfToken: function () {
            // Try to get CSRF token from cookie
            let csrftoken = this._getCookie("csrftoken");

            // If not found in cookie, try to get from meta tag
            if (!csrftoken) {
                const $meta = $('meta[name="csrf-token"]');
                if ($meta.length) {
                    csrftoken = $meta.attr("content");
                }
            }

            // If still not found, try to get from form
            if (!csrftoken) {
                const $csrfInput = $('input[name="csrfmiddlewaretoken"]');
                if ($csrfInput.length) {
                    csrftoken = $csrfInput.val();
                }
            }

            return csrftoken || "";
        },

        _getCookie: function (name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== "") {
                const cookies = document.cookie.split(";");
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === name + "=") {
                        cookieValue = decodeURIComponent(
                            cookie.substring(name.length + 1)
                        );
                        break;
                    }
                }
            }
            return cookieValue;
        },

        _handleDeleteSuccess: function ($el, response) {
            // Priority 1: Check for data-delete-callback attribute
            const callbackFunctionName = $el.attr("data-delete-callback");

            if (callbackFunctionName !== undefined) {
                if (this._tryCallCallback(callbackFunctionName, $el, response)) {
                    // Callback was successfully called
                    this._triggerSuccessEvent($el, response);
                    return;
                } else {
                    // Callback function doesn't exist, reload page
                    this._triggerSuccessEvent($el, response);
                    window.location.reload();
                    return;
                }
            }

            // Priority 2: Check for data-delete-element attribute
            const deleteElementSelector = $el.attr("data-delete-element");

            if (deleteElementSelector !== undefined) {
                // If data-delete-element exists but has no value (empty string), reload location
                if (!deleteElementSelector || deleteElementSelector.trim() === "") {
                    window.location.reload();
                    this._triggerSuccessEvent($el, response);
                    return;
                }

                // If selector is provided, delete the element matching that selector
                const $elementToDelete = $(deleteElementSelector);
                if ($elementToDelete.length) {
                    $elementToDelete.fadeOut(300, function () {
                        $(this).remove();
                    });
                }
            } else {
                // Default behavior: reload location if neither callback nor element selector is provided
                window.location.reload();
            }

            // Trigger custom event for other scripts to listen
            this._triggerSuccessEvent($el, response);
        },

        _tryCallCallback: function (functionName, $el, response) {
            if (!functionName || functionName.trim() === "") {
                return false;
            }

            try {
                // Try to resolve the function from window object
                // Supports both simple names (myFunction) and namespaced (MyNamespace.myFunction)
                const functionPath = functionName.trim().split(".");
                let func = window;

                for (let i = 0; i < functionPath.length; i++) {
                    if (func && typeof func === "object" && functionPath[i] in func) {
                        func = func[functionPath[i]];
                    } else {
                        return false;
                    }
                }

                // Check if it's actually a function
                if (typeof func === "function") {
                    // Call the function with element and response as parameters
                    func($el, response);
                    return true;
                }

                return false;
            } catch (e) {
                console.warn("Error calling callback function:", functionName, e);
                return false;
            }
        },

        _triggerSuccessEvent: function ($el, response) {
            // Trigger custom event for other scripts to listen
            $(document).trigger("generic-deletion:success", {
                element: $el,
                response: response,
            });
        },
    };

    // Expose globally
    window.GenericDeletion = GenericDeletion;

    // Auto-init on DOM ready
    $(function () {
        GenericDeletion.init();
    });
})(jQuery);
