/**
 * Shared utility functions and constants for the Lattice Lock Dashboard.
 * @module utils
 */

/**
 * Application constants and configuration.
 * @constant
 * @type {Object}
 */
export const CONSTANTS = {
    /** Maximum number of WebSocket reconnection attempts. */
    MAX_RECONNECT_ATTEMPTS: 5,
    /** Base delay for WebSocket reconnection in ms. */
    RECONNECT_DELAY_MS: 3000,
    /** Interval for auto-refreshing data in ms. */
    AUTO_REFRESH_INTERVAL_MS: 30000,
    /** Default animation duration in ms. */
    ANIMATION_DURATION_MS: 300,
    /** WebSocket URL path */
    WS_PATH: '/ws/dashboard',
    /** Default host for WebSocket connection */
    DEFAULT_WS_HOST: 'localhost:8080'
};

/**
 * Formats a timestamp into a relative time string (e.g., "5m ago").
 * @param {string|Date} isoString - ISO 8601 date string or Date object.
 * @returns {string} Formatted time string.
 */
export function formatTime(isoString) {
    if (!isoString) return '';

    try {
        const date = new Date(isoString);
        // specific check also for "Invalid Date"
        if (isNaN(date.getTime())) return 'Invalid date';

        const now = new Date();
        const diff = now - date;

        if (diff < 0) return 'Just now'; // Handle slight client clock skew
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        console.error('Error formatting time:', e);
        return 'Unknown time';
    }
}

/**
 * Escapes HTML characters to prevent XSS.
 * @param {string} str - The string to escape.
 * @returns {string} Escaped string.
 */
export function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    if (typeof str !== 'string') return String(str);

    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
