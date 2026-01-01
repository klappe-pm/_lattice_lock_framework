import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

/**
 * Models Store - Manages registered models state
 */
export const useModelsStore = create(
  devtools(
    (set, get) => ({
      // State
      models: [],
      selectedModel: null,
      isLoading: false,
      error: null,

      // Actions
      setModels: (models) => set({ models, isLoading: false, error: null }),
      
      addModel: (model) =>
        set((state) => ({
          models: [...state.models, model],
        })),
      
      updateModel: (id, updates) =>
        set((state) => ({
          models: state.models.map((m) =>
            m.id === id ? { ...m, ...updates } : m
          ),
        })),
      
      removeModel: (id) =>
        set((state) => ({
          models: state.models.filter((m) => m.id !== id),
        })),
      
      setSelectedModel: (model) => set({ selectedModel: model }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      setError: (error) => set({ error, isLoading: false }),

      // Selectors
      getModelById: (id) => get().models.find((m) => m.id === id),
      
      getModelsByProvider: (provider) =>
        get().models.filter((m) => m.provider === provider),
      
      getOnlineModels: () =>
        get().models.filter((m) => m.status === 'online'),
    }),
    { name: 'models-store' }
  )
);

/**
 * Execution Store - Manages prompt execution state
 */
export const useExecutionStore = create(
  devtools(
    (set, get) => ({
      // State
      currentExecution: null,
      systemInstructions: '',
      conversationHistory: [],
      isExecuting: false,
      error: null,

      // Actions
      setSystemInstructions: (instructions) =>
        set({ systemInstructions: instructions }),

      startExecution: (executionId) =>
        set({
          currentExecution: {
            id: executionId,
            status: 'starting',
            startedAt: new Date().toISOString(),
          },
          isExecuting: true,
          error: null,
        }),

      updateExecution: (updates) =>
        set((state) => ({
          currentExecution: state.currentExecution
            ? { ...state.currentExecution, ...updates }
            : null,
        })),

      completeExecution: (result) =>
        set((state) => ({
          currentExecution: state.currentExecution
            ? {
                ...state.currentExecution,
                status: 'completed',
                result,
                completedAt: new Date().toISOString(),
              }
            : null,
          isExecuting: false,
        })),

      failExecution: (error) =>
        set((state) => ({
          currentExecution: state.currentExecution
            ? {
                ...state.currentExecution,
                status: 'failed',
                error,
                completedAt: new Date().toISOString(),
              }
            : null,
          isExecuting: false,
          error,
        })),

      addToHistory: (message) =>
        set((state) => ({
          conversationHistory: [...state.conversationHistory, message],
        })),

      clearHistory: () => set({ conversationHistory: [] }),

      reset: () =>
        set({
          currentExecution: null,
          isExecuting: false,
          error: null,
        }),
    }),
    { name: 'execution-store' }
  )
);

/**
 * Progress Store - Manages task progress and tracking
 */
export const useProgressStore = create(
  devtools(
    (set, get) => ({
      // State
      tasks: [],
      timeline: [],
      tokenUsage: {
        input: 0,
        output: 0,
        total: 0,
      },
      cost: 0,
      selectionFlow: null,

      // Actions
      setTasks: (tasks) => set({ tasks }),

      addTask: (task) =>
        set((state) => ({
          tasks: [
            ...state.tasks,
            {
              ...task,
              id: task.id || crypto.randomUUID(),
              status: task.status || 'pending',
              createdAt: new Date().toISOString(),
            },
          ],
        })),

      updateTask: (taskId, updates) =>
        set((state) => ({
          tasks: state.tasks.map((t) =>
            t.id === taskId ? { ...t, ...updates } : t
          ),
        })),

      addTimelineEvent: (event) =>
        set((state) => ({
          timeline: [
            ...state.timeline,
            {
              ...event,
              id: event.id || crypto.randomUUID(),
              timestamp: new Date().toISOString(),
            },
          ],
        })),

      updateTokenUsage: (usage) =>
        set((state) => ({
          tokenUsage: {
            input: state.tokenUsage.input + (usage.input || 0),
            output: state.tokenUsage.output + (usage.output || 0),
            total:
              state.tokenUsage.total +
              (usage.input || 0) +
              (usage.output || 0),
          },
        })),

      updateCost: (amount) =>
        set((state) => ({
          cost: state.cost + amount,
        })),

      setSelectionFlow: (flow) => set({ selectionFlow: flow }),

      reset: () =>
        set({
          tasks: [],
          timeline: [],
          tokenUsage: { input: 0, output: 0, total: 0 },
          cost: 0,
          selectionFlow: null,
        }),

      // Selectors
      getTasksByStatus: (status) =>
        get().tasks.filter((t) => t.status === status),

      getCompletedTasks: () =>
        get().tasks.filter((t) => t.status === 'completed'),

      getPendingTasks: () =>
        get().tasks.filter((t) => t.status === 'pending'),

      getRunningTasks: () =>
        get().tasks.filter((t) => t.status === 'running'),
    }),
    { name: 'progress-store' }
  )
);

/**
 * UI Store - Manages UI state (dialogs, sidebars, etc.)
 */
export const useUIStore = create(
  devtools(
    (set) => ({
      // State
      isModelDialogOpen: false,
      editingModel: null,
      isSidebarCollapsed: false,
      activeTab: 'dashboard',
      notifications: [],

      // Actions
      openModelDialog: (model = null) =>
        set({ isModelDialogOpen: true, editingModel: model }),

      closeModelDialog: () =>
        set({ isModelDialogOpen: false, editingModel: null }),

      toggleSidebar: () =>
        set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),

      setActiveTab: (tab) => set({ activeTab: tab }),

      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            ...state.notifications,
            {
              ...notification,
              id: crypto.randomUUID(),
              createdAt: new Date().toISOString(),
            },
          ],
        })),

      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),

      clearNotifications: () => set({ notifications: [] }),
    }),
    { name: 'ui-store' }
  )
);
