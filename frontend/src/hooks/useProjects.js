import { useEffect } from 'react';
import { useProjectsStore } from '../store';

export default function useProjects() {
  const { 
    projects, 
    // projectStore uses activeProjectId, and helpers to get activeProject
    // But store also exposes getActiveProject() selector if we use selector? 
    // The store definition (Step 1062) has activeProjectId state and getActiveProject action/selector.
    // It doesn't seem to expose activeProject as derived state directly in the object returned by create() unless using selector.
    // Wait, useProjectStore = create((set, get) => ({ ... })).
    // usage: const { activeProjectId } = useProjectStore().
    // usage: const activeProject = useProjectStore(state => state.getActiveProject()).
    // If useProjects just calls useProjectsStore() without selector, it gets the whole state + actions.
    activeProjectId,
    isLoading,
    error,
    loadProjects,
    createProject,
    updateProject,
    deleteProject,
    setActiveProject,
    getActiveProject
  } = useProjectsStore();

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  return {
    projects,
    activeProject: getActiveProject ? getActiveProject() : null, // If mock doesn't return getActiveProject, handle grace? Mock should return it.
    activeProjectId,
    loading: isLoading,
    error,
    fetchProjects: loadProjects,
    createProject,
    updateProject,
    deleteProject,
    setActiveProject
  };
}
