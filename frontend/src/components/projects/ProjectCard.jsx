/**
 * ProjectCard Component
 * 
 * Displays an individual project as a card with quick actions
 */

import { useState } from 'react';
import { formatDate, truncateText } from '../../utils/projectHelpers';

export default function ProjectCard({ project, onEdit, onDelete, onDuplicate, onClick }) {
  const [showMenu, setShowMenu] = useState(false);

  const handleCardClick = (e) => {
    // Don't trigger if clicking on action buttons
    if (e.target.closest('.project-card-actions')) return;
    onClick?.(project);
  };

  const handleEdit = (e) => {
    e.stopPropagation();
    setShowMenu(false);
    onEdit?.(project);
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    setShowMenu(false);
    if (confirm(`Are you sure you want to delete "${project.name}"?`)) {
      onDelete?.(project.id);
    }
  };

  const handleDuplicate = (e) => {
    e.stopPropagation();
    setShowMenu(false);
    onDuplicate?.(project.id);
  };

  const chatCount = project.linkedChats?.length || 0;

  return (
    <div 
      className="project-card card card-elevated fade-in"
      onClick={handleCardClick}
      style={{ cursor: 'pointer' }}
    >
      {/* Color indicator */}
      <div 
        className="project-card-color-bar"
        style={{
          height: '4px',
          backgroundColor: project.color || 'var(--md-sys-color-primary)',
          borderRadius: 'var(--md-sys-shape-corner-small) var(--md-sys-shape-corner-small) 0 0',
          marginBottom: 'var(--spacing-md)'
        }}
      />

      {/* Header */}
      <div className="flex justify-between items-center" style={{ marginBottom: 'var(--spacing-sm)' }}>
        <h3 
          className="project-card-title"
          style={{
            font: 'var(--md-sys-typescale-title-large)',
            color: 'var(--md-sys-color-on-surface)',
            margin: 0,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}
        >
          {project.name}
        </h3>

        {/* Actions menu */}
        <div className="project-card-actions" style={{ position: 'relative' }}>
          <button
            className="btn btn-icon btn-text"
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            aria-label="More actions"
          >
            ⋮
          </button>

          {showMenu && (
            <>
              {/* Backdrop */}
              <div 
                style={{
                  position: 'fixed',
                  inset: 0,
                  zIndex: 10
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  setShowMenu(false);
                }}
              />
              {/* Menu */}
              <div 
                className="project-card-menu elevation-2"
                style={{
                  position: 'absolute',
                  right: 0,
                  top: '100%',
                  marginTop: 'var(--spacing-xs)',
                  backgroundColor: 'var(--md-sys-color-surface-container-high)',
                  borderRadius: 'var(--md-sys-shape-corner-medium)',
                  padding: 'var(--spacing-xs)',
                  minWidth: '160px',
                  zIndex: 20
                }}
              >
                <button
                  className="menu-item"
                  onClick={handleEdit}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    border: 'none',
                    background: 'none',
                    textAlign: 'left',
                    cursor: 'pointer',
                    font: 'var(--md-sys-typescale-body-medium)',
                    color: 'var(--md-sys-color-on-surface)',
                    borderRadius: 'var(--md-sys-shape-corner-small)',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(208, 188, 255, 0.08)'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                >
                  ✏️ Edit
                </button>
                <button
                  className="menu-item"
                  onClick={handleDuplicate}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    border: 'none',
                    background: 'none',
                    textAlign: 'left',
                    cursor: 'pointer',
                    font: 'var(--md-sys-typescale-body-medium)',
                    color: 'var(--md-sys-color-on-surface)',
                    borderRadius: 'var(--md-sys-shape-corner-small)',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(208, 188, 255, 0.08)'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                >
                  📋 Duplicate
                </button>
                <div className="divider" style={{ margin: 'var(--spacing-xs) 0' }} />
                <button
                  className="menu-item"
                  onClick={handleDelete}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    border: 'none',
                    background: 'none',
                    textAlign: 'left',
                    cursor: 'pointer',
                    font: 'var(--md-sys-typescale-body-medium)',
                    color: 'var(--color-error)',
                    borderRadius: 'var(--md-sys-shape-corner-small)',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(229, 115, 115, 0.08)'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                >
                  🗑️ Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Description */}
      {project.description && (
        <p 
          className="project-card-description"
          style={{
            font: 'var(--md-sys-typescale-body-medium)',
            color: 'var(--md-sys-color-on-surface-variant)',
            margin: '0 0 var(--spacing-md) 0',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical'
          }}
        >
          {project.description}
        </p>
      )}

      {/* Tags */}
      {project.tags && project.tags.length > 0 && (
        <div 
          className="project-card-tags flex gap-xs"
          style={{ 
            marginBottom: 'var(--spacing-md)',
            flexWrap: 'wrap'
          }}
        >
          {project.tags.slice(0, 3).map(tag => (
            <span key={tag} className="chip">
              {tag}
            </span>
          ))}
          {project.tags.length > 3 && (
            <span className="chip">+{project.tags.length - 3}</span>
          )}
        </div>
      )}

      {/* Footer */}
      <div 
        className="project-card-footer flex justify-between items-center"
        style={{
          paddingTop: 'var(--spacing-sm)',
          borderTop: '1px solid var(--md-sys-color-outline-variant)'
        }}
      >
        <span 
          style={{
            font: 'var(--md-sys-typescale-label-medium)',
            color: 'var(--md-sys-color-on-surface-variant)'
          }}
        >
          {formatDate(project.updatedAt)}
        </span>

        {chatCount > 0 && (
          <span 
            className="chat-count-badge"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 'var(--spacing-xs)',
              padding: '2px var(--spacing-sm)',
              borderRadius: 'var(--md-sys-shape-corner-small)',
              backgroundColor: 'var(--md-sys-color-secondary-container)',
              color: 'var(--md-sys-color-on-secondary-container)',
              font: 'var(--md-sys-typescale-label-small)',
              fontWeight: 500
            }}
          >
            💬 {chatCount}
          </span>
        )}
      </div>
    </div>
  );
}
