/**
 * Project State Management
 * 
 * Zustand store for managing project state across the application.
 * Handles CRUD operations, active project selection, and localStorage persistence.
 */

import { create } from 'zustand';
import { projectAPI } from '../api/projectAPI';
import { validateProject } from '../utils/projectHelpers';

export const useProjectStore = create((set, get) => ({
  // State
  projects: [],
  activeProjectId: null,
  isLoading: false,
  error: null,

  // Actions

  /**
   * Load all projects from storage
   */
  loadProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const projects = await projectAPI.getAll();
      set({ projects, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  /**
   * Create a new project
   * @param {Object} projectData - Project data
   * @returns {Promise<Object>} Created project
   */
  createProject: async (projectData) => {
    set({ error: null });

    // Validate project data
    const validation = validateProject(projectData);
    if (!validation.isValid) {
      const error = validation.errors.join(', ');
      set({ error });
      throw new Error(error);
    }

    try {
      const newProject = await projectAPI.create(projectData);
      
      // Optimistic update
      set(state => ({
        projects: [...state.projects, newProject]
      }));

      return newProject;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  /**
   * Update an existing project
   * @param {string} id - Project ID
   * @param {Object} updates - Partial project data
   * @returns {Promise<Object|null>} Updated project or null
   */
  updateProject: async (id, updates) => {
    set({ error: null });

    // Validate updates if they include critical fields
    if (updates.name !== undefined) {
      const validation = validateProject({ ...get().projects.find(p => p.id === id), ...updates });
      if (!validation.isValid) {
        const error = validation.errors.join(', ');
        set({ error });
        throw new Error(error);
      }
    }

    try {
      const updatedProject = await projectAPI.update(id, updates);
      
      if (!updatedProject) {
        throw new Error('Project not found');
      }

      // Optimistic update
      set(state => ({
        projects: state.projects.map(p => 
          p.id === id ? updatedProject : p
        )
      }));

      return updatedProject;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  /**
   * Delete a project
   * @param {string} id - Project ID
   * @returns {Promise<boolean>} True if deleted
   */
  deleteProject: async (id) => {
    set({ error: null });

    try {
      const deleted = await projectAPI.delete(id);
      
      if (!deleted) {
        throw new Error('Project not found');
      }

      // Optimistic update
      set(state => ({
        projects: state.projects.filter(p => p.id !== id),
        activeProjectId: state.activeProjectId === id ? null : state.activeProjectId
      }));

      return true;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  /**
   * Set the active project
   * @param {string|null} id - Project ID or null to clear
   */
  setActiveProject: (id) => {
    set({ activeProjectId: id });
  },

  /**
   * Get the active project object
   * @returns {Object|null} Active project or null
   */
  getActiveProject: () => {
    const { projects, activeProjectId } = get();
    return projects.find(p => p.id === activeProjectId) || null;
  },

  /**
   * Link a chat to a project
   * @param {string} projectId - Project ID
   * @param {Object} chatData - Chat reference data
   * @returns {Promise<Object|null>} Updated project or null
   */
  linkChatToProject: async (projectId, chatData) => {
    set({ error: null });

    try {
      const updatedProject = await projectAPI.linkChat(projectId, chatData);
      
      if (!updatedProject) {
        throw new Error('Project not found');
      }

      // Optimistic update
      set(state => ({
        projects: state.projects.map(p => 
          p.id === projectId ? updatedProject : p
        )
      }));

      return updatedProject;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  /**
   * Unlink a chat from a project
   * @param {string} projectId - Project ID
   * @param {string} chatId - Chat ID
   * @returns {Promise<Object|null>} Updated project or null
   */
  unlinkChatFromProject: async (projectId, chatId) => {
    set({ error: null });

    try {
      const updatedProject = await projectAPI.unlinkChat(projectId, chatId);
      
      if (!updatedProject) {
        throw new Error('Project not found');
      }

      // Optimistic update
      set(state => ({
        projects: state.projects.map(p => 
          p.id === projectId ? updatedProject : p
        )
      }));

      return updatedProject;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  /**
   * Archive a project
   * @param {string} id - Project ID
   * @returns {Promise<Object|null>} Updated project or null
   */
  archiveProject: async (id) => {
    return await get().updateProject(id, { isArchived: true });
  },

  /**
   * Unarchive a project
   * @param {string} id - Project ID
   * @returns {Promise<Object|null>} Updated project or null
   */
  unarchiveProject: async (id) => {
    return await get().updateProject(id, { isArchived: false });
  },

  /**
   * Duplicate a project
   * @param {string} id - Project ID to duplicate
   * @returns {Promise<Object|null>} New project or null
   */
  duplicateProject: async (id) => {
    set({ error: null });

    try {
      const duplicated = await projectAPI.duplicate(id);
      
      if (!duplicated) {
        throw new Error('Project not found');
      }

      // Add to state
      set(state => ({
        projects: [...state.projects, duplicated]
      }));

      return duplicated;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  /**
   * Export all projects
   * @returns {Promise<string>} JSON string
   */
  exportProjects: async () => {
    try {
      return await projectAPI.exportAll();
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  /**
   * Import projects
   * @param {string} jsonString - JSON string of projects
   * @returns {Promise<Object>} Import result
   */
  importProjects: async (jsonString) => {
    set({ error: null });

    try {
      const result = await projectAPI.importProjects(jsonString);
      
      if (result.success) {
        // Reload all projects
        await get().loadProjects();
      } else {
        set({ error: result.error });
      }

      return result;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  /**
   * Clear error state
   */
  clearError: () => {
    set({ error: null });
  }
}));
