import { useModelsStore, useExecutionStore, useProgressStore } from '../store';
import { useProjectStore } from '../store/projectStore';
import './DashboardPage.css';

/**
 * Dashboard Page
 * 
 * Overview page showing system stats, recent activity, and quick actions.
 * Serves as the landing page for the application.
 */
export default function DashboardPage() {
  const { models } = useModelsStore();
  const { conversationHistory, currentExecution } = useExecutionStore();
  const { tasks, tokenUsage, cost } = useProgressStore();
  const { projects } = useProjectStore();

  const onlineModels = models.filter(m => m.status === 'online').length;
  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const runningTasks = tasks.filter(t => t.status === 'running').length;

  return (
    <div className="dashboard-page">
      {/* Stats Overview */}
      <section className="stats-grid">
        <div className="stat-card card card-elevated">
          <div className="stat-icon models-icon">🤖</div>
          <div className="stat-content">
            <span className="stat-value">{models.length}</span>
            <span className="stat-label">Models</span>
            <span className="stat-detail">{onlineModels} online</span>
          </div>
        </div>

        <div className="stat-card card card-elevated">
          <div className="stat-icon projects-icon">📁</div>
          <div className="stat-content">
            <span className="stat-value">{projects.length}</span>
            <span className="stat-label">Projects</span>
            <span className="stat-detail">Active</span>
          </div>
        </div>

        <div className="stat-card card card-elevated">
          <div className="stat-icon tasks-icon">✅</div>
          <div className="stat-content">
            <span className="stat-value">{completedTasks}</span>
            <span className="stat-label">Tasks Completed</span>
            <span className="stat-detail">{runningTasks} running</span>
          </div>
        </div>

        <div className="stat-card card card-elevated">
          <div className="stat-icon tokens-icon">🎯</div>
          <div className="stat-content">
            <span className="stat-value">{tokenUsage.total.toLocaleString()}</span>
            <span className="stat-label">Tokens Used</span>
            <span className="stat-detail">${cost.toFixed(4)} cost</span>
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <a href="/execute" className="action-card card card-outlined">
            <span className="action-icon">▶️</span>
            <span className="action-label">New Prompt</span>
          </a>
          <a href="/models" className="action-card card card-outlined">
            <span className="action-icon">➕</span>
            <span className="action-label">Add Model</span>
          </a>
          <a href="/projects" className="action-card card card-outlined">
            <span className="action-icon">📂</span>
            <span className="action-label">New Project</span>
          </a>
          <a href="/history" className="action-card card card-outlined">
            <span className="action-icon">📜</span>
            <span className="action-label">View History</span>
          </a>
        </div>
      </section>

      {/* Recent Activity */}
      <section className="recent-activity">
        <h2>Recent Activity</h2>
        <div className="activity-list card">
          {conversationHistory.length === 0 ? (
            <div className="empty-state">
              <p>No recent activity</p>
              <p className="empty-hint">Start by executing a prompt or adding a model</p>
            </div>
          ) : (
            conversationHistory.slice(-5).reverse().map((message, index) => (
              <div key={index} className="activity-item">
                <span className="activity-role chip chip-secondary">
                  {message.role}
                </span>
                <span className="activity-content">
                  {message.content?.substring(0, 100)}
                  {message.content?.length > 100 && '...'}
                </span>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Current Execution Status */}
      {currentExecution && (
        <section className="current-execution">
          <h2>Current Execution</h2>
          <div className="execution-status card card-elevated">
            <div className={`status-indicator status-${currentExecution.status}`}>
              <span className="status-dot"></span>
              <span>{currentExecution.status}</span>
            </div>
            <span className="execution-id">ID: {currentExecution.id}</span>
          </div>
        </section>
      )}
    </div>
  );
}
