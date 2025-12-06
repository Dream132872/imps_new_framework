/**
 * GenericDeletion - Attribute-Driven Deletion System
 *
 * A jQuery-based deletion utility that provides a unified, attribute-driven approach
 * for handling delete operations across the application. It supports SweetAlert2
 * confirmations with automatic fallback to native browser confirm dialogs.
 *
 * ## How It Works
 *
 * 1. **Initialization**: Automatically initializes on DOM ready and binds event
 *    handlers to all elements with the `data-delete-url` attribute.
 *
 * 2. **User Interaction**: When a user clicks an element with `data-delete-url`,
 *    the system prevents default behavior and shows a confirmation dialog.
 *
 * 3. **Confirmation**:
 *    - If SweetAlert2 is available: Shows a styled confirmation dialog with
 *      customizable title, message, and animations.
 *    - If SweetAlert2 is not available: Falls back to native browser `confirm()`.
 *
 * 4. **Deletion Request**: On confirmation, makes a POST AJAX request to the
 *    specified URL with CSRF token included (automatically retrieved from cookie,
 *    meta tag, or form input).
 *
 * 5. **Success Handling**: After successful deletion, handles the response with
 *    a priority system:
 *    - Priority 1: If `data-delete-callback` is specified, calls the custom
 *      callback function (supports namespaced functions like "MyNamespace.myFunction").
 *    - Priority 2: If `data-delete-element` is specified, fades out and removes
 *      the matching DOM element.
 *    - Default: Reloads the page.
 *
 * 6. **Events**: Triggers a custom jQuery event `generic-deletion:success` after
 *    successful deletion, allowing other scripts to listen and react.
 *
 * ## Data Attributes
 *
 * ### Required:
 * - `data-delete-url`: The URL endpoint to send the DELETE request to (POST method)
 *
 * ### Optional:
 * - `data-delete-title`: Custom title for confirmation dialog (default: "Are you sure?")
 * - `data-delete-info-message`: Custom confirmation message (default: "Are you sure you want to delete this information?")
 * - `data-delete-success-message`: Custom success message (default: "Information deleted successfully")
 * - `data-delete-callback`: Name of a global function to call after successful deletion
 *   (e.g., "myFunction" or "MyNamespace.myFunction"). Takes two parameters: $element, response
 * - `data-delete-element`: CSS selector for element to remove after deletion
 *   (e.g., ".item-row" or "#item-123"). If empty string, reloads page instead.
 *
 * ## Usage Example
 *
 * ```html
 * <!-- Basic usage with default messages -->
 * <button data-delete-url="/api/items/123/delete/">Delete Item</button>
 *
 * <!-- Custom messages -->
 * <a href="#"
 *    data-delete-url="/api/pictures/456/delete/"
 *    data-delete-title="Delete Picture?"
 *    data-delete-info-message="This picture will be permanently deleted."
 *    data-delete-success-message="Picture deleted successfully!">
 *    Delete Picture
 * </a>
 *
 * <!-- With callback function -->
 * <button data-delete-url="/api/items/789/delete/"
 *         data-delete-callback="handleItemDelete">
 *    Delete Item
 * </button>
 *
 * <!-- Remove specific element after deletion -->
 * <button data-delete-url="/api/items/101/delete/"
 *         data-delete-element="#item-101">
 *    Delete Item
 * </button>
 *
 * <!-- Custom callback with namespaced function -->
 * <button data-delete-url="/api/items/202/delete/"
 *         data-delete-callback="MyApp.handleDelete">
 *    Delete Item
 * </button>
 * ```
 *
 * ## Callback Function Signature
 *
 * ```javascript
 * function myCallback($element, response) {
 *     // $element: jQuery object of the clicked element
 *     // response: Server response from the delete request
 *     console.log("Deleted:", response);
 * }
 * ```
 *
 * ## Listening to Events
 *
 * ```javascript
 * $(document).on('generic-deletion:success', function(event, data) {
 *     // data.element: jQuery object of the clicked element
 *     // data.response: Server response from the delete request
 *     console.log("Deletion successful:", data.response);
 * });
 * ```
 *
 * ## Dependencies
 *
 * - jQuery (required)
 * - SweetAlert2 (optional, falls back to native confirm if not available)
 * - Animate.css (optional, for animation classes in SweetAlert)
 * - Django CSRF token (required for POST requests)
 *
 * ## CSRF Token Handling
 *
 * Automatically retrieves CSRF token in the following order:
 * 1. From `csrftoken` cookie
 * 2. From `<meta name="csrf-token">` tag
 * 3. From `<input name="csrfmiddlewaretoken">` in any form
 *
 * ## Error Handling
 *
 * On error, displays error message from server response (checks `responseJSON.message`,
 * `responseText`, or shows default error message). If SweetAlert2 is available,
 * shows styled error dialog, otherwise uses native `alert()`.
 *
 * ## Global API
 *
 * The module exposes `window.GenericDeletion` object with the following public methods:
 * - `init()`: Manually initialize the deletion system (auto-initialized on DOM ready)
 * - `handleDeleteClick(el)`: Programmatically trigger deletion on an element
 *
 * @module GenericDeletion
 * @requires jQuery
 * @optional SweetAlert2
 */
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
                            timer: 1000,
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
                        xhr.responseJSON?.error ||
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
