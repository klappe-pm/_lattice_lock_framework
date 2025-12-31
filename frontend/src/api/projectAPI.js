/**
 * Project API Layer
 * 
 * This module provides an abstraction layer for project data persistence.
 * Currently implements localStorage, but can be easily swapped to HTTP API calls.
 */

const STORAGE_KEY = 'lattice_lock_projects';

/**
 * Get all projects from storage
 * @returns {Promise<Array>} Array of project objects
 */
async function getAll() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error reading projects from localStorage:', error);
    return [];
  }
}

/**
 * Get a single project by ID
 * @param {string} id - Project ID
 * @returns {Promise<Object|null>} Project object or null if not found
 */
async function getById(id) {
  const projects = await getAll();
  return projects.find(p => p.id === id) || null;
}

/**
 * Create a new project
 * @param {Object} project - Project object
 * @returns {Promise<Object>} Created project with generated ID and timestamps
 */
async function create(project) {
  const projects = await getAll();
  
  const newProject = {
    ...project,
    id: project.id || `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    linkedChats: project.linkedChats || [],
    tags: project.tags || [],
    isArchived: false
  };

  projects.push(newProject);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
  
  return newProject;
}

/**
 * Update an existing project
 * @param {string} id - Project ID
 * @param {Object} updates - Partial project object with updates
 * @returns {Promise<Object|null>} Updated project or null if not found
 */
async function update(id, updates) {
  const projects = await getAll();
  const index = projects.findIndex(p => p.id === id);
  
  if (index === -1) {
    return null;
  }

  projects[index] = {
    ...projects[index],
    ...updates,
    id, // Ensure ID doesn't change
    createdAt: projects[index].createdAt, // Preserve creation date
    updatedAt: new Date().toISOString()
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
  
  return projects[index];
}

/**
 * Delete a project
 * @param {string} id - Project ID
 * @returns {Promise<boolean>} True if deleted, false if not found
 */
async function deleteProject(id) {
  const projects = await getAll();
  const filtered = projects.filter(p => p.id !== id);
  
  if (filtered.length === projects.length) {
    return false; // Project not found
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  return true;
}

/**
 * Link a chat/conversation to a project
 * @param {string} projectId - Project ID
 * @param {Object} chatData - Chat reference object
 * @returns {Promise<Object|null>} Updated project or null if not found
 */
async function linkChat(projectId, chatData) {
  const project = await getById(projectId);
  
  if (!project) {
    return null;
  }

  const linkedChats = project.linkedChats || [];
  
  // Check if chat is already linked
  if (linkedChats.some(chat => chat.id === chatData.id)) {
    return project;
  }

  linkedChats.push({
    id: chatData.id,
    title: chatData.title,
    timestamp: chatData.timestamp || new Date().toISOString(),
    summary: chatData.summary || '',
    turns: chatData.turns || 0
  });

  return await update(projectId, { linkedChats });
}

/**
 * Unlink a chat from a project
 * @param {string} projectId - Project ID
 * @param {string} chatId - Chat ID
 * @returns {Promise<Object|null>} Updated project or null if not found
 */
async function unlinkChat(projectId, chatId) {
  const project = await getById(projectId);
  
  if (!project) {
    return null;
  }

  const linkedChats = (project.linkedChats || []).filter(chat => chat.id !== chatId);
  
  return await update(projectId, { linkedChats });
}

/**
 * Archive a project (soft delete)
 * @param {string} id - Project ID
 * @returns {Promise<Object|null>} Updated project or null if not found
 */
async function archive(id) {
  return await update(id, { isArchived: true });
}

/**
 * Unarchive a project
 * @param {string} id - Project ID
 * @returns {Promise<Object|null>} Updated project or null if not found
 */
async function unarchive(id) {
  return await update(id, { isArchived: false });
}

/**
 * Duplicate a project
 * @param {string} id - Project ID to duplicate
 * @returns {Promise<Object|null>} New project or null if source not found
 */
async function duplicate(id) {
  const project = await getById(id);
  
  if (!project) {
    return null;
  }

  const duplicated = {
    ...project,
    name: `${project.name} (Copy)`,
    linkedChats: [] // Don't copy linked chats
  };

  delete duplicated.id; // Will be regenerated
  
  return await create(duplicated);
}

/**
 * Export all projects as JSON
 * @returns {Promise<string>} JSON string of all projects
 */
async function exportAll() {
  const projects = await getAll();
  return JSON.stringify(projects, null, 2);
}

/**
 * Import projects from JSON (merges with existing)
 * @param {string} jsonString - JSON string of projects array
 * @returns {Promise<Object>} { success: boolean, count?: number, error?: string }
 */
async function importProjects(jsonString) {
  try {
    const importedProjects = JSON.parse(jsonString);
    
    if (!Array.isArray(importedProjects)) {
      return {
        success: false,
        error: 'Invalid format: expected an array of projects'
      };
    }

    const existingProjects = await getAll();
    
    // Generate new IDs to avoid conflicts
    const processedProjects = importedProjects.map(p => ({
      ...p,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }));

    const merged = [...existingProjects, ...processedProjects];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));

    return {
      success: true,
      count: processedProjects.length
    };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to import projects'
    };
  }
}

/**
 * Clear all projects (use with caution!)
 * @returns {Promise<void>}
 */
async function clear() {
  localStorage.removeItem(STORAGE_KEY);
}

export const projectAPI = {
  getAll,
  getById,
  create,
  update,
  delete: deleteProject,
  linkChat,
  unlinkChat,
  archive,
  unarchive,
  duplicate,
  exportAll,
  importProjects,
  clear
};
