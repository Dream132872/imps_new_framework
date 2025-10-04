/**
 * Enhanced Custom Popup Receiver
 *
 * This module handles data reception and communication in popup windows.
 * It should be included in popup pages to enable communication with the parent window.
 *
 * Features:
 * - Automatic data retrieval from parent window
 * - Close handler execution
 * - Parent window communication
 * - Error handling
 * - Cross-browser compatibility
 *
 * Usage:
 * Include this script in your popup pages and access data via:
 * - popupData: Data passed from parent window
 * - closeHandler: Function to call when popup closes
 * - PopupReceiver.close(): Method to close popup and notify parent
 */

(function($) {
    'use strict';

    // Popup receiver configuration
    const PopupReceiver = {
        // Storage key for popup data
        storageKey: 'customPopupWindow',

        // Data received from parent window
        popupData: {},

        // Close handler function name
        closeHandler: null,

        // Parent window reference
        parentWindow: null,

        // Initialization flag
        initialized: false,


        /**
         * Initialize the popup receiver
         */
        init: function() {
            if (this.initialized) {
                return;
            }

            try {
                this.parentWindow = this.getParentWindow();
                this.loadDataFromParent();
                this.setupEventListeners();
                this.initialized = true;

                console.log('Popup Receiver initialized');
                console.log('Received data:', this.popupData);
                console.log('Close handler:', this.closeHandler);

            } catch (error) {
                console.error('Error initializing popup receiver:', error);
            }
        },

        /**
         * Get parent window reference
         * @returns {Window|null} Parent window or null
         */
        getParentWindow: function() {
            try {
                if (window.opener) {
                    return window.opener;
                }

                if (window.parent && window.parent !== window) {
                    return window.parent;
                }

                return null;
            } catch (error) {
                console.error('Error getting parent window:', error);
                return null;
            }
        },

        /**
         * Load data from parent window
         */
        loadDataFromParent: function() {
            try {
                const storedData = localStorage.getItem(this.storageKey);

                if (storedData) {
                    const data = JSON.parse(storedData);

                    if (data.popupData) {
                        this.popupData = data.popupData;
                    }

                    if (data.handler) {
                        this.closeHandler = data.handler;
                    }

                    // Clean up storage after reading
                    this.cleanupStorage();
                }
            } catch (error) {
                console.error('Error loading data from parent:', error);
            }
        },

        /**
         * Setup event listeners
         */
        setupEventListeners: function() {
            const self = this;

            // Handle window close
            $(window).on('beforeunload', function() {
                self.notifyParentClose();
            });

            // Handle page visibility change
            $(document).on('visibilitychange', function() {
                if (document.hidden) {
                    self.notifyParentClose();
                }
            });
        },

        /**
         * Notify parent window that popup is closing
         */
        notifyParentClose: function() {
            try {
                if (this.parentWindow) {
                    // Send message to parent
                    this.parentWindow.postMessage({
                        type: 'popup-close',
                        target: window.name || 'custom-popup',
                        timestamp: Date.now()
                    }, '*');
                }

                // Also use storage as fallback
                this.notifyParentViaStorage();

            } catch (error) {
                console.error('Error notifying parent window:', error);
            }
        },

        /**
         * Notify parent via localStorage
         */
        notifyParentViaStorage: function() {
            try {
                const closeData = {
                    type: 'popup-close',
                    target: window.name || 'custom-popup',
                    timestamp: Date.now()
                };

                localStorage.setItem(this.storageKey, JSON.stringify(closeData));

                // Clean up after a short delay
                setTimeout(() => {
                    this.cleanupStorage();
                }, 100);

            } catch (error) {
                console.error('Error notifying parent via storage:', error);
            }
        },

        /**
         * Close popup and notify parent
         * @param {Object} data - Optional data to send to parent
         */
        close: function(data) {
            try {
                // Send data to parent if provided
                if (data) {
                    this.sendDataToParent(data);
                }

                // Notify parent of close
                this.notifyParentClose();

                // Close the window
                window.close();

            } catch (error) {
                console.error('Error closing popup:', error);
            }
        },

        /**
         * Send data to parent window
         * @param {Object} data - Data to send
         */
        sendDataToParent: function(data) {
            try {
                if (this.parentWindow) {
                    this.parentWindow.postMessage({
                        type: 'popup-data',
                        data: data,
                        timestamp: Date.now()
                    }, '*');
                }
            } catch (error) {
                console.error('Error sending data to parent:', error);
            }
        },

        /**
         * Clean up localStorage
         */
        cleanupStorage: function() {
            try {
                localStorage.removeItem(this.storageKey);
            } catch (error) {
                console.error('Error cleaning up storage:', error);
            }
        },

        /**
         * Get popup data
         * @returns {Object} Popup data
         */
        getData: function() {
            return this.popupData;
        },

        /**
         * Set popup data
         * @param {Object} data - Data to set
         */
        setData: function(data) {
            this.popupData = data;
        },

        /**
         * Get close handler
         * @returns {string|null} Close handler function name
         */
        getCloseHandler: function() {
            return this.closeHandler;
        },

        /**
         * Check if popup is in popup mode
         * @returns {boolean} True if in popup mode
         */
        isPopupMode: function() {
            return window.opener !== null || window.parent !== window;
        },

        /**
         * Get detailed popup detection information
         * @returns {Object} Popup detection details
         */
        getPopupInfo: function() {
            const isPopup = this.isPopupMode();
            const hasOpener = window.opener !== null;
            const hasParent = window.parent !== window;
            const isIframe = window.parent !== window && !window.opener;
            const isNewWindow = window.opener !== null;

            return {
                isPopup: isPopup,
                hasOpener: hasOpener,
                hasParent: hasParent,
                isIframe: isIframe,
                isNewWindow: isNewWindow,
                windowName: window.name || 'unnamed',
                referrer: document.referrer,
                openerUrl: hasOpener ? (window.opener.location ? window.opener.location.href : 'unknown') : null,
                parentUrl: hasParent ? (window.parent.location ? window.parent.location.href : 'unknown') : null
            };
        },

        /**
         * Check if opened via custom popup manager
         * @returns {boolean} True if opened via custom popup manager
         */
        isCustomPopup: function() {
            // Check if we have popup data in storage (primary method)
            const hasPopupData = localStorage.getItem(this.storageKey) !== null;

            // Check window name pattern
            const hasCustomTarget = window.name && window.name.startsWith('custom-popup');

            // Check if opened via window.open with specific parameters
            const hasOpener = window.opener !== null;
            const isNewWindow = hasOpener && window.parent === window;

            // Check for popup-specific window features (if available)
            const hasPopupFeatures = this.checkPopupFeatures();

            return hasPopupData || hasCustomTarget || (hasOpener && isNewWindow && hasPopupFeatures);
        },

        /**
         * Check for popup-specific window features
         * @returns {boolean} True if window has popup features
         */
        checkPopupFeatures: function() {
            try {
                // Check if window has popup-like characteristics
                const hasSmallSize = window.innerWidth < 1200 || window.innerHeight < 800;
                const hasNoHistory = window.history.length <= 1;
                const hasOpener = window.opener !== null;

                // Check if window was opened with specific features
                const isResizable = window.outerWidth !== window.innerWidth || window.outerHeight !== window.innerHeight;
                const hasScrollbars = window.innerWidth < document.body.scrollWidth || window.innerHeight < document.body.scrollHeight;

                return hasOpener && (hasSmallSize || hasNoHistory);
            } catch (error) {
                return false;
            }
        },

        /**
         * Get popup layout configuration
         * @returns {Object} Layout configuration
         */
        getLayoutConfig: function() {
            const popupInfo = this.getPopupInfo();
            const isCustomPopup = this.isCustomPopup();

            return {
                isPopup: popupInfo.isPopup,
                isCustomPopup: isCustomPopup,
                layout: isCustomPopup ? 'popup' : 'normal',
                showHeader: !isCustomPopup,
                showFooter: !isCustomPopup,
                showSidebar: !isCustomPopup,
                fullWidth: isCustomPopup,
                compactMode: isCustomPopup,
                windowInfo: popupInfo
            };
        },

        /**
         * Get popup dimensions
         * @returns {Object} Object with width and height
         */
        getDimensions: function() {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            };
        },

        /**
         * Resize popup
         * @param {number} width - New width
         * @param {number} height - New height
         */
        resize: function(width, height) {
            try {
                window.resizeTo(width, height);
            } catch (error) {
                console.error('Error resizing popup:', error);
            }
        },

        /**
         * Move popup
         * @param {number} x - X coordinate
         * @param {number} y - Y coordinate
         */
        move: function(x, y) {
            try {
                window.moveTo(x, y);
            } catch (error) {
                console.error('Error moving popup:', error);
            }
        },

        /**
         * Center popup on screen
         */
        center: function() {
            try {
                const screenWidth = screen.availWidth;
                const screenHeight = screen.availHeight;
                const windowWidth = window.outerWidth || window.innerWidth;
                const windowHeight = window.outerHeight || window.innerHeight;

                const x = Math.max(0, (screenWidth - windowWidth) / 2);
                const y = Math.max(0, (screenHeight - windowHeight) / 2);

                this.move(x, y);
            } catch (error) {
                console.error('Error centering popup:', error);
            }
        },

    };

    // Initialize when document is ready
    $(document).ready(function() {
        PopupReceiver.init();
    });

    // Expose to global scope
    window.PopupReceiver = PopupReceiver;

    // Legacy global variables for backward compatibility
    window.popupData = PopupReceiver.popupData;
    window.closeHandler = PopupReceiver.closeHandler;

})(jQuery);
