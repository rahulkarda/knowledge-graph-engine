import { useState } from 'react'
import { useAskQuestion } from '../api/hooks/useQA'
import { LoadingSpinner } from '../components/shared'
import { Link } from 'react-router-dom'
import { Send, MessageSquare } from 'lucide-react'

export default function QAPage() {
  const [question, setQuestion] = useState('')
  const [history, setHistory] = useState([])
  const { mutate, isPending } = useAskQuestion()

  const submit = () => {
    if (!question.trim()) return
    const q = question
    setQuestion('')
    mutate({ question: q }, {
      onSuccess: (data) => setHistory(h => [...h, data]),
      onError: () => setHistory(h => [...h, { question: q, answer: 'Error fetching answer.', sources: [] }]),
    })
  }

  return (
    <div className="max-w-2xl flex flex-col" style={{ height: 'calc(100vh - 96px)' }}>
      <h1 className="text-2xl font-bold text-gray-100 mb-4">Ask AI</h1>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {history.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <MessageSquare size={40} className="text-gray-700 mb-4" />
            <p className="text-gray-400">Ask anything about your knowledge base.</p>
            <p className="text-gray-600 text-sm mt-1">Try: "What do I know about machine learning?"</p>
          </div>
        )}
        {history.map((item, i) => (
          <div key={i} className="space-y-2">
            <div className="flex justify-end">
              <div className="bg-brand-600/20 border border-brand-600/30 rounded-xl px-4 py-2 text-sm text-gray-100 max-w-sm">
                {item.question}
              </div>
            </div>
            <div className="card max-w-none">
              <p className="text-gray-200 text-sm leading-relaxed">{item.answer}</p>
              {item.sources?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-800">
                  <p className="text-gray-500 text-xs mb-1.5">Sources</p>
                  <div className="flex flex-col gap-1">
                    {item.sources.map(s => (
                      <Link key={s.node_id} to={`/nodes/${s.node_id}`}
                        className="text-brand-400 text-xs hover:underline">
                        → {s.title}
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {isPending && (
          <div className="card flex items-center gap-2">
            <LoadingSpinner size="sm" />
            <span className="text-gray-500 text-sm">Thinking…</span>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <input
          className="input flex-1"
          placeholder="Ask a question…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !isPending && submit()}
        />
        <button className="btn-primary px-4" onClick={submit} disabled={isPending || !question.trim()}>
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
