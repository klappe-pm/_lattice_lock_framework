import { useState, useMemo } from 'react';
import { useExecutionStore } from '../store';
import './HistoryPage.css';

/**
 * History Page
 * 
 * Displays execution history with filtering and search capabilities.
 * Allows users to view past conversations and replay prompts.
 */
export default function HistoryPage() {
  const { conversationHistory, clearHistory } = useExecutionStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');

  const filteredHistory = useMemo(() => {
    return conversationHistory.filter(message => {
      const matchesSearch = !searchQuery || 
        message.content?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesRole = roleFilter === 'all' || message.role === roleFilter;
      return matchesSearch && matchesRole;
    });
  }, [conversationHistory, searchQuery, roleFilter]);

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all history? This cannot be undone.')) {
      clearHistory();
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="history-page">
      {/* Filters */}
      <section className="history-filters card">
        <div className="filter-row">
          <div className="input-field search-field">
            <input
              type="text"
              placeholder="Search history..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="filter-chips">
            <button
              className={`chip ${roleFilter === 'all' ? 'chip-primary' : ''}`}
              onClick={() => setRoleFilter('all')}
            >
              All
            </button>
            <button
              className={`chip ${roleFilter === 'user' ? 'chip-primary' : ''}`}
              onClick={() => setRoleFilter('user')}
            >
              User
            </button>
            <button
              className={`chip ${roleFilter === 'assistant' ? 'chip-primary' : ''}`}
              onClick={() => setRoleFilter('assistant')}
            >
              Assistant
            </button>
          </div>

          <button 
            className="btn btn-outlined danger"
            onClick={handleClearHistory}
            disabled={conversationHistory.length === 0}
          >
            Clear History
          </button>
        </div>
      </section>

      {/* History List */}
      <section className="history-list">
        {filteredHistory.length === 0 ? (
          <div className="empty-state card">
            <div className="empty-icon">📜</div>
            <h3>No History Found</h3>
            <p>
              {conversationHistory.length === 0 
                ? 'Start by executing a prompt to see history here.'
                : 'No messages match your search criteria.'}
            </p>
          </div>
        ) : (
          filteredHistory.map((message, index) => (
            <div 
              key={index} 
              className={`history-item card ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
            >
              <div className="message-header">
                <span className={`role-badge chip chip-${message.role === 'user' ? 'secondary' : 'primary'}`}>
                  {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
                </span>
                {message.model && (
                  <span className="model-badge chip">{message.model}</span>
                )}
                <span className="timestamp">{formatTimestamp(message.timestamp)}</span>
              </div>
              <div className="message-content">
                {message.content}
              </div>
              <div className="message-actions">
                <button 
                  className="btn btn-text"
                  onClick={() => navigator.clipboard.writeText(message.content)}
                >
                  📋 Copy
                </button>
                {message.role === 'user' && (
                  <a href={`/execute?prompt=${encodeURIComponent(message.content)}`} className="btn btn-text">
                    🔄 Replay
                  </a>
                )}
              </div>
            </div>
          ))
        )}
      </section>

      {/* Stats */}
      {conversationHistory.length > 0 && (
        <section className="history-stats card">
          <div className="stat">
            <span className="stat-value">{conversationHistory.length}</span>
            <span className="stat-label">Total Messages</span>
          </div>
          <div className="stat">
            <span className="stat-value">
              {conversationHistory.filter(m => m.role === 'user').length}
            </span>
            <span className="stat-label">Prompts</span>
          </div>
          <div className="stat">
            <span className="stat-value">
              {conversationHistory.filter(m => m.role === 'assistant').length}
            </span>
            <span className="stat-label">Responses</span>
          </div>
        </section>
      )}
    </div>
  );
}
