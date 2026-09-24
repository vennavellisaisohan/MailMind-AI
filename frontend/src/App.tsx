import { useCallback, useEffect, useState } from 'react'
import './App.css'

type HealthResponse = {
  status: string
  service: string
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const checkBackend = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/health')

      if (!response.ok) {
        throw new Error('Backend returned status ' + response.status)
      }

      const data: HealthResponse = await response.json()
      setHealth(data)
    } catch {
      setHealth(null)
      setError('Unable to connect to the backend.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void checkBackend()
  }, [checkBackend])

  const isConnected = health?.status === 'healthy'

  return (
    <main className="app">
      <section className="card">
        <div className="brand-icon">M</div>

        <p className="eyebrow">MAILMIND AI</p>

        <h1>Your intelligent email assistant</h1>

        <p className="description">
          A foundation for intelligent email analysis, task extraction,
          and smart reminders.
        </p>

        <div className={'status ' + (isConnected ? 'success' : 'error')}>
          <span className="status-dot" />

          <div>
            <strong>
              {isConnected ? 'Backend Connected' : 'Backend Disconnected'}
            </strong>

            <p>
              {isConnected
                ? health.service + ' is running successfully.'
                : error ?? 'Checking backend connection...'}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => void checkBackend()}
          disabled={loading}
        >
          {loading ? 'Checking...' : 'Check Connection'}
        </button>

        <p className="footer-text">
          Phase 1 · Development Foundation
        </p>
      </section>
    </main>
  )
}

export default App
