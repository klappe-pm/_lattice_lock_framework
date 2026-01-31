import { useEffect, useCallback } from 'react';
import { useModelsStore } from '../store';
import { modelsApi } from '../api/models';

export default function useModels() {
  const { models, loading, setModels, setLoading } = useModelsStore();

  const fetchModels = useCallback(async () => {
    setLoading(true);
    try {
      const data = await modelsApi.getAll();
      setModels(data);
    } catch (error) {
      console.error('Failed to fetch models:', error);
    } finally {
      setLoading(false);
    }
  }, [setModels, setLoading]);

  const refreshModels = useCallback(async () => {
      await fetchModels();
  }, [fetchModels]);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  return {
    models,
    loading,
    refreshModels
  };
}
