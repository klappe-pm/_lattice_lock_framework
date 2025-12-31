/**
 * ProjectList Component
 * 
 * Grid-based display of all projects with search and filter capabilities
 */

import { useState, useMemo } from 'react';
import ProjectCard from './ProjectCard';
import { searchProjects, sortProjects, filterByTags, getAllTags } from '../../utils/projectHelpers';

export default function ProjectList({ 
  projects, 
  onProjectClick, 
  onEditProject, 
  onDeleteProject,
  onDuplicateProject 
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('updatedAt');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedTags, setSelectedTags] = useState([]);

  // Get all available tags
  const availableTags = useMemo(() => getAllTags(projects), [projects]);

  // Filter and sort projects
  const filteredProjects = useMemo(() => {
    let result = projects.filter(p => !p.isArchived);
    
    // Search
    if (searchQuery) {
      result = searchProjects(result, searchQuery);
    }

    // Filter by tags
    if (selectedTags.length > 0) {
      result = filterByTags(result, selectedTags);
    }

    // Sort
    result = sortProjects(result, sortBy, sortOrder);

    return result;
  }, [projects, searchQuery, selectedTags, sortBy, sortOrder]);

  const toggleTag = (tag) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  if (projects.length === 0) {
    // Empty state
    return (
      <div 
        className="empty-state"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 'var(--spacing-xxl)',
          textAlign: 'center'
        }}
      >
        <div 
          style={{
            fontSize: '64px',
            marginBottom: 'var(--spacing-md)'
          }}
        >
          📁
        </div>
        <h2 
          style={{
            font: 'var(--md-sys-typescale-headline-medium)',
            color: 'var(--md-sys-color-on-surface)',
            marginBottom: 'var(--spacing-sm)'
          }}
        >
          No Projects Yet
        </h2>
        <p 
          style={{
            font: 'var(--md-sys-typescale-body-large)',
            color: 'var(--md-sys-color-on-surface-variant)',
            maxWidth: '400px'
          }}
        >
          Create your first project to organize your work with custom context, instructions, and conversation history.
        </p>
      </div>
    );
  }

  return (
    <div className="project-list">
      {/* Search and Filter Bar */}
      <div 
        className="project-list-controls"
        style={{
          marginBottom: 'var(--spacing-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-md)'
        }}
      >
        {/* Search */}
        <div className="flex gap-md" style={{ flexWrap: 'wrap' }}>
          <div className="input-field" style={{ flex: '1 1 300px' }}>
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: '100%' }}
            />
          </div>

          {/* Sort controls */}
          <div className="flex gap-sm" style={{ alignItems: 'flex-end' }}>
            <div className="input-field" style={{ minWidth: '150px' }}>
              <label>Sort by</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="updatedAt">Last Updated</option>
                <option value="createdAt">Date Created</option>
                <option value="name">Name</option>
              </select>
            </div>

            <button
              className="btn btn-outlined"
              onClick={toggleSortOrder}
              title={`Sort ${sortOrder === 'asc' ? 'descending' : 'ascending'}`}
              style={{ height: 'fit-content' }}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>
        </div>

        {/* Tag filters */}
        {availableTags.length > 0 && (
          <div className="tag-filters">
            <div 
              style={{
                font: 'var(--md-sys-typescale-label-medium)',
                color: 'var(--md-sys-color-on-surface-variant)',
                marginBottom: 'var(--spacing-xs)'
              }}
            >
              Filter by tags:
            </div>
            <div className="flex gap-xs" style={{ flexWrap: 'wrap' }}>
              {availableTags.map(tag => (
                <button
                  key={tag}
                  className={`chip ${selectedTags.includes(tag) ? 'chip-primary' : ''}`}
                  onClick={() => toggleTag(tag)}
                  style={{
                    cursor: 'pointer',
                    border: 'none',
                    transition: 'all 0.2s'
                  }}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Results count */}
      <div 
        style={{
          font: 'var(--md-sys-typescale-body-medium)',
          color: 'var(--md-sys-color-on-surface-variant)',
          marginBottom: 'var(--spacing-md)'
        }}
      >
        {filteredProjects.length} {filteredProjects.length === 1 ? 'project' : 'projects'}
        {(searchQuery || selectedTags.length > 0) && ` (filtered from ${projects.length})`}
      </div>

      {/* Project grid */}
      {filteredProjects.length > 0 ? (
        <div className="grid grid-cols-3" style={{ gap: 'var(--spacing-md)' }}>
          {filteredProjects.map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              onClick={onProjectClick}
              onEdit={onEditProject}
              onDelete={onDeleteProject}
              onDuplicate={onDuplicateProject}
            />
          ))}
        </div>
      ) : (
        <div 
          className="no-results"
          style={{
            textAlign: 'center',
            padding: 'var(--spacing-xl)',
            color: 'var(--md-sys-color-on-surface-variant)'
          }}
        >
          <div style={{ fontSize: '48px', marginBottom: 'var(--spacing-sm)' }}>
            🔍
          </div>
          <p>No projects match your filters</p>
          <button
            className="btn btn-text"
            onClick={() => {
              setSearchQuery('');
              setSelectedTags([]);
            }}
            style={{ marginTop: 'var(--spacing-sm)' }}
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
}
