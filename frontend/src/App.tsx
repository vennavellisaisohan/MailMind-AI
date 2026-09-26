import { useState } from 'react'
import './App.css'

type EmailAnalysis = {
  category: string
  priority: string
  summary: string
  tasks: string[]
  deadline: string | null
}

type EmailResult = {
  email_id: string | null
  subject: string
  sender: string
  date: string
  analysis: EmailAnalysis
}

type EmailAnalysisResponse = {
  results: EmailResult[]
}

function App() {
  const [emails, setEmails] = useState<EmailResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyzeEmails = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/emails/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 1,
          max_results: 5,
          query: 'in:anywhere',
        }),
      })

      if (!response.ok) {
        throw new Error(`Backend returned status ${response.status}`)
      }

      const data: EmailAnalysisResponse = await response.json()

      setEmails(data.results)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to analyze emails.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">M</div>

          <div>
            <h1>MailMind AI</h1>
            <p>Intelligent Email Assistant</p>
          </div>
        </div>

        <div className="connection">
          <span className="connection-dot" />
          Gmail Analysis Ready
        </div>
      </header>

      <section className="hero">
        <div>
          <p className="eyebrow">AI EMAIL INTELLIGENCE</p>

          <h2>
            Turn your inbox into
            <span> actionable insights.</span>
          </h2>

          <p className="hero-description">
            MailMind analyzes your emails, identifies important information,
            extracts tasks, and detects deadlines automatically.
          </p>
        </div>

        <button
          className="analyze-button"
          type="button"
          onClick={() => void analyzeEmails()}
          disabled={loading}
        >
          {loading ? 'Analyzing...' : 'Analyze My Emails'}
        </button>
      </section>

      {error && (
        <section className="error-banner">
          <strong>Analysis failed</strong>
          <span>{error}</span>
        </section>
      )}

      <section className="dashboard-header">
        <div>
          <p className="section-label">YOUR INBOX</p>
          <h3>Recent Email Analysis</h3>
        </div>

        <span className="email-count">
          {emails.length} {emails.length === 1 ? 'email' : 'emails'}
        </span>
      </section>

      {emails.length === 0 && !loading && !error && (
        <section className="empty-state">
          <div className="empty-icon">✦</div>

          <h3>Your AI inbox is waiting</h3>

          <p>
            Click <strong>Analyze My Emails</strong> to retrieve and analyze
            your Gmail messages.
          </p>
        </section>
      )}

      {loading && (
        <section className="loading-state">
          <div className="spinner" />
          <h3>Analyzing your emails...</h3>
          <p>
            MailMind AI is reading your inbox and extracting useful insights.
          </p>
        </section>
      )}

      <section className="email-list">
        {emails.map((email) => (
          <article className="email-card" key={email.email_id ?? email.subject}>
            <div className="email-card-header">
              <div>
                <span className="category">
                  {email.analysis.category}
                </span>

                <h3>{email.subject || 'No subject'}</h3>

                <p className="sender">
                  {email.sender || 'Unknown sender'}
                </p>
              </div>

              <span
                className={
                  'priority priority-' +
                  email.analysis.priority.toLowerCase()
                }
              >
                {email.analysis.priority}
              </span>
            </div>

            <div className="analysis-section">
              <span className="analysis-label">AI SUMMARY</span>

              <p>{email.analysis.summary}</p>
            </div>

            {email.analysis.tasks.length > 0 && (
              <div className="analysis-section">
                <span className="analysis-label">ACTION ITEMS</span>

                <ul className="task-list">
                  {email.analysis.tasks.map((task) => (
                    <li key={task}>
                      <span className="task-check">✓</span>
                      {task}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {email.analysis.deadline && (
              <div className="deadline">
                <span>⏰</span>

                <div>
                  <strong>Deadline</strong>
                  <p>{email.analysis.deadline}</p>
                </div>
              </div>
            )}

            <div className="email-date">
              {email.date}
            </div>
          </article>
        ))}
      </section>
    </main>
  )
}

export default App