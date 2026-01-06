import ModelRegistry from '../components/models/ModelRegistry';

/**
 * Models Page
 * 
 * Displays the model registry with all available LLM models.
 * Supports viewing, adding, editing, and removing models.
 */
export default function ModelsPage() {
  return (
    <div className="models-page">
      <ModelRegistry />
    </div>
  );
}
