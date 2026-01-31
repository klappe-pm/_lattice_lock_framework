import { useCallback } from 'react';
import { useExecutionStore } from '../store';
import { orchestratorApi } from '../api/orchestrator';

export default function useExecution() {
  const { 
    isExecuting, 
    setIsExecuting, 
    setResult, 
    addToHistory 
  } = useExecutionStore();

  const executePrompt = useCallback(async (prompt, systemInstructions, model) => {
    if (!prompt.trim()) return;

    setIsExecuting(true);
    try {
      const result = await orchestratorApi.execute({
        prompt,
        system_instructions: systemInstructions,
        model
      });
      
      setResult(result);
      addToHistory({
        role: 'user',
        content: prompt,
        timestamp: new Date().toISOString()
      });
      addToHistory({
        role: 'assistant',
        content: result.response || result.data || JSON.stringify(result),
        model: model || 'auto',
        timestamp: new Date().toISOString()
      });
      
      return result;
    } catch (error) {
      console.error('Execution failed:', error);
      setResult({ error: error.message });
    } finally {
      setIsExecuting(false);
    }
  }, [setIsExecuting, setResult, addToHistory]);

  return {
    isExecuting,
    executePrompt
  };
}
