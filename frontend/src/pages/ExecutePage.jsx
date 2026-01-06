import { useState } from 'react';
import { useModelsStore, useExecutionStore, useProgressStore } from '../store';
import PromptInput from '../components/execution/PromptInput';
import TaskList from '../components/progress/TaskList';
import SelectionFlow from '../components/selection/SelectionFlow';
import './ExecutePage.css';

/**
 * Execute Page
 * 
 * Main prompt execution interface.
 * Allows users to input prompts, select models, and track execution progress.
 */
export default function ExecutePage() {
  const { models, selectedModel, setSelectedModel } = useModelsStore();
  const { 
    isExecuting, 
    currentExecution, 
    systemInstructions, 
    setSystemInstructions,
    startExecution,
    completeExecution,
    failExecution,
    addToHistory 
  } = useExecutionStore();
  const { tasks, selectionFlow } = useProgressStore();

  const [showAdvanced, setShowAdvanced] = useState(false);

  const onlineModels = models.filter(m => m.status === 'online');

  const handleSubmit = async (prompt) => {
    if (!prompt.trim()) return;
    
    // Start execution
    const executionId = crypto.randomUUID();
    startExecution(executionId);
    
    // Add user message to history
    addToHistory({
      role: 'user',
      content: prompt,
      timestamp: new Date().toISOString(),
    });

    try {
      // Simulate API call (in production, this would call the orchestrator)
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulate response
      const response = `Response to: "${prompt.substring(0, 50)}..."`;
      
      addToHistory({
        role: 'assistant',
        content: response,
        timestamp: new Date().toISOString(),
        model: selectedModel?.name || 'Auto-selected',
      });
      
      completeExecution({ content: response });
    } catch (error) {
      failExecution(error.message);
    }
  };

  return (
    <div className="execute-page">
      <div className="execute-main">
        {/* Model Selection */}
        <section className="model-selection card">
          <h3>Select Model</h3>
          <div className="model-chips">
            <button 
              className={`chip ${!selectedModel ? 'chip-primary' : ''}`}
              onClick={() => setSelectedModel(null)}
            >
              🤖 Auto (Best Match)
            </button>
            {onlineModels.slice(0, 4).map(model => (
              <button
                key={model.id}
                className={`chip ${selectedModel?.id === model.id ? 'chip-primary' : ''}`}
                onClick={() => setSelectedModel(model)}
              >
                {model.name}
              </button>
            ))}
          </div>
        </section>

        {/* Advanced Options */}
        <button 
          className="btn btn-text advanced-toggle"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? '▲ Hide' : '▼ Show'} Advanced Options
        </button>

        {showAdvanced && (
          <section className="advanced-options card card-outlined">
            <div className="input-field">
              <label htmlFor="system-instructions">System Instructions</label>
              <textarea
                id="system-instructions"
                value={systemInstructions}
                onChange={(e) => setSystemInstructions(e.target.value)}
                placeholder="Optional: Provide system-level instructions for the model..."
                rows={4}
              />
            </div>
          </section>
        )}

        {/* Prompt Input */}
        <section className="prompt-section">
          <PromptInput 
            onSubmit={handleSubmit}
            isLoading={isExecuting}
            placeholder="Enter your prompt..."
          />
        </section>

        {/* Execution Status */}
        {currentExecution && (
          <section className="execution-status card card-elevated">
            <div className={`status-badge status-${currentExecution.status}`}>
              <span className="status-dot"></span>
              {currentExecution.status}
            </div>
            {currentExecution.result && (
              <div className="execution-result">
                <h4>Result</h4>
                <p>{currentExecution.result.content}</p>
              </div>
            )}
            {currentExecution.error && (
              <div className="execution-error">
                <h4>Error</h4>
                <p>{currentExecution.error}</p>
              </div>
            )}
          </section>
        )}
      </div>

      {/* Sidebar */}
      <aside className="execute-sidebar">
        {/* Selection Flow Visualization */}
        {selectionFlow && (
          <section className="selection-flow-section">
            <h3>Model Selection Flow</h3>
            <SelectionFlow flow={selectionFlow} />
          </section>
        )}

        {/* Task Progress */}
        <section className="tasks-section">
          <h3>Task Progress</h3>
          <TaskList tasks={tasks} />
        </section>
      </aside>
    </div>
  );
}
