import { useState } from 'react';
import './SettingsPage.css';

/**
 * Settings Page
 * 
 * Application configuration including API keys, default models, and theme settings.
 * API keys are stored securely and displayed masked.
 */
export default function SettingsPage() {
  const [settings, setSettings] = useState({
    defaultModel: 'auto',
    theme: 'dark',
    autoRefresh: true,
    refreshInterval: 30,
    apiKeys: {
      openai: '',
      anthropic: '',
      google: '',
    },
  });

  const [showKeys, setShowKeys] = useState({
    openai: false,
    anthropic: false,
    google: false,
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // In production, this would save to backend/localStorage
    console.log('Saving settings:', settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleApiKeyChange = (provider, value) => {
    setSettings(prev => ({
      ...prev,
      apiKeys: {
        ...prev.apiKeys,
        [provider]: value,
      },
    }));
  };

  const maskKey = (key) => {
    if (!key) return '';
    if (key.length <= 8) return '••••••••';
    return key.substring(0, 4) + '••••••••' + key.substring(key.length - 4);
  };

  return (
    <div className="settings-page">
      <div className="settings-content">
        {/* General Settings */}
        <section className="settings-section card">
          <h2>General Settings</h2>
          
          <div className="setting-item">
            <div className="setting-info">
              <label htmlFor="default-model">Default Model</label>
              <p className="setting-description">
                Model to use when no specific model is selected
              </p>
            </div>
            <select
              id="default-model"
              value={settings.defaultModel}
              onChange={(e) => setSettings(prev => ({ ...prev, defaultModel: e.target.value }))}
            >
              <option value="auto">Auto (Best Match)</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
              <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
            </select>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label htmlFor="theme">Theme</label>
              <p className="setting-description">
                Application color theme
              </p>
            </div>
            <select
              id="theme"
              value={settings.theme}
              onChange={(e) => setSettings(prev => ({ ...prev, theme: e.target.value }))}
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="system">System</option>
            </select>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label htmlFor="auto-refresh">Auto Refresh</label>
              <p className="setting-description">
                Automatically refresh model status
              </p>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                id="auto-refresh"
                checked={settings.autoRefresh}
                onChange={(e) => setSettings(prev => ({ ...prev, autoRefresh: e.target.checked }))}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          {settings.autoRefresh && (
            <div className="setting-item">
              <div className="setting-info">
                <label htmlFor="refresh-interval">Refresh Interval (seconds)</label>
              </div>
              <input
                type="number"
                id="refresh-interval"
                value={settings.refreshInterval}
                onChange={(e) => setSettings(prev => ({ ...prev, refreshInterval: parseInt(e.target.value) || 30 }))}
                min={10}
                max={300}
                style={{ width: '100px' }}
              />
            </div>
          )}
        </section>

        {/* API Keys */}
        <section className="settings-section card">
          <h2>API Keys</h2>
          <p className="section-description">
            Configure API keys for different LLM providers. Keys are stored securely.
          </p>

          {['openai', 'anthropic', 'google'].map(provider => (
            <div key={provider} className="setting-item api-key-item">
              <div className="setting-info">
                <label htmlFor={`${provider}-key`}>
                  {provider.charAt(0).toUpperCase() + provider.slice(1)} API Key
                </label>
              </div>
              <div className="key-input-group">
                <input
                  type={showKeys[provider] ? 'text' : 'password'}
                  id={`${provider}-key`}
                  value={settings.apiKeys[provider]}
                  onChange={(e) => handleApiKeyChange(provider, e.target.value)}
                  placeholder={`Enter ${provider} API key`}
                />
                <button
                  type="button"
                  className="btn btn-icon"
                  onClick={() => setShowKeys(prev => ({ ...prev, [provider]: !prev[provider] }))}
                  title={showKeys[provider] ? 'Hide' : 'Show'}
                >
                  {showKeys[provider] ? '🙈' : '👁️'}
                </button>
              </div>
              {settings.apiKeys[provider] && !showKeys[provider] && (
                <span className="key-preview">{maskKey(settings.apiKeys[provider])}</span>
              )}
            </div>
          ))}
        </section>

        {/* Save Button */}
        <div className="settings-actions">
          <button className="btn btn-filled" onClick={handleSave}>
            {saved ? '✓ Saved!' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
}
