import { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useProgressStore } from '../../store';
import './SelectionFlow.css';

// Custom node component for flow diagram
function FlowNode({ data }) {
  const { label, type, status, details } = data;

  const getNodeClass = () => {
    let classes = 'flow-node';
    if (type) classes += ` node-${type}`;
    if (status) classes += ` status-${status}`;
    return classes;
  };

  return (
    <div className={getNodeClass()}>
      <div className="node-icon">{data.icon}</div>
      <div className="node-content">
        <div className="node-label">{label}</div>
        {details && <div className="node-details">{details}</div>}
      </div>
      {status === 'active' && <div className="node-pulse" />}
    </div>
  );
}

const nodeTypes = {
  flowNode: FlowNode,
};

// Initial nodes for the selection flow
const createInitialNodes = (selectionData) => {
  const baseNodes = [
    {
      id: 'request',
      type: 'flowNode',
      position: { x: 50, y: 150 },
      data: {
        label: 'Request',
        icon: '📝',
        type: 'input',
        details: selectionData?.prompt?.substring(0, 30) + '...' || 'User prompt',
      },
    },
    {
      id: 'analyzer',
      type: 'flowNode',
      position: { x: 250, y: 150 },
      data: {
        label: 'Analyzer',
        icon: '🔍',
        type: 'process',
        status: selectionData?.analyzing ? 'active' : null,
        details: 'Capability matching',
      },
    },
    {
      id: 'selector',
      type: 'flowNode',
      position: { x: 450, y: 150 },
      data: {
        label: 'Model Selector',
        icon: '🎯',
        type: 'process',
        status: selectionData?.selecting ? 'active' : null,
        details: 'Cost/performance optimization',
      },
    },
  ];

  // Add model nodes if we have selection data
  if (selectionData?.candidates) {
    selectionData.candidates.forEach((model, index) => {
      baseNodes.push({
        id: `model-${model.id}`,
        type: 'flowNode',
        position: { x: 650, y: 50 + index * 100 },
        data: {
          label: model.name,
          icon: model.selected ? '✅' : '⚪',
          type: model.selected ? 'selected' : 'candidate',
          details: `Score: ${model.score?.toFixed(2) || 'N/A'}`,
        },
      });
    });
  } else {
    // Default placeholder
    baseNodes.push({
      id: 'model-placeholder',
      type: 'flowNode',
      position: { x: 650, y: 150 },
      data: {
        label: 'Selected Model',
        icon: '🤖',
        type: 'output',
        details: 'Waiting for selection...',
      },
    });
  }

  return baseNodes;
};

const createInitialEdges = (selectionData) => {
  const baseEdges = [
    {
      id: 'e-request-analyzer',
      source: 'request',
      target: 'analyzer',
      animated: true,
      style: { stroke: 'var(--md-sys-color-primary)' },
      markerEnd: { type: MarkerType.ArrowClosed },
    },
    {
      id: 'e-analyzer-selector',
      source: 'analyzer',
      target: 'selector',
      animated: true,
      style: { stroke: 'var(--md-sys-color-primary)' },
      markerEnd: { type: MarkerType.ArrowClosed },
    },
  ];

  if (selectionData?.candidates) {
    selectionData.candidates.forEach((model) => {
      baseEdges.push({
        id: `e-selector-model-${model.id}`,
        source: 'selector',
        target: `model-${model.id}`,
        animated: model.selected,
        style: {
          stroke: model.selected
            ? 'var(--md-sys-color-secondary)'
            : 'var(--md-sys-color-outline)',
          strokeWidth: model.selected ? 2 : 1,
        },
        markerEnd: { type: MarkerType.ArrowClosed },
      });
    });
  } else {
    baseEdges.push({
      id: 'e-selector-placeholder',
      source: 'selector',
      target: 'model-placeholder',
      animated: false,
      style: { stroke: 'var(--md-sys-color-outline)', strokeDasharray: '5,5' },
      markerEnd: { type: MarkerType.ArrowClosed },
    });
  }

  return baseEdges;
};

export default function SelectionFlow() {
  const { selectionFlow } = useProgressStore();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    setNodes(createInitialNodes(selectionFlow));
    setEdges(createInitialEdges(selectionFlow));
  }, [selectionFlow, setNodes, setEdges]);

  // Demo: simulate selection flow
  const [isSimulating, setIsSimulating] = useState(false);

  const simulateSelection = useCallback(async () => {
    setIsSimulating(true);
    const { setSelectionFlow } = useProgressStore.getState();

    // Step 1: Analyzing
    setSelectionFlow({ analyzing: true, prompt: 'Explain quantum computing' });
    await new Promise((r) => setTimeout(r, 1000));

    // Step 2: Selecting
    setSelectionFlow({
      analyzing: false,
      selecting: true,
      prompt: 'Explain quantum computing',
      candidates: [
        { id: 'gpt4', name: 'GPT-4o', score: 0.92, selected: false },
        { id: 'claude', name: 'Claude 3.5', score: 0.95, selected: false },
        { id: 'gemini', name: 'Gemini 2.0', score: 0.88, selected: false },
      ],
    });
    await new Promise((r) => setTimeout(r, 1000));

    // Step 3: Selected
    setSelectionFlow({
      analyzing: false,
      selecting: false,
      prompt: 'Explain quantum computing',
      candidates: [
        { id: 'gpt4', name: 'GPT-4o', score: 0.92, selected: false },
        { id: 'claude', name: 'Claude 3.5', score: 0.95, selected: true },
        { id: 'gemini', name: 'Gemini 2.0', score: 0.88, selected: false },
      ],
    });

    setIsSimulating(false);
  }, []);

  return (
    <div className="selection-flow-container">
      <div className="flow-header">
        <h3>Model Selection Flow</h3>
        <button
          className="btn btn-outlined"
          onClick={simulateSelection}
          disabled={isSimulating}
        >
          {isSimulating ? 'Simulating...' : 'Demo Selection'}
        </button>
      </div>

      <div className="flow-diagram">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
          proOptions={{ hideAttribution: true }}
        >
          <Background color="var(--md-sys-color-outline-variant)" gap={20} />
          <Controls />
        </ReactFlow>
      </div>

      {selectionFlow?.candidates && (
        <div className="selection-summary">
          <h4>Selection Summary</h4>
          <div className="summary-items">
            {selectionFlow.candidates.map((model) => (
              <div
                key={model.id}
                className={`summary-item ${model.selected ? 'selected' : ''}`}
              >
                <span className="model-name">{model.name}</span>
                <span className="model-score">
                  Score: {model.score?.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
