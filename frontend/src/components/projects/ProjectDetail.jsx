/**
 * ProjectDetail Component
 * 
 * Full project view with tabs for different sections
 */

import { useState } from 'react';
import ChatHistoryPanel from './ChatHistoryPanel';

export default function ProjectDetail({ 
  project, 
  onUpdate, 
  onUnlinkChat,
  onViewChat 
}) {
  const [activeTab, setActiveTab] = useState('overview');
  const [isEditing, setIsEditing] = useState({
    context: false,
    instructions: false
  });
  const [editValues, setEditValues] = useState({
    context: project.context || '',
    instructions: project.instructions || ''
  });

  const handleSaveContext = () => {
    onUpdate?.({ context: editValues.context });
    setIsEditing({ ...isEditing, context: false });
  };

  const handleSaveInstructions = () => {
    onUpdate?.({ instructions: editValues.instructions });
    setIsEditing({ ...isEditing, instructions: false });
  };

  const handleCancelEdit = (field) => {
    setEditValues({ ...editValues, [field]: project[field] || '' });
    setIsEditing({ ...isEditing, [field]: false });
  };

  const tabs = [
    { id: 'overview', label: '📋 Overview', icon: '📋' },
    { id: 'context', label: '📚 Context', icon: '📚' },
    { id: 'instructions', label: '📝 Instructions', icon: '📝' },
    { id: 'history', label: '💬 History', icon: '💬', badge: project.linkedChats?.length }
  ];

  return (
    <div className="project-detail">
      {/* Header */}
      <div 
        className="project-detail-header"
        style={{
          marginBottom: 'var(--spacing-lg)',
          paddingBottom: 'var(--spacing-md)',
          borderBottom: `2px solid ${project.color || 'var(--md-sys-color-primary)'}`
        }}
      >
        <h1 
          style={{
            font: 'var(--md-sys-typescale-headline-large)',
            color: 'var(--md-sys-color-on-surface)',
            margin: 0
          }}
        >
          {project.name}
        </h1>
        {project.description && (
          <p 
            style={{
              font: 'var(--md-sys-typescale-body-large)',
              color: 'var(--md-sys-color-on-surface-variant)',
              margin: 'var(--spacing-sm) 0 0 0'
            }}
          >
            {project.description}
          </p>
        )}
      </div>

      {/* Tabs */}
      <div 
        className="project-detail-tabs"
        style={{
          display: 'flex',
          gap: 'var(--spacing-xs)',
          marginBottom: 'var(--spacing-lg)',
          borderBottom: '1px solid var(--md-sys-color-outline-variant)',
          overflow: 'auto'
        }}
      >
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: 'var(--spacing-sm) var(--spacing-md)',
              border: 'none',
              background: 'none',
              font: 'var(--md-sys-typescale-label-large)',
              color: activeTab === tab.id 
                ? 'var(--md-sys-color-primary)' 
                : 'var(--md-sys-color-on-surface-variant)',
              borderBottom: activeTab === tab.id 
                ? `2px solid var(--md-sys-color-primary)` 
                : '2px solid transparent',
              cursor: 'pointer',
              transition: 'all 0.2s',
              whiteSpace: 'nowrap',
              position: 'relative'
            }}
          >
            {tab.label}
            {tab.badge !== undefined && tab.badge > 0 && (
              <span 
                style={{
                  marginLeft: 'var(--spacing-xs)',
                  padding: '2px 6px',
                  borderRadius: '10px',
                  backgroundColor: 'var(--md-sys-color-primary-container)',
                  color: 'var(--md-sys-color-on-primary-container)',
                  fontSize: '11px',
                  fontWeight: 600
                }}
              >
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="project-detail-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {/* Tags */}
            <div style={{ marginBottom: 'var(--spacing-lg)' }}>
              <h3 
                style={{
                  font: 'var(--md-sys-typescale-title-medium)',
                  color: 'var(--md-sys-color-on-surface)',
                  marginBottom: 'var(--spacing-sm)'
                }}
              >
                Tags
              </h3>
              {project.tags && project.tags.length > 0 ? (
                <div className="flex gap-xs" style={{ flexWrap: 'wrap' }}>
                  {project.tags.map(tag => (
                    <span key={tag} className="chip chip-primary">
                      {tag}
                    </span>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
                  No tags added
                </p>
              )}
            </div>

            {/* Metadata */}
            <div className="card card-outlined" style={{ padding: 'var(--spacing-md)' }}>
              <div style={{ display: 'grid', gap: 'var(--spacing-sm)' }}>
                <div className="flex justify-between">
                  <span style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
                    Created:
                  </span>
                  <span>{new Date(project.createdAt).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
                    Last Updated:
                  </span>
                  <span>{new Date(project.updatedAt).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
                    Linked Conversations:
                  </span>
                  <span>{project.linkedChats?.length || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
                    Color:
                  </span>
                  <div 
                    style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      backgroundColor: project.color,
                      border: '2px solid var(--md-sys-color-outline)'
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'context' && (
          <div className="context-tab">
            <div className="flex justify-between items-center" style={{ marginBottom: 'var(--spacing-md)' }}>
              <h3 
                style={{
                  font: 'var(--md-sys-typescale-title-medium)',
                  color: 'var(--md-sys-color-on-surface)',
                  margin: 0
                }}
              >
                Project Context
              </h3>
              {!isEditing.context ? (
                <button
                  className="btn btn-outlined"
                  onClick={() => setIsEditing({ ...isEditing, context: true })}
                >
                  ✏️ Edit
                </button>
              ) : (
                <div className="flex gap-sm">
                  <button
                    className="btn btn-text"
                    onClick={() => handleCancelEdit('context')}
                  >
                    Cancel
                  </button>
                  <button
                    className="btn btn-filled"
                    onClick={handleSaveContext}
                  >
                    Save
                  </button>
                </div>
              )}
            </div>

            {isEditing.context ? (
              <div className="input-field">
                <textarea
                  value={editValues.context}
                  onChange={(e) => setEditValues({ ...editValues, context: e.target.value })}
                  placeholder="Add any relevant context, documentation, or background information that should be available across all conversations in this project..."
                  rows="15"
                  style={{ width: '100%', fontFamily: 'monospace' }}
                />
                <span style={{ 
                  font: 'var(--md-sys-typescale-label-small)',
                  color: 'var(--md-sys-color-on-surface-variant)' 
                }}>
                  {editValues.context.length} characters
                </span>
              </div>
            ) : (
              <div 
                className="card card-outlined"
                style={{
                  padding: 'var(--spacing-md)',
                  minHeight: '200px',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '14px'
                }}
              >
                {project.context || (
                  <span style={{ color: 'var(--md-sys-color-on-surface-variant)', fontStyle: 'italic' }}>
                    No context added yet. Click Edit to add project context.
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'instructions' && (
          <div className="instructions-tab">
            <div className="flex justify-between items-center" style={{ marginBottom: 'var(--spacing-md)' }}>
              <h3 
                style={{
                  font: 'var(--md-sys-typescale-title-medium)',
                  color: 'var(--md-sys-color-on-surface)',
                  margin: 0
                }}
              >
                Project Instructions
              </h3>
              {!isEditing.instructions ? (
                <button
                  className="btn btn-outlined"
                  onClick={() => setIsEditing({ ...isEditing, instructions: true })}
                >
                  ✏️ Edit
                </button>
              ) : (
                <div className="flex gap-sm">
                  <button
                    className="btn btn-text"
                    onClick={() => handleCancelEdit('instructions')}
                  >
                    Cancel
                  </button>
                  <button
                    className="btn btn-filled"
                    onClick={handleSaveInstructions}
                  >
                    Save
                  </button>
                </div>
              )}
            </div>

            {isEditing.instructions ? (
              <div className="input-field">
                <textarea
                  value={editValues.instructions}
                  onChange={(e) => setEditValues({ ...editValues, instructions: e.target.value })}
                  placeholder="Add specific instructions on how AI should behave, what style to use, constraints, or preferences for this project..."
                  rows="15"
                  style={{ width: '100%', fontFamily: 'monospace' }}
                />
                <span style={{ 
                  font: 'var(--md-sys-typescale-label-small)',
                  color: 'var(--md-sys-color-on-surface-variant)' 
                }}>
                  {editValues.instructions.length} characters
                </span>
              </div>
            ) : (
              <div 
                className="card card-outlined"
                style={{
                  padding: 'var(--spacing-md)',
                  minHeight: '200px',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '14px'
                }}
              >
                {project.instructions || (
                  <span style={{ color: 'var(--md-sys-color-on-surface-variant)', fontStyle: 'italic' }}>
                    No instructions added yet. Click Edit to add project instructions.
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <ChatHistoryPanel
            linkedChats={project.linkedChats}
            onUnlinkChat={onUnlinkChat}
            onViewChat={onViewChat}
          />
        )}
      </div>
    </div>
  );
}
