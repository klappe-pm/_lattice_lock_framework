import { useState } from 'react';
import { useModelsStore } from '../../store';
import './ModelDialog.css';

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google' },
  { value: 'local', label: 'Local (Ollama)' },
  { value: 'bedrock', label: 'AWS Bedrock' },
  { value: 'azure', label: 'Azure OpenAI' },
  { value: 'xai', label: 'xAI (Grok)' },
];

const CAPABILITIES = [
  { value: 'reasoning', label: 'Reasoning' },
  { value: 'code', label: 'Code Generation' },
  { value: 'vision', label: 'Vision/Image' },
  { value: 'function_calling', label: 'Function Calling' },
  { value: 'long_context', label: 'Long Context' },
  { value: 'speed', label: 'Fast Inference' },
  { value: 'chain_of_thought', label: 'Chain of Thought' },
];

export default function ModelDialog({ model, onClose }) {
  const { addModel, updateModel } = useModelsStore();
  const isEditing = Boolean(model);

  const [formData, setFormData] = useState({
    name: model?.name || '',
    provider: model?.provider || 'openai',
    api_name: model?.api_name || '',
    api_key: '', // Never pre-filled for security
    api_base: model?.api_base || '',
    capabilities: model?.capabilities || [],
    context_window: model?.context_window || 128000,
    cost_per_1k_input: model?.cost_per_1k_input || 0,
    cost_per_1k_output: model?.cost_per_1k_output || 0,
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value,
    }));
  };

  const handleCapabilityToggle = (capability) => {
    setFormData((prev) => ({
      ...prev,
      capabilities: prev.capabilities.includes(capability)
        ? prev.capabilities.filter((c) => c !== capability)
        : [...prev.capabilities, capability],
    }));
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);

    // Simulate API test
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Mock result
    const success = Math.random() > 0.2;
    setTestResult({
      success,
      message: success ? 'Connection successful!' : 'Failed to connect. Check your API key.',
      latency: success ? Math.floor(Math.random() * 500) + 100 : null,
    });
    setIsTesting(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const modelData = {
      ...formData,
      id: model?.id || crypto.randomUUID(),
      status: 'online',
    };

    // Remove api_key from stored data (would be sent to backend separately)
    delete modelData.api_key;

    if (isEditing) {
      updateModel(model.id, modelData);
    } else {
      addModel(modelData);
    }

    onClose();
  };

  const requiresApiKey = formData.provider !== 'local';

  return (
    <div className="dialog-overlay" onClick={onClose}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-header">
          <h2 className="dialog-title">
            {isEditing ? 'Edit Model' : 'Add New Model'}
          </h2>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="dialog-content">
            <div className="form-grid">
              {/* Basic Info */}
              <div className="input-field">
                <label htmlFor="name">Display Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g., GPT-4o"
                  required
                />
              </div>

              <div className="input-field">
                <label htmlFor="provider">Provider</label>
                <select
                  id="provider"
                  name="provider"
                  value={formData.provider}
                  onChange={handleChange}
                >
                  {PROVIDERS.map((p) => (
                    <option key={p.value} value={p.value}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="input-field">
                <label htmlFor="api_name">API Model Name</label>
                <input
                  type="text"
                  id="api_name"
                  name="api_name"
                  value={formData.api_name}
                  onChange={handleChange}
                  placeholder="e.g., gpt-4o"
                  required
                />
              </div>

              <div className="input-field">
                <label htmlFor="context_window">Context Window</label>
                <input
                  type="number"
                  id="context_window"
                  name="context_window"
                  value={formData.context_window}
                  onChange={handleChange}
                  min="1024"
                  step="1024"
                />
              </div>

              {/* API Key (only for cloud providers) */}
              {requiresApiKey && (
                <div className="input-field full-width">
                  <label htmlFor="api_key">
                    API Key
                    {isEditing && (
                      <span className="hint"> (leave blank to keep existing)</span>
                    )}
                  </label>
                  <div className="password-input">
                    <input
                      type={showApiKey ? 'text' : 'password'}
                      id="api_key"
                      name="api_key"
                      value={formData.api_key}
                      onChange={handleChange}
                      placeholder="sk-..."
                      autoComplete="off"
                    />
                    <button
                      type="button"
                      className="toggle-visibility"
                      onClick={() => setShowApiKey(!showApiKey)}
                    >
                      {showApiKey ? '🙈' : '👁️'}
                    </button>
                  </div>
                  <button
                    type="button"
                    className="btn btn-outlined test-btn"
                    onClick={handleTestConnection}
                    disabled={isTesting || !formData.api_key}
                  >
                    {isTesting ? 'Testing...' : 'Test Connection'}
                  </button>
                  {testResult && (
                    <div
                      className={`test-result ${
                        testResult.success ? 'success' : 'error'
                      }`}
                    >
                      {testResult.message}
                      {testResult.latency && ` (${testResult.latency}ms)`}
                    </div>
                  )}
                </div>
              )}

              {/* Optional API Base for self-hosted */}
              {(formData.provider === 'local' || formData.provider === 'azure') && (
                <div className="input-field full-width">
                  <label htmlFor="api_base">API Base URL</label>
                  <input
                    type="url"
                    id="api_base"
                    name="api_base"
                    value={formData.api_base}
                    onChange={handleChange}
                    placeholder="http://localhost:11434"
                  />
                </div>
              )}

              {/* Cost per token */}
              <div className="input-field">
                <label htmlFor="cost_per_1k_input">Input Cost ($/1K tokens)</label>
                <input
                  type="number"
                  id="cost_per_1k_input"
                  name="cost_per_1k_input"
                  value={formData.cost_per_1k_input}
                  onChange={handleChange}
                  step="0.0001"
                  min="0"
                />
              </div>

              <div className="input-field">
                <label htmlFor="cost_per_1k_output">Output Cost ($/1K tokens)</label>
                <input
                  type="number"
                  id="cost_per_1k_output"
                  name="cost_per_1k_output"
                  value={formData.cost_per_1k_output}
                  onChange={handleChange}
                  step="0.0001"
                  min="0"
                />
              </div>

              {/* Capabilities */}
              <div className="input-field full-width">
                <label>Capabilities</label>
                <div className="capabilities-grid">
                  {CAPABILITIES.map((cap) => (
                    <label key={cap.value} className="capability-checkbox">
                      <input
                        type="checkbox"
                        checked={formData.capabilities.includes(cap.value)}
                        onChange={() => handleCapabilityToggle(cap.value)}
                      />
                      <span>{cap.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="dialog-actions">
            <button type="button" className="btn btn-text" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-filled">
              {isEditing ? 'Save Changes' : 'Add Model'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
