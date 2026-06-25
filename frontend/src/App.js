import { useState } from 'react';

const animationStyles = ['Cinematic', 'Cartoon', 'Minimal', 'Action', 'Fantasy'];

function App() {
  const [script, setScript] = useState('');
  const [scriptFileName, setScriptFileName] = useState('');
  const [scenes, setScenes] = useState([]);
  const [plan, setPlan] = useState(null);
  const [sceneOptions, setSceneOptions] = useState([]);
  const [animationResult, setAnimationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const clearGeneratedState = () => {
    setScenes([]);
    setPlan(null);
    setSceneOptions([]);
    setAnimationResult(null);
    setError('');
  };

  const handleFileUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setScriptFileName(file.name);
    clearGeneratedState();

    const reader = new FileReader();
    reader.onload = (e) => {
      setScript(e.target.result || '');
    };
    reader.readAsText(file, 'UTF-8');
  };

  const handleScriptChange = (value) => {
    setScript(value);
    clearGeneratedState();
    setScriptFileName('');
  };

  const getErrorText = async (response) => {
    const text = await response.text();
    if (!text) {
      return response.statusText || 'Unknown server error';
    }

    try {
      const parsed = JSON.parse(text);
      return parsed.error || JSON.stringify(parsed);
    } catch {
      return text;
    }
  };

  const updateSceneOptions = (assetList) => {
    const options = assetList.map((asset) => ({
      sceneNumber: asset.sceneNumber,
      enabled: true,
      animationStyle: 'Cinematic',
      imagePrompt: asset.imagePrompt,
      transition: asset.transition,
    }));
    setSceneOptions(options);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    setScenes([]);
    setPlan(null);
    setSceneOptions([]);
    setAnimationResult(null);

    try {
      const parseResponse = await fetch('/api/parse-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script }),
      });

      if (!parseResponse.ok) {
        const errorMessage = await getErrorText(parseResponse);
        throw new Error(errorMessage || 'Failed to parse script');
      }

      const parseData = await parseResponse.json();
      setScenes(parseData.scenes || []);

      const planResponse = await fetch('/api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script }),
      });

      if (!planResponse.ok) {
        const errorMessage = await getErrorText(planResponse);
        throw new Error(errorMessage || 'Failed to generate plan');
      }

      const planData = await planResponse.json();
      setPlan(planData);
      updateSceneOptions(planData.sceneAssets || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOptionChange = (sceneNumber, field, value) => {
    setSceneOptions((current) =>
      current.map((option) =>
        option.sceneNumber === sceneNumber ? { ...option, [field]: value } : option
      )
    );
  };

  const handleCreateAnimation = async () => {
    setError('');
    setLoading(true);
    setAnimationResult(null);

    const selectedScenes = sceneOptions.filter((option) => option.enabled);
    if (selectedScenes.length === 0) {
      setError('Please select at least one scene to animate.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/create-animation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script, options: selectedScenes }),
      });

      if (!response.ok) {
        const errorMessage = await getErrorText(response);
        throw new Error(errorMessage || 'Failed to create animation');
      }

      const data = await response.json();
      setAnimationResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>AI Script-to-Animation</h1>
        <p>Upload a script file or paste your story prompt, then generate a plan and create an animation video.</p>
      </header>

      <form className="script-form" onSubmit={handleSubmit}>
        <div className="upload-row">
          <label className="upload-button" htmlFor="script-file">
            Upload Script File
          </label>
          <input
            id="script-file"
            type="file"
            accept=".txt"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <span className="upload-info">{scriptFileName || 'No file selected'}</span>
        </div>

        <label htmlFor="script">Story prompt or screenplay text</label>
        <textarea
          id="script"
          value={script}
          onChange={(event) => handleScriptChange(event.target.value)}
          placeholder="Type your story here..."
          rows={8}
        />

        <button type="submit" disabled={!script.trim() || loading}>
          {loading ? 'Generating...' : 'Generate animation plan'}
        </button>
      </form>

      {error && <div className="error-box">{error}</div>}

      {scenes.length > 0 && (
        <section>
          <h2>Scene Breakdown</h2>
          <div className="scene-grid">
            {scenes.map((scene) => (
              <article key={scene.sceneNumber} className="scene-card">
                <h3>Scene {scene.sceneNumber}</h3>
                <p><strong>Description:</strong> {scene.description}</p>
                <p><strong>Characters:</strong> {scene.characters?.join(', ')}</p>
                <p><strong>Setting:</strong> {scene.setting}</p>
                <p><strong>Mood:</strong> {scene.mood}</p>
                <p><strong>Action:</strong> {scene.action}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {plan && (
        <section>
          <h2>Animation Plan</h2>

          <div className="plan-section">
            <h3>Choose Scenes and Animation Style</h3>
            <div className="scene-options">
              {sceneOptions.map((option) => (
                <div key={option.sceneNumber} className="scene-option">
                  <div className="option-header">
                    <label>
                      <input
                        type="checkbox"
                        checked={option.enabled}
                        onChange={(event) => handleOptionChange(option.sceneNumber, 'enabled', event.target.checked)}
                      />
                      <span>Scene {option.sceneNumber}</span>
                    </label>
                  </div>

                  <div className="select-row">
                    <div className="select-group">
                      <label>Animation Style</label>
                      <select
                        value={option.animationStyle}
                        onChange={(event) => handleOptionChange(option.sceneNumber, 'animationStyle', event.target.value)}
                      >
                        {animationStyles.map((style) => (
                          <option key={style} value={style}>{style}</option>
                        ))}
                      </select>
                    </div>

                    <div className="select-group">
                      <label>Transition</label>
                      <input
                        type="text"
                        value={option.transition}
                        onChange={(event) => handleOptionChange(option.sceneNumber, 'transition', event.target.value)}
                      />
                    </div>
                  </div>

                  <p><strong>Prompt:</strong> {option.imagePrompt}</p>
                </div>
              ))}
            </div>

            <button
              type="button"
              className="create-button"
              onClick={handleCreateAnimation}
              disabled={loading || sceneOptions.every((option) => !option.enabled)}
            >
              {loading ? 'Creating animation...' : 'Create animation video'}
            </button>
          </div>

          <div className="plan-section">
            <h3>Scene Assets</h3>
            {plan.sceneAssets?.map((asset) => (
              <div key={asset.sceneNumber} className="asset-card">
                <h4>Scene {asset.sceneNumber}</h4>
                <p><strong>Image prompt:</strong> {asset.imagePrompt}</p>
                <p><strong>Animation notes:</strong> {asset.animationNotes}</p>
                <p><strong>Transition:</strong> {asset.transition}</p>
              </div>
            ))}
          </div>

          <div className="plan-section">
            <h3>Audio Assets</h3>
            {plan.audioAssets?.map((audio) => (
              <div key={audio.sceneNumber} className="asset-card">
                <h4>Scene {audio.sceneNumber}</h4>
                <p><strong>Dialogue:</strong> {audio.dialogue}</p>
                <p><strong>Voice style:</strong> {audio.voiceStyle}</p>
                <p><strong>Sound effects:</strong> {audio.soundEffects?.join(', ')}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {animationResult && (
        <section>
          <h2>Generated Animation</h2>
          <div className="video-preview">
            <h3>{animationResult.title || 'Your animation video'}</h3>
            {animationResult.videoUrl ? (
              <video controls width="100%" src={animationResult.videoUrl} />
            ) : (
              <div className="video-placeholder">Animation created successfully.</div>
            )}
            {animationResult.description && <p>{animationResult.description}</p>}
            {animationResult.selectedScenes && (
              <div className="selected-summary">
                <strong>Selected scenes:</strong>{' '}
                {animationResult.selectedScenes.map((scene) => scene.sceneNumber).join(', ')}
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
