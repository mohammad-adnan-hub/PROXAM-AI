import { Link } from 'react-router-dom'
import { ROUTES } from '../../utils/constants'
import Button from '../../components/shared/Button'

export default function HelpPage() {
  const faqs = [
    {
      q: 'Do students need to install software or extensions?',
      a: 'No. Proxam AI works entirely inside modern standards-compliant web browsers (Chrome, Edge, Firefox, Brave) without any downloads.',
    },
    {
      q: 'What equipment is required for an examination?',
      a: 'A desktop or laptop with a working webcam, microphone, and a stable internet connection.',
    },
    {
      q: 'What happens if my network drops during an exam?',
      a: 'Your answers are continuously synchronized. When your connection resumes, your state will be maintained within your allotted time limit.',
    },
    {
      q: 'Does the system automatically disqualify students?',
      a: 'No. Proxam AI never issues automatic disqualifications. Any flagged events are presented as a neutral event timeline for human review.',
    },
  ]

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <header className="flex items-center justify-between px-8 py-5 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <Link to={ROUTES.HOME} className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[var(--color-primary)] flex items-center justify-center">
            <span className="font-display font-bold text-[var(--color-mint)] text-sm">P</span>
          </div>
          <span className="font-display font-bold text-[var(--color-text-primary)] text-base">Proxam AI</span>
        </Link>
        <Link to={ROUTES.LOGIN}><Button variant="secondary" size="sm">Back to Platform</Button></Link>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-16">
        <h1 className="text-3xl font-display font-bold mb-3">Help & Frequently Asked Questions</h1>
        <p className="text-[var(--color-text-secondary)] mb-8">
          Guidance on system requirements, examinations, and proctoring.
        </p>

        <div className="space-y-4">
          {faqs.map((faq, i) => (
            <div key={i} className="bg-[var(--color-surface)] p-6 rounded-xl border border-[var(--color-border)] shadow-card">
              <h3 className="font-bold text-base mb-2">{faq.q}</h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
