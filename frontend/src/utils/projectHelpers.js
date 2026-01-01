/**
 * Utility functions for project management
 */

/**
 * Generate a unique ID for projects
 * @returns {string} A unique identifier
 */
export function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Format a timestamp for display
 * @param {string|number} timestamp - ISO string or unix timestamp
 * @returns {string} Formatted date string
 */
export function formatDate(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    if (diffHours === 0) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return diffMinutes <= 1 ? 'Just now' : `${diffMinutes} minutes ago`;
    }
    return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
  }

  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  });
}

/**
 * Format a full date with time
 * @param {string|number} timestamp - ISO string or unix timestamp
 * @returns {string} Formatted date and time string
 */
export function formatDateTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Validate project data
 * @param {Object} project - Project object to validate
 * @returns {Object} { isValid: boolean, errors: string[] }
 */
export function validateProject(project) {
  const errors = [];

  if (!project.name || project.name.trim().length === 0) {
    errors.push('Project name is required');
  }

  if (project.name && project.name.length > 100) {
    errors.push('Project name must be 100 characters or less');
  }

  if (project.description && project.description.length > 500) {
    errors.push('Description must be 500 characters or less');
  }

  if (project.color && !/^#[0-9A-F]{6}$/i.test(project.color)) {
    errors.push('Color must be a valid hex color code');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Search projects by query string
 * @param {Array} projects - Array of project objects
 * @param {string} query - Search query
 * @returns {Array} Filtered projects
 */
export function searchProjects(projects, query) {
  if (!query || query.trim() === '') return projects;

  const lowerQuery = query.toLowerCase();
  
  return projects.filter(project => {
    const searchableText = [
      project.name,
      project.description,
      ...(project.tags || [])
    ].join(' ').toLowerCase();

    return searchableText.includes(lowerQuery);
  });
}

/**
 * Sort projects by specified field
 * @param {Array} projects - Array of project objects
 * @param {string} sortBy - Field to sort by (name, createdAt, updatedAt)
 * @param {string} order - Sort order (asc, desc)
 * @returns {Array} Sorted projects
 */
export function sortProjects(projects, sortBy = 'updatedAt', order = 'desc') {
  const sorted = [...projects].sort((a, b) => {
    let aVal = a[sortBy];
    let bVal = b[sortBy];

    if (sortBy === 'name') {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }

    if (order === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  return sorted;
}

/**
 * Filter projects by tags
 * @param {Array} projects - Array of project objects
 * @param {Array} tags - Tags to filter by
 * @returns {Array} Filtered projects
 */
export function filterByTags(projects, tags) {
  if (!tags || tags.length === 0) return projects;

  return projects.filter(project => {
    return tags.some(tag => project.tags?.includes(tag));
  });
}

/**
 * Export project to JSON
 * @param {Object} project - Project object
 * @returns {string} JSON string
 */
export function exportProject(project) {
  return JSON.stringify(project, null, 2);
}

/**
 * Import project from JSON
 * @param {string} jsonString - JSON string
 * @returns {Object} { success: boolean, project?: Object, error?: string }
 */
export function importProject(jsonString) {
  try {
    const project = JSON.parse(jsonString);
    const validation = validateProject(project);
    
    if (!validation.isValid) {
      return {
        success: false,
        error: validation.errors.join(', ')
      };
    }

    // Generate new ID to avoid conflicts
    project.id = generateId();
    project.createdAt = new Date().toISOString();
    project.updatedAt = new Date().toISOString();

    return {
      success: true,
      project
    };
  } catch (error) {
    return {
      success: false,
      error: 'Invalid JSON format'
    };
  }
}

/**
 * Get all unique tags from projects
 * @param {Array} projects - Array of project objects
 * @returns {Array} Array of unique tag strings
 */
export function getAllTags(projects) {
  const tagSet = new Set();
  
  projects.forEach(project => {
    if (project.tags) {
      project.tags.forEach(tag => tagSet.add(tag));
    }
  });

  return Array.from(tagSet).sort();
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength = 100) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Generate a random color from Material Design 3 palette
 * @returns {string} Hex color code
 */
export function getRandomColor() {
  const colors = [
    '#d0bcff', // primary
    '#4fd8eb', // secondary
    '#ffb4ab', // tertiary
    '#81c784', // success
    '#ffb74d', // warning
    '#64b5f6', // info
  ];
  
  return colors[Math.floor(Math.random() * colors.length)];
}
