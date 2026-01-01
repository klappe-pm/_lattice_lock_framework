import './ModelCard.css';

const EditIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
    <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
  </svg>
);

const DeleteIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
    <path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z"/>
  </svg>
);

const TestIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
    <path d="M480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm-40-82v-78q-33 0-56.5-23.5T360-320v-40L168-552q-3 18-5.5 36t-2.5 36q0 121 79.5 212T440-162Zm276-102q20-22 36-47.5t26.5-53q10.5-27.5 16-56.5t5.5-59q0-98-54.5-179T600-776v16q0 33-23.5 56.5T520-680h-80v80q0 17-11.5 28.5T400-560h-80v80h240q17 0 28.5 11.5T600-440v120h40q26 0 47 15.5t29 40.5Z"/>
  </svg>
);

const providerColors = {
  openai: '#10A37F',
  anthropic: '#D4A574',
  google: '#4285F4',
  local: '#9E9E9E',
  bedrock: '#FF9900',
  azure: '#0078D4',
  xai: '#1DA1F2',
};

const capabilityLabels = {
  reasoning: '🧠 Reasoning',
  code: '💻 Code',
  vision: '👁️ Vision',
  function_calling: '🔧 Functions',
  long_context: '📚 Long Context',
  speed: '⚡ Fast',
  chain_of_thought: '🔗 CoT',
};

export default function ModelCard({ model, onEdit, onDelete }) {
  const {
    name,
    provider,
    api_name,
    status,
    capabilities = [],
    context_window,
    cost_per_1k_input,
    cost_per_1k_output,
  } = model;

  const providerColor = providerColors[provider] || '#6750A4';

  const formatContextWindow = (size) => {
    if (size >= 1000000) return `${(size / 1000000).toFixed(1)}M`;
    if (size >= 1000) return `${(size / 1000).toFixed(0)}K`;
    return size;
  };

  const formatCost = (cost) => {
    if (cost === 0) return 'Free';
    if (cost < 0.001) return `$${(cost * 1000).toFixed(3)}/1M`;
    return `$${cost.toFixed(4)}/1K`;
  };

  const handleTest = async (e) => {
    e.stopPropagation();
    console.log('Testing connection for:', model.id);
    // In production, this would call the test API
  };

  return (
    <div className="model-card card card-elevated">
      <div className="card-header">
        <div className="model-info">
          <div 
            className="provider-indicator" 
            style={{ backgroundColor: providerColor }}
          />
          <div>
            <h3 className="model-name">{name}</h3>
            <span className="api-name">{api_name}</span>
          </div>
        </div>
        <div className={`status-indicator status-${status}`}>
          <span className="status-dot"></span>
          <span>{status}</span>
        </div>
      </div>

      <div className="card-body">
        <div className="capabilities">
          {capabilities.slice(0, 4).map((cap) => (
            <span key={cap} className="chip" title={cap}>
              {capabilityLabels[cap] || cap}
            </span>
          ))}
          {capabilities.length > 4 && (
            <span className="chip">+{capabilities.length - 4}</span>
          )}
        </div>

        <div className="model-stats">
          <div className="stat">
            <span className="stat-label">Context</span>
            <span className="stat-value">{formatContextWindow(context_window)}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Input</span>
            <span className="stat-value">{formatCost(cost_per_1k_input)}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Output</span>
            <span className="stat-value">{formatCost(cost_per_1k_output)}</span>
          </div>
        </div>
      </div>

      <div className="card-actions">
        <button 
          className="btn btn-text btn-icon" 
          onClick={handleTest}
          title="Test Connection"
        >
          <TestIcon />
        </button>
        <button 
          className="btn btn-text btn-icon" 
          onClick={onEdit}
          title="Edit Model"
        >
          <EditIcon />
        </button>
        <button 
          className="btn btn-text btn-icon" 
          onClick={onDelete}
          title="Delete Model"
        >
          <DeleteIcon />
        </button>
      </div>
    </div>
  );
}
