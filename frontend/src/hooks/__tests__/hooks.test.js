import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import useModels from '../useModels';
import useExecution from '../useExecution';
import useProjects from '../useProjects';
import { modelsApi } from '../../api/models';
import { projectAPI } from '../../api/projectAPI';
import { orchestratorApi } from '../../api/orchestrator';

// Mock APIs
vi.mock('../../api/models', () => ({
    modelsApi: {
        getAll: vi.fn(),
        testConnection: vi.fn(),
    }
}));

vi.mock('../../api/projectAPI', () => ({
    projectAPI: {
        getAll: vi.fn(),
        create: vi.fn(),
        update: vi.fn(),
        delete: vi.fn(),
    }
}));

vi.mock('../../api/orchestrator', () => ({
    orchestratorApi: {
        execute: vi.fn(),
        getHistory: vi.fn(),
    }
}));

// Mock Stores
const mockSetLoading = vi.fn();
const mockSetModels = vi.fn();
const mockSetProjects = vi.fn();
const mockSetIsExecuting = vi.fn();
const mockSetResult = vi.fn();
const mockAddToHistory = vi.fn();

vi.mock('../../store', () => ({
    useModelsStore: vi.fn(() => ({
        models: [],
        loading: false,
        setModels: mockSetModels,
        setLoading: mockSetLoading,
    })),
    useProjectsStore: vi.fn(() => ({
        projects: [],
        loading: false,
        setProjects: mockSetProjects,
        setLoading: mockSetLoading,
        addProject: vi.fn(),
        updateProject: vi.fn(),
        deleteProject: vi.fn(),
    })),
    useExecutionStore: vi.fn(() => ({
        isExecuting: false,
        setIsExecuting: mockSetIsExecuting,
        setResult: mockSetResult,
        addToHistory: mockAddToHistory,
    })),
}));

describe('Custom Hooks', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    // ... useModels and useProjects tests remain the same (implicit) ...
    // Note: To avoid overwriting them, I should probably use multi_replace or include them.
    // Since I'm using replace_file_content with range, I need to be careful.
    // The previous content ended at line 35 for mocks.
    // I will replace from line 35 to the end of the file.
    
    describe('useModels', () => {
        it('should fetch models on mount', async () => {
             modelsApi.getAll.mockResolvedValue([{ id: 'm1', name: 'M1' }]);
             
             const { result } = renderHook(() => useModels());
             
             await waitFor(() => {
                 expect(mockSetModels).toHaveBeenCalledWith(expect.arrayContaining([expect.objectContaining({ id: 'm1' })]));
             });
        });
        
        it('should handle fetch error', async () => {
            modelsApi.getAll.mockRejectedValue(new Error('Failed'));
            const { result } = renderHook(() => useModels());
            
            await waitFor(() => {
                 expect(mockSetLoading).toHaveBeenCalledWith(false);
            });
        });

        it('should refresh models', async () => {
             modelsApi.getAll.mockResolvedValue([{ id: 'm1' }]);
             const { result } = renderHook(() => useModels());
             
             await waitFor(() => expect(mockSetModels).toHaveBeenCalled());
             
             modelsApi.getAll.mockResolvedValue([{ id: 'm1' }, { id: 'm2' }]);
             await result.current.refreshModels();
             
             await waitFor(() => expect(modelsApi.getAll).toHaveBeenCalledTimes(2));
        });
    });

    describe('useProjects', () => {
        it('should fetch projects on mount', async () => {
            projectAPI.getAll.mockResolvedValue([{ id: 'p1' }]);
            const { result } = renderHook(() => useProjects());
            
            await waitFor(() => {
                expect(mockSetProjects).toHaveBeenCalledWith(expect.arrayContaining([expect.objectContaining({ id: 'p1' })]));
            });
        });

        it('should create project', async () => {
            projectAPI.getAll.mockResolvedValue([]);
            projectAPI.create.mockResolvedValue({ id: 'p2', name: 'New' });
            
            const { result } = renderHook(() => useProjects());
            await result.current.createProject({ name: 'New' });
            
            expect(projectAPI.create).toHaveBeenCalledWith({ name: 'New' });
        });
    });
    
    describe('useExecution', () => {
        it('should provide execution methods', () => {
            const { result } = renderHook(() => useExecution());
            expect(result.current.executePrompt).toBeDefined();
            expect(result.current.isExecuting).toBeDefined();
        });

        it('should execute prompt', async () => {
            orchestratorApi.execute.mockResolvedValue({ response: 'AI Response' });
            const { result } = renderHook(() => useExecution());
            
            await result.current.executePrompt('test prompt', 'system instr', 'gpt-4');
            
            expect(mockSetIsExecuting).toHaveBeenCalledWith(true);
            expect(orchestratorApi.execute).toHaveBeenCalledWith({
                prompt: 'test prompt',
                system_instructions: 'system instr',
                model: 'gpt-4'
            });
            expect(mockSetResult).toHaveBeenCalledWith({ response: 'AI Response' });
            expect(mockAddToHistory).toHaveBeenCalledTimes(2); // User + Assistant
            expect(mockSetIsExecuting).toHaveBeenCalledWith(false);
        });

        it('should handle result with data property and default model', async () => {
            orchestratorApi.execute.mockResolvedValue({ data: 'Data Response' });
            const { result } = renderHook(() => useExecution());
            
            await result.current.executePrompt('test prompt'); // No model/system provided
            
            expect(mockAddToHistory).toHaveBeenLastCalledWith(expect.objectContaining({
                content: 'Data Response',
                model: 'auto'
            }));
        });

        it('should handle generic object result', async () => {
            const genericResult = { some: 'value' };
            orchestratorApi.execute.mockResolvedValue(genericResult);
            const { result } = renderHook(() => useExecution());
            
            await result.current.executePrompt('test prompt');
            
            expect(mockAddToHistory).toHaveBeenLastCalledWith(expect.objectContaining({
                content: JSON.stringify(genericResult)
            }));
        });

        it('should handle execution error', async () => {
            orchestratorApi.execute.mockRejectedValue(new Error('API Fail'));
            const { result } = renderHook(() => useExecution());
            
            await result.current.executePrompt('test prompt');
            
            expect(mockSetResult).toHaveBeenCalledWith({ error: 'API Fail' });
            expect(mockSetIsExecuting).toHaveBeenCalledWith(false);
        });
        
        it('should ignore empty prompt', async () => {
            const { result } = renderHook(() => useExecution());
            await result.current.executePrompt('   ');
            expect(orchestratorApi.execute).not.toHaveBeenCalled();
        });
    });
});
