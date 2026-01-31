import { describe, it, expect, beforeEach, vi } from 'vitest';
// Import directly from the file to ensure we hit the source code
import { useProjectStore } from '../projectStore';

// Mock API dependencies
vi.mock('../../api/projectAPI', () => ({
    projectAPI: {
        getAll: vi.fn(),
        create: vi.fn(),
        update: vi.fn(),
        delete: vi.fn(),
        linkChat: vi.fn(),
        unlinkChat: vi.fn(),
        archive: vi.fn(), // If implemented in API
        duplicate: vi.fn(),
        exportAll: vi.fn(),
        importProjects: vi.fn(),
    }
}));

// Mock utils if needed, or rely on real one
vi.mock('../../utils/projectHelpers', () => ({
    validateProject: vi.fn(() => ({ isValid: true, errors: [] }))
}));

import { projectAPI } from '../../api/projectAPI';
import { validateProject } from '../../utils/projectHelpers';

describe('useProjectStore', () => {
    beforeEach(() => {
        useProjectStore.setState({ 
            projects: [], 
            activeProjectId: null, 
            isLoading: false, 
            error: null 
        });
        vi.clearAllMocks();
        // Reset default mock implementations
        validateProject.mockReturnValue({ isValid: true, errors: [] });
    });

    it('should load projects successfully', async () => {
        const mockProjects = [{ id: '1', name: 'P1' }];
        projectAPI.getAll.mockResolvedValue(mockProjects);

        await useProjectStore.getState().loadProjects();

        expect(useProjectStore.getState().projects).toEqual(mockProjects);
        expect(useProjectStore.getState().isLoading).toBe(false);
        expect(useProjectStore.getState().error).toBeNull();
    });

    it('should handle load projects error', async () => {
        projectAPI.getAll.mockRejectedValue(new Error('Fetch failed'));

        await useProjectStore.getState().loadProjects();

        expect(useProjectStore.getState().error).toBe('Fetch failed');
        expect(useProjectStore.getState().isLoading).toBe(false);
    });

    it('should create project successfully', async () => {
        const newProject = { id: '2', name: 'New P' };
        projectAPI.create.mockResolvedValue(newProject);

        const result = await useProjectStore.getState().createProject({ name: 'New P' });

        expect(result).toEqual(newProject);
        expect(useProjectStore.getState().projects).toContainEqual(newProject);
    });

    it('should handle create validation error', async () => {
        validateProject.mockReturnValue({ isValid: false, errors: ['Invalid name'] });

        await expect(useProjectStore.getState().createProject({ name: '' }))
            .rejects.toThrow('Invalid name');
        
        expect(useProjectStore.getState().error).toBe('Invalid name');
        expect(projectAPI.create).not.toHaveBeenCalled();
    });

    it('should handle create API error', async () => {
        projectAPI.create.mockRejectedValue(new Error('Create failed'));

        await expect(useProjectStore.getState().createProject({ name: 'P' }))
            .rejects.toThrow('Create failed');
            
        expect(useProjectStore.getState().error).toBe('Create failed');
    });

    it('should update project successfully', async () => {
        const initial = { id: '1', name: 'Old' };
        useProjectStore.setState({ projects: [initial] });
        
        const updated = { ...initial, name: 'New' };
        projectAPI.update.mockResolvedValue(updated);

        const result = await useProjectStore.getState().updateProject('1', { name: 'New' });

        expect(result).toEqual(updated);
        expect(useProjectStore.getState().projects[0].name).toBe('New');
    });

    it('should handle update validation error', async () => {
        useProjectStore.setState({ projects: [{ id: '1', name: 'P' }] });
        validateProject.mockReturnValue({ isValid: false, errors: ['Bad Update'] });

        await expect(useProjectStore.getState().updateProject('1', { name: '' }))
            .rejects.toThrow('Bad Update');
    });

    it('should handle update missing project API response', async () => {
        useProjectStore.setState({ projects: [{ id: '1', name: 'P' }] });
        projectAPI.update.mockResolvedValue(null);

        await expect(useProjectStore.getState().updateProject('1', { name: 'N' }))
            .rejects.toThrow('Project not found');
    });

    it('should delete project successfully', async () => {
        useProjectStore.setState({ 
            projects: [{ id: '1' }], 
            activeProjectId: '1' 
        });
        projectAPI.delete.mockResolvedValue(true);

        await useProjectStore.getState().deleteProject('1');

        expect(useProjectStore.getState().projects).toHaveLength(0);
        expect(useProjectStore.getState().activeProjectId).toBeNull();
    });

    it('should setActiveProject', () => {
        useProjectStore.getState().setActiveProject('1');
        expect(useProjectStore.getState().activeProjectId).toBe('1');
    });

    it('should getActiveProject', () => {
        const p = { id: '1' };
        useProjectStore.setState({ projects: [p], activeProjectId: '1' });
        expect(useProjectStore.getState().getActiveProject()).toEqual(p);
    });

    it('should link chat to project', async () => {
        const p = { id: '1', linkedChats: [] };
        useProjectStore.setState({ projects: [p] });
        const updated = { ...p, linkedChats: [{ id: 'c1' }] };
        projectAPI.linkChat.mockResolvedValue(updated);

        await useProjectStore.getState().linkChatToProject('1', { id: 'c1' });
        
        expect(useProjectStore.getState().projects[0].linkedChats).toHaveLength(1);
    });

    it('should unlink chat from project', async () => {
        const p = { id: '1', linkedChats: [{ id: 'c1' }] };
        useProjectStore.setState({ projects: [p] });
        const updated = { ...p, linkedChats: [] };
        // Assume unlinkChat is called
        // Note: projectAPI mock definition above missed `unlinkChat`? No I added it.
        // Wait, did I? 
        // Yes: `unlinkChat: vi.fn(),`
        // But in projectStore.js it calls `projectAPI.unlinkChat`.
        projectAPI.unlinkChat.mockResolvedValue(updated);

        await useProjectStore.getState().unlinkChatFromProject('1', 'c1');
        
        expect(useProjectStore.getState().projects[0].linkedChats).toHaveLength(0);
    });

    it('should archive project', async () => {
         const p = { id: '1', isArchived: false };
         useProjectStore.setState({ projects: [p] });
         const updated = { ...p, isArchived: true };
         projectAPI.update.mockResolvedValue(updated);

         await useProjectStore.getState().archiveProject('1');
         // archiveProject calls updateProject internally
         // which calls projectAPI.update
         expect(useProjectStore.getState().projects[0].isArchived).toBe(true);
    });

    it('should duplicate project', async () => {
        const p = { id: '1' };
        const dup = { id: '2' };
        useProjectStore.setState({ projects: [p] });
        projectAPI.duplicate.mockResolvedValue(dup);

        await useProjectStore.getState().duplicateProject('1');
        
        expect(useProjectStore.getState().projects).toContainEqual(dup);
    });

    it('should export projects', async () => {
        projectAPI.exportAll.mockResolvedValue('json');
        const res = await useProjectStore.getState().exportProjects();
        expect(res).toBe('json');
    });

    it('should import projects', async () => {
        projectAPI.importProjects.mockResolvedValue({ success: true });
        projectAPI.getAll.mockResolvedValue([{ id: '1' }]); // Reloads after import

        await useProjectStore.getState().importProjects('{}');
        
        expect(projectAPI.importProjects).toHaveBeenCalled();
        expect(useProjectStore.getState().projects).toHaveLength(1);
    });

    it('should handle import failure', async () => {
        projectAPI.importProjects.mockResolvedValue({ success: false, error: 'Bad JSON' });
        
        await useProjectStore.getState().importProjects('{}');
        
        expect(useProjectStore.getState().error).toBe('Bad JSON');
    });
    
    it('should clear error', () => {
        useProjectStore.setState({ error: 'err' });
        useProjectStore.getState().clearError();
        expect(useProjectStore.getState().error).toBeNull();
    });
});
