import { useModelsStore, useUIStore } from '../../store';
import ModelCard from './ModelCard';
import ModelDialog from './ModelDialog';
import './ModelRegistry.css';

const AddIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
    <path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/>
  </svg>
);

const RefreshIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
    <path d="M480-160q-134 0-227-93t-93-227q0-134 93-227t227-93q69 0 132 28.5T720-690v-110h80v280H520v-80h168q-32-56-87.5-88T480-720q-100 0-170 70t-70 170q0 100 70 170t170 70q77 0 139-44t87-116h84q-28 106-114 173t-196 67Z"/>
  </svg>
);

// Mock data for demonstration
const MOCK_MODELS = [
  {
    id: '1',
    name: 'GPT-4o',
    provider: 'openai',
    api_name: 'gpt-4o',
    status: 'online',
    capabilities: ['reasoning', 'code', 'vision', 'function_calling'],
    context_window: 128000,
    cost_per_1k_input: 0.005,
    cost_per_1k_output: 0.015,
  },
  {
    id: '2',
    name: 'Claude 3.5 Sonnet',
    provider: 'anthropic',
    api_name: 'claude-3-5-sonnet-20241022',
    status: 'online',
    capabilities: ['reasoning', 'code', 'vision', 'long_context'],
    context_window: 200000,
    cost_per_1k_input: 0.003,
    cost_per_1k_output: 0.015,
  },
  {
    id: '3',
    name: 'Gemini 2.0 Flash',
    provider: 'google',
    api_name: 'gemini-2.0-flash-exp',
    status: 'online',
    capabilities: ['reasoning', 'code', 'vision', 'speed'],
    context_window: 1000000,
    cost_per_1k_input: 0.0001,
    cost_per_1k_output: 0.0004,
  },
  {
    id: '4',
    name: 'Llama 3.2 (Local)',
    provider: 'local',
    api_name: 'llama3.2:latest',
    status: 'offline',
    capabilities: ['reasoning', 'code'],
    context_window: 8192,
    cost_per_1k_input: 0,
    cost_per_1k_output: 0,
  },
  {
    id: '5',
    name: 'DeepSeek R1',
    provider: 'openai',
    api_name: 'deepseek-reasoner',
    status: 'online',
    capabilities: ['reasoning', 'code', 'chain_of_thought'],
    context_window: 64000,
    cost_per_1k_input: 0.00055,
    cost_per_1k_output: 0.00219,
  },
];

export default function ModelRegistry() {
  const { models, setModels, isLoading } = useModelsStore();
  const { isModelDialogOpen, openModelDialog, closeModelDialog, editingModel } = useUIStore();

  // Initialize with mock data if empty
  if (models.length === 0 && !isLoading) {
    setModels(MOCK_MODELS);
  }

  const handleRefresh = () => {
    // In production, this would call the API
    console.log('Refreshing models...');
    setModels(MOCK_MODELS);
  };

  const handleAddModel = () => {
    openModelDialog(null);
  };

  const handleEditModel = (model) => {
    openModelDialog(model);
  };

  const handleDeleteModel = (modelId) => {
    if (window.confirm('Are you sure you want to delete this model?')) {
      const { removeModel } = useModelsStore.getState();
      removeModel(modelId);
    }
  };

  const groupedModels = models.reduce((acc, model) => {
    const provider = model.provider;
    if (!acc[provider]) {
      acc[provider] = [];
    }
    acc[provider].push(model);
    return acc;
  }, {});

  const providerLabels = {
    openai: 'OpenAI',
    anthropic: 'Anthropic',
    google: 'Google',
    local: 'Local (Ollama)',
    bedrock: 'AWS Bedrock',
    azure: 'Azure OpenAI',
    xai: 'xAI (Grok)',
  };

  return (
    <div className="model-registry">
      <div className="registry-header">
        <div className="registry-stats">
          <div className="stat-item">
            <span className="stat-value">{models.length}</span>
            <span className="stat-label">Total Models</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{models.filter(m => m.status === 'online').length}</span>
            <span className="stat-label">Online</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{Object.keys(groupedModels).length}</span>
            <span className="stat-label">Providers</span>
          </div>
        </div>

        <div className="registry-actions">
          <button className="btn btn-outlined" onClick={handleRefresh}>
            <RefreshIcon />
            Refresh Status
          </button>
          <button className="btn btn-filled" onClick={handleAddModel}>
            <AddIcon />
            Add Model
          </button>
        </div>
      </div>

      {Object.entries(groupedModels).map(([provider, providerModels]) => (
        <section key={provider} className="provider-section">
          <h2 className="provider-title">{providerLabels[provider] || provider}</h2>
          <div className="models-grid grid grid-cols-3">
            {providerModels.map((model) => (
              <ModelCard
                key={model.id}
                model={model}
                onEdit={() => handleEditModel(model)}
                onDelete={() => handleDeleteModel(model.id)}
              />
            ))}
          </div>
        </section>
      ))}

      {isModelDialogOpen && (
        <ModelDialog
          model={editingModel}
          onClose={closeModelDialog}
        />
      )}
    </div>
  );
}
