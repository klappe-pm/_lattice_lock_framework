import { Routes, Route } from 'react-router-dom';
import ProjectList from '../components/projects/ProjectList';
import ProjectDetail from '../components/projects/ProjectDetail';
import ProjectForm from '../components/projects/ProjectForm';
import './ProjectsPage.css';

export default function ProjectsPage() {
  return (
    <div className="projects-page">
      <Routes>
        <Route index element={<ProjectList />} />
        <Route path="new" element={<ProjectForm />} />
        <Route path=":id" element={<ProjectDetail />} />
        <Route path=":id/edit" element={<ProjectForm />} />
      </Routes>
    </div>
  );
}
