import { useNavigate } from 'react-router-dom';

export default function ProjectCard({ project, onDelete }) {
  const navigate = useNavigate();
  const { id, name, description, updatedAt, modelConfig } = project;

  return (
    <div className="project-card card card-elevated" onClick={() => navigate(`/projects/${id}`)}>
      <div className="card-header">
        <h3>{name}</h3>
        <span className="project-date">{new Date(updatedAt).toLocaleDateString()}</span>
      </div>
      <p className="project-description">{description || 'No description'}</p>
      <div className="card-footer">
        <span className="model-badge chip">{modelConfig?.model || 'Auto'}</span>
        <div className="actions">
          <button 
            className="btn btn-icon"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/projects/${id}/edit`);
            }}
            title="Edit"
          >
            ✏️
          </button>
          <button 
            className="btn btn-icon"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(id);
            }}
            title="Delete"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
}
