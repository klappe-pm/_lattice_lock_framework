import { useProgressStore } from '../../store';
import './TaskList.css';

const StatusIcon = ({ status }) => {
  switch (status) {
    case 'pending':
      return <span className="status-icon pending">⏳</span>;
    case 'running':
      return <span className="status-icon running">🔄</span>;
    case 'completed':
      return <span className="status-icon completed">✓</span>;
    case 'failed':
      return <span className="status-icon failed">✗</span>;
    default:
      return <span className="status-icon">•</span>;
  }
};

function TaskItem({ task, depth = 0 }) {
  const { name, status, duration, model, subtasks = [] } = task;

  return (
    <div className="task-item" style={{ '--depth': depth }}>
      <div className={`task-row status-${status}`}>
        <StatusIcon status={status} />
        <span className="task-name">{name}</span>
        {model && <span className="task-model chip">{model}</span>}
        {duration && <span className="task-duration">{duration}ms</span>}
        {status === 'running' && (
          <div className="task-progress">
            <div className="progress-linear">
              <div className="progress-linear-bar progress-linear-indeterminate" />
            </div>
          </div>
        )}
      </div>
      {subtasks.length > 0 && (
        <div className="subtasks">
          {subtasks.map((subtask) => (
            <TaskItem key={subtask.id} task={subtask} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function TaskList() {
  const { tasks, tokenUsage, cost } = useProgressStore();

  const completedCount = tasks.filter((t) => t.status === 'completed').length;
  const totalCount = tasks.length;
  const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <div className="task-list-container">
      <div className="task-list-header">
        <div className="header-left">
          <h3>Task Progress</h3>
          <span className="task-count">
            {completedCount} / {totalCount} tasks
          </span>
        </div>
        <div className="header-right">
          <div className="stat-badge">
            <span className="label">Tokens</span>
            <span className="value">{tokenUsage.total.toLocaleString()}</span>
          </div>
          <div className="stat-badge">
            <span className="label">Cost</span>
            <span className="value">${cost.toFixed(4)}</span>
          </div>
        </div>
      </div>

      {totalCount > 0 && (
        <div className="overall-progress">
          <div className="progress-linear">
            <div
              className="progress-linear-bar"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="progress-label">{Math.round(progress)}%</span>
        </div>
      )}

      <div className="tasks">
        {tasks.length === 0 ? (
          <div className="empty-tasks">
            <p>No tasks yet. Submit a prompt to start execution.</p>
          </div>
        ) : (
          tasks.map((task) => <TaskItem key={task.id} task={task} />)
        )}
      </div>
    </div>
  );
}
