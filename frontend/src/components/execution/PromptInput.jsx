import { useState } from 'react';
import { useExecutionStore } from '../../store';
import './PromptInput.css';

const SendIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
    <path d="M120-160v-640l760 320-760 320Zm80-120 474-200-474-200v140l240 60-240 60v140Zm0 0v-400 400Z"/>
  </svg>
);

const SettingsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
    <path d="M440-120v-240h80v80h320v80H520v80h-80Zm-320-80v-80h240v80H120Zm160-160v-80H120v-80h160v-80h80v240h-80Zm160-80v-80h400v80H440Zm160-160v-240h80v80h160v80H680v80h-80Zm-480-80v-80h400v80H120Z"/>
  </svg>
);

const ClearIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
    <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
  </svg>
);

export default function PromptInput({ onSubmit }) {
  const { systemInstructions, setSystemInstructions, isExecuting } = useExecutionStore();
  const [prompt, setPrompt] = useState('');
  const [showSystemInstructions, setShowSystemInstructions] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || isExecuting) return;

    onSubmit?.({
      prompt: prompt.trim(),
      systemInstructions: systemInstructions.trim(),
    });
    setPrompt('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit(e);
    }
  };

  return (
    <div className="prompt-input-container">
      {/* System Instructions Panel */}
      <div className={`system-instructions-panel ${showSystemInstructions ? 'open' : ''}`}>
        <div className="panel-header">
          <h4>System Instructions</h4>
          <p className="hint">
            Persistent instructions to prevent prompt drift and maintain coherence.
          </p>
        </div>
        <textarea
          className="system-textarea"
          value={systemInstructions}
          onChange={(e) => setSystemInstructions(e.target.value)}
          placeholder="e.g., You are a helpful coding assistant. Always provide working code examples. Use TypeScript when appropriate."
          rows={4}
        />
      </div>

      {/* Main Prompt Input */}
      <form className="prompt-form" onSubmit={handleSubmit}>
        <div className="prompt-actions-left">
          <button
            type="button"
            className={`btn btn-icon ${showSystemInstructions ? 'active' : ''}`}
            onClick={() => setShowSystemInstructions(!showSystemInstructions)}
            title="System Instructions"
          >
            <SettingsIcon />
          </button>
          {systemInstructions && (
            <span className="system-indicator chip chip-primary">
              System Active
            </span>
          )}
        </div>

        <div className="prompt-input-wrapper">
          <textarea
            className="prompt-textarea"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter your prompt... (Cmd/Ctrl + Enter to send)"
            rows={3}
            disabled={isExecuting}
          />
          {prompt && (
            <button
              type="button"
              className="clear-btn"
              onClick={() => setPrompt('')}
              title="Clear"
            >
              <ClearIcon />
            </button>
          )}
        </div>

        <div className="prompt-actions-right">
          <button
            type="submit"
            className="btn btn-fab"
            disabled={!prompt.trim() || isExecuting}
            title="Send (Cmd/Ctrl + Enter)"
          >
            {isExecuting ? (
              <div className="spinner" />
            ) : (
              <SendIcon />
            )}
          </button>
        </div>
      </form>

      {/* Quick Actions */}
      <div className="quick-actions">
        <button
          className="btn btn-text"
          onClick={() => setPrompt('Explain this code step by step')}
        >
          💡 Explain code
        </button>
        <button
          className="btn btn-text"
          onClick={() => setPrompt('Review this code for bugs and improvements')}
        >
          🔍 Code review
        </button>
        <button
          className="btn btn-text"
          onClick={() => setPrompt('Write comprehensive tests for this')}
        >
          🧪 Write tests
        </button>
        <button
          className="btn btn-text"
          onClick={() => setPrompt('Refactor this code to be more maintainable')}
        >
          🔧 Refactor
        </button>
      </div>
    </div>
  );
}
