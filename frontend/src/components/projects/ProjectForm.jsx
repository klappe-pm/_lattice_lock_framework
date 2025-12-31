/**
 * ProjectForm Component
 * 
 * Modal dialog for creating or editing projects
 */

import { useState, useEffect } from 'react';
import { getRandomColor } from '../../utils/projectHelpers';

export default function ProjectForm({ project, onSave, onCancel, isOpen }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    context: '',
    instructions: '',
    tags: [],
    color: getRandomColor()
  });
  const [tagInput, setTagInput] = useState('');
  const [errors, setErrors] = useState({});

  // Initialize form with project data if editing
  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name || '',
        description: project.description || '',
        context: project.context || '',
        instructions: project.instructions || '',
        tags: project.tags || [],
        color: project.color || getRandomColor()
      });
    } else {
      setFormData({
        name: '',
        description: '',
        context: '',
        instructions: '',
        tags: [],
        color: getRandomColor()
      });
    }
    setErrors({});
  }, [project, isOpen]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const handleAddTag = (e) => {
    e.preventDefault();
    const tag = tagInput.trim();
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleTagInputKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag(e);
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Project name is required';
    } else if (formData.name.length > 100) {
      newErrors.name = 'Project name must be 100 characters or less';
    }

    if (formData.description.length > 500) {
      newErrors.description = 'Description must be 500 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }

    onSave({
      ...project,
      ...formData
    });
  };

  if (!isOpen) return null;

  const isEditing = !!project;

  return (
    <div className="dialog-overlay">
      <div className="dialog slide-up" style={{ maxWidth: '600px' }}>
        {/* Header */}
        <div className="dialog-header">
          <h2 className="dialog-title">
            {isEditing ? 'Edit Project' : 'Create New Project'}
          </h2>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="dialog-content" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
            {/* Name */}
            <div className="input-field">
              <label htmlFor="project-name">
                Project Name <span style={{ color: 'var(--color-error)' }}>*</span>
              </label>
              <input
                id="project-name"
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="My Awesome Project"
                autoFocus
                required
              />
              {errors.name && (
                <span style={{ 
                  font: 'var(--md-sys-typescale-label-small)',
                  color: 'var(--color-error)' 
                }}>
                  {errors.name}
                </span>
              )}
              <span style={{ 
                font: 'var(--md-sys-typescale-label-small)',
                color: 'var(--md-sys-color-on-surface-variant)' 
              }}>
                {formData.name.length}/100
              </span>
            </div>

            {/* Description */}
            <div className="input-field">
              <label htmlFor="project-description">Description</label>
              <textarea
                id="project-description"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                placeholder="A brief description of what this project is about..."
                rows="3"
              />
              {errors.description && (
                <span style={{ 
                  font: 'var(--md-sys-typescale-label-small)',
                  color: 'var(--color-error)' 
                }}>
                  {errors.description}
                </span>
              )}
              <span style={{ 
                font: 'var(--md-sys-typescale-label-small)',
                color: 'var(--md-sys-color-on-surface-variant)' 
              }}>
                {formData.description.length}/500
              </span>
            </div>

            {/* Context */}
            <div className="input-field">
              <label htmlFor="project-context">
                Context
                <span style={{ 
                  marginLeft: 'var(--spacing-xs)',
                  font: 'var(--md-sys-typescale-label-small)',
                  color: 'var(--md-sys-color-on-surface-variant)',
                  fontWeight: 'normal'
                }}>
                  (Background knowledge for this project)
                </span>
              </label>
              <textarea
                id="project-context"
                value={formData.context}
                onChange={(e) => handleChange('context', e.target.value)}
                placeholder="Add any relevant context, documentation, or background information..."
                rows="4"
              />
            </div>

            {/* Instructions */}
            <div className="input-field">
              <label htmlFor="project-instructions">
                Instructions
                <span style={{ 
                  marginLeft: 'var(--spacing-xs)',
                  font: 'var(--md-sys-typescale-label-small)',
                  color: 'var(--md-sys-color-on-surface-variant)',
                  fontWeight: 'normal'
                }}>
                  (Guidelines for AI behavior)
                </span>
              </label>
              <textarea
                id="project-instructions"
                value={formData.instructions}
                onChange={(e) => handleChange('instructions', e.target.value)}
                placeholder="Specific instructions on how to approach tasks in this project..."
                rows="4"
              />
            </div>

            {/* Tags */}
            <div className="input-field">
              <label htmlFor="project-tags">Tags</label>
              <div className="flex gap-sm">
                <input
                  id="project-tags"
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagInputKeyDown}
                  placeholder="Add a tag..."
                  style={{ flex: 1 }}
                />
                <button
                  type="button"
                  className="btn btn-outlined"
                  onClick={handleAddTag}
                  disabled={!tagInput.trim()}
                >
                  Add
                </button>
              </div>
              
              {formData.tags.length > 0 && (
                <div className="flex gap-xs" style={{ marginTop: 'var(--spacing-sm)', flexWrap: 'wrap' }}>
                  {formData.tags.map(tag => (
                    <span key={tag} className="chip chip-primary" style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          padding: 0,
                          color: 'inherit',
                          fontSize: '14px',
                          lineHeight: 1
                        }}
                        aria-label={`Remove ${tag}`}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Color picker */}
            <div className="input-field">
              <label htmlFor="project-color">Project Color</label>
              <div className="flex gap-md items-center">
                <input
                  id="project-color"
                  type="color"
                  value={formData.color}
                  onChange={(e) => handleChange('color', e.target.value)}
                  style={{
                    width: '60px',
                    height: '40px',
                    border: '1px solid var(--md-sys-color-outline)',
                    borderRadius: 'var(--md-sys-shape-corner-small)',
                    cursor: 'pointer'
                  }}
                />
                <button
                  type="button"
                  className="btn btn-text"
                  onClick={() => handleChange('color', getRandomColor())}
                >
                  Random
                </button>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="dialog-actions">
            <button
              type="button"
              className="btn btn-text"
              onClick={onCancel}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-filled"
            >
              {isEditing ? 'Save Changes' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
