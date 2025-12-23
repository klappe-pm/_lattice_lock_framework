/**
 * Shared utility functions and constants for the Lattice Lock Dashboard.
 */

export const CONSTANTS = {
    MAX_RECONNECT_ATTEMPTS: 5,
    RECONNECT_DELAY_MS: 3000,
    AUTO_REFRESH_INTERVAL_MS: 30000,
    ANIMATION_DURATION_MS: 300
};

/**
 * Formats a timestamp into a relative time string (e.g., "5m ago").
 * @param {string} isoString - ISO 8601 date string.
 * @returns {string} Formatted time string.
 */
export function formatTime(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
}

/**
 * Escapes HTML characters to prevent XSS.
 * @param {string} str - The string to escape.
 * @returns {string} Escaped string.
 */
export function escapeHtml(str) {
    if (typeof str !== 'string') return str;
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
