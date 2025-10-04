/**
 * Enhanced Custom Popup Manager
 *
 * This module provides a robust popup management system with the following features:
 * - Data passing between parent and popup windows
 * - Customizable popup dimensions and positioning
 * - Multiple layout support (empty, admin)
 * - Event handling and callbacks
 * - Error handling and validation
 * - Popup state management
 * - Cross-browser compatibility
 *
 * Usage:
 * Add the 'custom-popup-page' attribute to any element to enable popup functionality.
 *
 * Available attributes:
 * - custom-popup-page-url: URL to open in popup (required)
 * - custom-popup-page-width: Popup width (default: 1000)
 * - custom-popup-page-height: Popup height (default: 700)
 * - custom-popup-page-data: Global variable name containing data to pass
 * - custom-popup-page-handler: Function name to call when popup closes
 * - custom-popup-page-target: Popup window target name (default: 'custom-popup')
 * - custom-popup-page-layout: Layout type - 'empty' or 'admin' (default: 'empty')
 * - custom-popup-page-center: Center popup on screen (default: true)
 * - custom-popup-page-toolbar: Show toolbar (default: false)
 * - custom-popup-page-menubar: Show menubar (default: false)
 * - custom-popup-page-location: Show location bar (default: false)
 */

(function($) {
    'use strict';

    // Popup manager configuration
    const PopupManager = {
        // Default configuration
        defaults: {
            width: 1000,
            height: 700,
            target: 'custom-popup',
            layout: 'empty',
            center: true,
            toolbar: false,
            menubar: false,
            location: false,
            dataKey: 'popupData',
            handlerKey: 'closeHandler'
        },

        // Active popup windows
        activePopups: new Map(),

        // Storage key for popup data
        storageKey: 'customPopupWindow',

        /**
         * Initialize the popup manager
         */
        init: function() {
            this.bindEvents();
            this.setupStorageListener();
            console.log('Custom Popup Manager initialized');
        },

        /**
         * Bind click events to elements with custom-popup-page attribute
         */
        bindEvents: function() {
            const self = this;

            // Use event delegation for dynamic content
            $(document).on('click', '[custom-popup-page]', function(e) {
                e.preventDefault();
                self.openPopup($(this));
            });

            // Handle popup close events
            $(window).on('beforeunload', function() {
                self.cleanup();
            });
        },

        /**
         * Setup storage listener for popup communication
         */
        setupStorageListener: function() {
            const self = this;

            // Listen for storage changes (popup communication)
            $(window).on('storage', function(e) {
                if (e.originalEvent.key === self.storageKey) {
                    self.handlePopupMessage(e.originalEvent);
                }
            });

            // Listen for popup close messages
            $(window).on('message', function(e) {
                if (e.originalEvent.data && e.originalEvent.data.type === 'popup-close') {
                    self.handlePopupClose(e.originalEvent.data);
                }
            });
        },

        /**
         * Open a popup window
         * @param {jQuery} $element - The element that triggered the popup
         */
        openPopup: function($element) {
            try {
                const config = this.getPopupConfig($element);

                // Validate configuration
                if (!this.validateConfig(config)) {
                    return;
                }

                // Prepare popup URL
                const popupUrl = this.preparePopupUrl(config);

                // Calculate popup position
                const position = this.calculatePosition(config);

                // Build popup parameters
                const params = this.buildPopupParams(config, position);

                // Prepare data for popup
                const popupData = this.preparePopupData(config);

                // Store data in localStorage
                this.storePopupData(popupData, config.handler);

                // Debug: Log the parameters being used
                console.log('Popup parameters:', params);
                console.log('Popup config:', config);

                // Open popup window
                const popupWindow = this.openWindow(popupUrl, config.target, params);

                if (popupWindow) {
                    // Store popup reference
                    this.activePopups.set(config.target, {
                        window: popupWindow,
                        config: config,
                        element: $element
                    });

                    // Focus popup
                    popupWindow.focus();

                    // Setup popup monitoring
                    this.monitorPopup(config.target, popupWindow);

                    console.log('Popup opened:', config.target, popupUrl);
                } else {
                    this.showError('Failed to open popup. Please check your popup blocker settings.');
                }

            } catch (error) {
                console.error('Error opening popup:', error);
                this.showError('An error occurred while opening the popup.');
            }
        },

        /**
         * Get popup configuration from element attributes
         * @param {jQuery} $element - The element
         * @returns {Object} Configuration object
         */
        getPopupConfig: function($element) {
            const config = Object.assign({}, this.defaults);

            // Required attributes
            config.url = $element.attr('custom-popup-page-url');

            // Optional attributes with validation
            const width = $element.attr('custom-popup-page-width');
            if (width && !isNaN(width) && parseInt(width) > 0) {
                config.width = parseInt(width);
            }

            const height = $element.attr('custom-popup-page-height');
            if (height && !isNaN(height) && parseInt(height) > 0) {
                config.height = parseInt(height);
            }

            config.target = $element.attr('custom-popup-page-target') || config.target;
            config.layout = $element.attr('custom-popup-page-layout') || config.layout;
            config.dataKey = $element.attr('custom-popup-page-data') || config.dataKey;
            config.handler = $element.attr('custom-popup-page-handler');

            // Boolean attributes
            config.center = this.parseBoolean($element.attr('custom-popup-page-center'), config.center);
            config.toolbar = this.parseBoolean($element.attr('custom-popup-page-toolbar'), config.toolbar);
            config.menubar = this.parseBoolean($element.attr('custom-popup-page-menubar'), config.menubar);
            config.location = this.parseBoolean($element.attr('custom-popup-page-location'), config.location);

            return config;
        },

        /**
         * Parse boolean attribute value
         * @param {string} value - Attribute value
         * @param {boolean} defaultValue - Default value
         * @returns {boolean}
         */
        parseBoolean: function(value, defaultValue) {
            if (value === null || value === undefined) {
                return defaultValue;
            }
            return value === 'true' || value === '1' || value === 'yes';
        },

        /**
         * Validate popup configuration
         * @param {Object} config - Configuration object
         * @returns {boolean} True if valid
         */
        validateConfig: function(config) {
            if (!config.url) {
                this.showError('Popup URL is required. Please set the custom-popup-page-url attribute.');
                return false;
            }

            if (config.width < 100 || config.width > 4000) {
                this.showError('Popup width must be between 100 and 4000 pixels.');
                return false;
            }

            if (config.height < 100 || config.height > 4000) {
                this.showError('Popup height must be between 100 and 4000 pixels.');
                return false;
            }

            if (!['empty', 'admin'].includes(config.layout)) {
                this.showError('Invalid layout. Must be "empty" or "admin".');
                return false;
            }

            return true;
        },

        /**
         * Prepare popup URL with layout parameter
         * @param {Object} config - Configuration object
         * @returns {string} Prepared URL
         */
        preparePopupUrl: function(config) {
            let url = config.url;
            const separator = url.includes('?') ? '&' : '?';

            if (config.layout === 'empty') {
                url += separator + 'popup_page=True';
            }

            return url;
        },

        /**
         * Calculate popup position
         * @param {Object} config - Configuration object
         * @returns {Object} Position object with x, y coordinates
         */
        calculatePosition: function(config) {
            if (!config.center) {
                return { x: 0, y: 0 };
            }

            const screenWidth = window.screen.availWidth;
            const screenHeight = window.screen.availHeight;
            const windowWidth = window.outerWidth || window.innerWidth;
            const windowHeight = window.outerHeight || window.innerHeight;

            const x = Math.max(0, (screenWidth - config.width) / 2);
            const y = Math.max(0, (screenHeight - config.height) / 2);

            return { x: Math.round(x), y: Math.round(y) };
        },

        /**
         * Build popup window parameters
         * @param {Object} config - Configuration object
         * @param {Object} position - Position object
         * @returns {string} Window parameters string
         */
        buildPopupParams: function(config, position) {
            const params = [];

            // Basic dimensions and position
            params.push(`width=${config.width}`);
            params.push(`height=${config.height}`);
            params.push(`left=${position.x}`);
            params.push(`top=${position.y}`);

            // Window features
            if (config.location) {
                params.push('location=yes');
            } else {
                params.push('location=no');
            }

            if (config.toolbar) {
                params.push('toolbar=yes');
                params.push('directories=yes');
            } else {
                params.push('toolbar=no');
                params.push('directories=no');
            }

            if (config.menubar) {
                params.push('menubar=yes');
            } else {
                params.push('menubar=no');
            }

            // Additional parameters for better control
            params.push('scrollbars=no');
            params.push('resizable=no');
            params.push('status=no');
            params.push('copyhistory=no');
            params.push('noopener=no');
            params.push('noreferrer=no');

            return params.join(',');
        },

        /**
         * Prepare data to pass to popup
         * @param {Object} config - Configuration object
         * @returns {Object} Data object
         */
        preparePopupData: function(config) {
            let data = {};

            if (config.dataKey && window[config.dataKey]) {
                data = window[config.dataKey];
            }

            return data;
        },

        /**
         * Store popup data in localStorage
         * @param {Object} data - Data to store
         * @param {string} handler - Handler function name
         */
        storePopupData: function(data, handler) {
            try {
                const popupData = {
                    popupData: data,
                    handler: handler,
                    timestamp: Date.now()
                };

                localStorage.setItem(this.storageKey, JSON.stringify(popupData));
            } catch (error) {
                console.error('Error storing popup data:', error);
            }
        },

        /**
         * Open popup window
         * @param {string} url - URL to open
         * @param {string} target - Window target name
         * @param {string} params - Window parameters
         * @returns {Window|null} Popup window or null
         */
        openWindow: function(url, target, params) {
            try {
                return window.open(url, target, params);
            } catch (error) {
                console.error('Error opening window:', error);
                return null;
            }
        },

        /**
         * Monitor popup window
         * @param {string} target - Window target name
         * @param {Window} popupWindow - Popup window reference
         */
        monitorPopup: function(target, popupWindow) {
            const self = this;
            const checkClosed = setInterval(function() {
                if (popupWindow.closed) {
                    clearInterval(checkClosed);
                    self.handlePopupClose({ target: target });
                }
            }, 1000);
        },

        /**
         * Handle popup close event
         * @param {Object} data - Close event data
         */
        handlePopupClose: function(data) {
            const target = data.target;
            const popupInfo = this.activePopups.get(target);

            if (popupInfo) {
                // Execute close handler if specified
                if (popupInfo.config.handler && typeof window[popupInfo.config.handler] === 'function') {
                    try {
                        window[popupInfo.config.handler](popupInfo.config, popupInfo.element);
                    } catch (error) {
                        console.error('Error executing close handler:', error);
                    }
                }

                // Remove from active popups
                this.activePopups.delete(target);

                // Clean up storage
                this.cleanupStorage();

                console.log('Popup closed:', target);
            }
        },

        /**
         * Handle popup message
         * @param {StorageEvent} event - Storage event
         */
        handlePopupMessage: function(event) {
            try {
                const data = JSON.parse(event.newValue);
                if (data && data.type === 'popup-close') {
                    this.handlePopupClose(data);
                }
            } catch (error) {
                console.error('Error handling popup message:', error);
            }
        },

        /**
         * Clean up popup data
         */
        cleanup: function() {
            this.activePopups.clear();
            this.cleanupStorage();
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
         * Show error message
         * @param {string} message - Error message
         */
        showError: function(message) {
            console.error('Popup Manager Error:', message);

            // You can customize this to show user-friendly error messages
            if (typeof alert !== 'undefined') {
                alert('Popup Error: ' + message);
            }
        },

        /**
         * Get active popup count
         * @returns {number} Number of active popups
         */
        getActivePopupCount: function() {
            return this.activePopups.size;
        },

        /**
         * Close specific popup
         * @param {string} target - Popup target name
         * @returns {boolean} True if closed successfully
         */
        closePopup: function(target) {
            const popupInfo = this.activePopups.get(target);
            if (popupInfo && popupInfo.window) {
                popupInfo.window.close();
                return true;
            }
            return false;
        },

        /**
         * Close all popups
         */
        closeAllPopups: function() {
            this.activePopups.forEach((popupInfo, target) => {
                if (popupInfo.window) {
                    popupInfo.window.close();
                }
            });
            this.cleanup();
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        PopupManager.init();
    });

    // Expose to global scope for external access
    window.CustomPopupManager = PopupManager;

})(jQuery);
