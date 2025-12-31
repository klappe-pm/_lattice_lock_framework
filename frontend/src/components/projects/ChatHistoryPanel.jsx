/**
 * ChatHistoryPanel Component
 * 
 * Display and manage linked conversations within a project
 */

import { useState } from 'react';
import { formatDateTime } from '../../utils/projectHelpers';

export default function ChatHistoryPanel({ linkedChats = [], onUnlinkChat, onViewChat }) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredChats = linkedChats.filter(chat => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      chat.title?.toLowerCase().includes(query) ||
      chat.summary?.toLowerCase().includes(query)
    );
  });

  if (linkedChats.length === 0) {
    return (
      <div 
        className="empty-state"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: 'var(--spacing-xl)',
          textAlign: 'center'
        }}
      >
        <div style={{ fontSize: '48px', marginBottom: 'var(--spacing-sm)' }}>
          💬
        </div>
        <h3 
          style={{
            font: 'var(--md-sys-typescale-title-large)',
            color: 'var(--md-sys-color-on-surface)',
            marginBottom: 'var(--spacing-xs)'
          }}
        >
          No Linked Conversations
        </h3>
        <p 
          style={{
            font: 'var(--md-sys-typescale-body-medium)',
            color: 'var(--md-sys-color-on-surface-variant)',
            maxWidth: '350px'
          }}
        >
          Link conversations to this project to keep track of your work and maintain context across sessions.
        </p>
      </div>
    );
  }

  return (
    <div className="chat-history-panel">
      {/* Search */}
      <div className="input-field" style={{ marginBottom: 'var(--spacing-md)' }}>
        <input
          type="text"
          placeholder="Search conversations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Results count */}
      <div 
        style={{
          font: 'var(--md-sys-typescale-body-medium)',
          color: 'var(--md-sys-color-on-surface-variant)',
          marginBottom: 'var(--spacing-sm)'
        }}
      >
        {filteredChats.length} {filteredChats.length === 1 ? 'conversation' : 'conversations'}
        {searchQuery && linkedChats.length !== filteredChats.length && ` (filtered from ${linkedChats.length})`}
      </div>

      {/* Chat list */}
      {filteredChats.length > 0 ? (
        <div className="chat-list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          {filteredChats.map(chat => (
            <div
              key={chat.id}
              className="chat-item card card-outlined"
              style={{
                padding: 'var(--spacing-md)',
                transition: 'all 0.2s',
                cursor: 'pointer'
              }}
              onClick={() => onViewChat?.(chat)}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--md-sys-color-primary)';
                e.currentTarget.style.backgroundColor = 'rgba(208, 188, 255, 0.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--md-sys-color-outline-variant)';
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              {/* Header */}
              <div className="flex justify-between items-center" style={{ marginBottom: 'var(--spacing-xs)' }}>
                <h4 
                  style={{
                    font: 'var(--md-sys-typescale-title-medium)',
                    color: 'var(--md-sys-color-on-surface)',
                    margin: 0,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    flex: 1
                  }}
                >
                  {chat.title || 'Untitled Conversation'}
                </h4>

                {/* Unlink button */}
                <button
                  className="btn btn-icon btn-text"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm('Unlink this conversation from the project?')) {
                      onUnlinkChat?.(chat.id);
                    }
                  }}
                  aria-label="Unlink conversation"
                  title="Unlink conversation"
                >
                  🔗
                </button>
              </div>

              {/* Summary */}
              {chat.summary && (
                <p 
                  style={{
                    font: 'var(--md-sys-typescale-body-medium)',
                    color: 'var(--md-sys-color-on-surface-variant)',
                    margin: '0 0 var(--spacing-sm) 0',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                  }}
                >
                  {chat.summary}
                </p>
              )}

              {/* Metadata */}
              <div className="flex gap-md items-center" style={{ flexWrap: 'wrap' }}>
                <span 
                  style={{
                    font: 'var(--md-sys-typescale-label-small)',
                    color: 'var(--md-sys-color-on-surface-variant)'
                  }}
                >
                  {formatDateTime(chat.timestamp)}
                </span>
                
                {chat.turns !== undefined && (
                  <span 
                    className="chip"
                    style={{
                      fontSize: '11px',
                      padding: '2px var(--spacing-xs)'
                    }}
                  >
                    {chat.turns} {chat.turns === 1 ? 'turn' : 'turns'}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div 
          style={{
            textAlign: 'center',
            padding: 'var(--spacing-xl)',
            color: 'var(--md-sys-color-on-surface-variant)'
          }}
        >
          <div style={{ fontSize: '32px', marginBottom: 'var(--spacing-xs)' }}>
            🔍
          </div>
          <p>No conversations match your search</p>
        </div>
      )}
    </div>
  );
}
