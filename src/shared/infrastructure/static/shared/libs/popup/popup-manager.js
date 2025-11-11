/* PopupManager: attribute-driven popup system with data passing and localStorage lifecycle */
(function ($) {
    const STORAGE_PREFIX = "popup:";
    const MESSAGE_TYPE_REPLY = "popup-reply";

    function generateId() {
        return (
            "pm-" + Date.now() + "-" + Math.random().toString(36).slice(2, 10)
        );
    }

    function buildFeatures(featureStr) {
        if (!featureStr)
            return "width=1000,height=700,resizable=yes,scrollbars=yes";
        return featureStr;
    }

    function parseFeatures(featureStr) {
        const obj = {};
        if (!featureStr) return obj;
        featureStr.split(",").forEach(function (part) {
            const [k, v] = part.split("=");
            if (!k) return;
            obj[k.trim()] = (v || "").trim();
        });
        return obj;
    }

    function stringifyFeatures(obj) {
        return Object.keys(obj)
            .map(function (k) {
                return k + "=" + obj[k];
            })
            .join(",");
    }

    function shouldCenterFromAttr($el) {
        const raw = $el.attr("data-popup-center");
        if (raw === undefined) return true; // default: center
        const v = String(raw).trim().toLowerCase();
        if (v === "") return true; // boolean attribute without value => true
        return !(v === "false" || v === "0" || v === "no" || v === "off");
    }

    function resolvePath(root, path) {
        if (!root || !path) return undefined;
        const parts = String(path).split(".");
        let node = root;
        for (let i = 0; i < parts.length; i++) {
            const key = parts[i];
            if (key in node) {
                node = node[key];
            } else {
                return undefined;
            }
        }
        return node;
    }

    function getDataPayloadFromAttributes($el) {
        const hasDataAttr = $el.is("[data-popup-data]");
        if (hasDataAttr) {
            const raw = $el.attr("data-popup-data");
            if (raw && raw.trim() !== "") {
                // Try JSON first
                try {
                    return JSON.parse(raw);
                } catch (_) {
                    // Fallback: treat as global variable path on opener window
                    try {
                        return resolvePath(window, raw.trim());
                    } catch (_) {
                        return undefined;
                    }
                }
            }
        }
        const fromSelector = $el.attr("data-popup-data-from");
        if (fromSelector) {
            const $form = $(fromSelector);
            if ($form.length) {
                return toObjectFromForm($form);
            }
        }
        return undefined;
    }

    function toObjectFromForm($form) {
        const arr = $form.serializeArray();
        const obj = {};
        arr.forEach(function (item) {
            const name = item.name;
            const value = item.value;
            if (obj[name] === undefined) {
                obj[name] = value;
            } else if (Array.isArray(obj[name])) {
                obj[name].push(value);
            } else {
                obj[name] = [obj[name], value];
            }
        });
        return obj;
    }

    function readJsonAttribute($el, attr) {
        const raw = $el.attr(attr);
        if (!raw) return undefined;
        try {
            return JSON.parse(raw);
        } catch (e) {
            console.warn("Invalid JSON in", attr, e);
            return undefined;
        }
    }

    function setStorage(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }
    function getStorage(key) {
        const raw = localStorage.getItem(key);
        if (!raw) return undefined;
        try {
            return JSON.parse(raw);
        } catch (e) {
            return undefined;
        }
    }
    function delStorage(key) {
        localStorage.removeItem(key);
    }

    const PopupManager = {
        currentPopupId: null,
        parentPopupId: null, // retained for backward compat; no longer populated
        isPopupWindow: false,

        init: function () {
            const params = new URLSearchParams(window.location.search);
            this.currentPopupId = params.get("popupId");
            // parentId is no longer required; not parsed
            this.isPopupWindow = !!this.currentPopupId;

            // Note: Do not delete on beforeunload so reloads keep data intact.

            // Listen for reply messages from any child popups
            window.addEventListener("message", function (event) {
                const msg = event.data;
                if (!msg || msg.type !== MESSAGE_TYPE_REPLY) return;
                // Invoke local hook and optionally bubble upstream if requested
                let handlerResult;
                if (typeof window.PopupManager_onReply === "function") {
                    try {
                        handlerResult = window.PopupManager_onReply(
                            msg.payload
                        );
                    } catch (e) {}
                }
                if (handlerResult && handlerResult.bubble) {
                    const nextPayload =
                        handlerResult.payload !== undefined
                            ? handlerResult.payload
                            : msg.payload;
                    const forward = {
                        type: MESSAGE_TYPE_REPLY,
                        payload: nextPayload,
                    };
                    try {
                        if (window.opener && !window.opener.closed) {
                            window.opener.postMessage(forward, "*");
                        }
                    } catch (_) {}
                }
            });

            // Attribute handlers
            this._bindAttributeHandlers();
        },

        openFromElement: function (el) {
            const $el = $(el);
            const url = $el.attr("data-popup-open");
            if (!url) return;

            // Construct payload (JSON string, or global var path, or form serialization)
            let payload = getDataPayloadFromAttributes($el);
            if (payload === undefined) payload = {};

            // Contextual info
            // parentId no longer used in URL; opener relationship is implicit
            const requestedName = ($el.attr("data-popup-name") || "").trim();
            const popupId = requestedName !== "" ? requestedName : generateId();
            let features = buildFeatures($el.attr("data-popup-features"));

            // Optional centering (default: true)
            if (shouldCenterFromAttr($el)) {
                const fObj = parseFeatures(features);
                const w = parseInt(fObj.width, 10) || 520;
                const h = parseInt(fObj.height, 10) || 520;
                const left = Math.max(
                    0,
                    (window.screenX || window.screenLeft || 0) +
                        Math.max(
                            0,
                            Math.floor(
                                ((window.outerWidth || window.innerWidth) - w) /
                                    2
                            )
                        )
                );
                const top = Math.max(
                    0,
                    (window.screenY || window.screenTop || 0) +
                        Math.max(
                            0,
                            Math.floor(
                                ((window.outerHeight || window.innerHeight) -
                                    h) /
                                    2
                            )
                        )
                );
                fObj.left = left;
                fObj.top = top;
                // Also include non-standard aliases for broader support
                fObj.screenX = left;
                fObj.screenY = top;
                features = stringifyFeatures(fObj);
            }

            // Persist payload scoped to popupId
            setStorage(STORAGE_PREFIX + popupId + ":data", payload);

            // Open the popup with ids in query
            const sep = url.indexOf("?") === -1 ? "?" : "&";
            const finalUrl =
                url + sep + "popupId=" + encodeURIComponent(popupId);
            const win = window.open(finalUrl, popupId, features);

            // Watch for popup close and cleanup storage only then
            try {
                const storageKey = STORAGE_PREFIX + popupId + ":data";
                const closeWatcher = setInterval(function () {
                    if (!win || win.closed) {
                        clearInterval(closeWatcher);
                        delStorage(storageKey);
                    }
                }, 700);
            } catch (_) {}

            return win;
        },

        getData: function () {
            if (!this.currentPopupId) return undefined;
            return getStorage(STORAGE_PREFIX + this.currentPopupId + ":data");
        },

        reply: function (payload) {
            const message = { type: MESSAGE_TYPE_REPLY, payload: payload };
            try {
                if (window.opener && !window.opener.closed) {
                    window.opener.postMessage(message, "*");
                }
            } catch (_) {}
        },

        _bindAttributeHandlers: function () {
            const self = this;
            // Openers
            $(document).on("click", "[data-popup-open]", function (evt) {
                evt.preventDefault();
                self.openFromElement(this);
            });

            // Reply buttons
            $(document).on(
                "click",
                "[data-popup-reply], [data-popup-reply-from]",
                function (evt) {
                    evt.preventDefault();
                    const $el = $(this);
                    let payload = readJsonAttribute($el, "data-popup-reply");
                    const fromSelector = $el.attr("data-popup-reply-from");
                    if (!payload && fromSelector) {
                        const $form = $(fromSelector);
                        if ($form.length) {
                            payload = toObjectFromForm($form);
                        }
                    }
                    if (!payload) payload = {};
                    self.reply(payload);
                }
            );
        },
    };

    // Expose globally
    window.PopupManager = PopupManager;

    // Auto-init on DOM ready
    $(function () {
        PopupManager.init();
    });
})(jQuery);
