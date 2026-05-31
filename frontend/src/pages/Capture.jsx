import { useState } from 'react'
import { useIngestNote, useIngestFile, useIngestUrl, useIngestAudio } from '../api/hooks/useIngest'
import { LoadingSpinner } from '../components/shared'
import toast from 'react-hot-toast'
import { useDropzone } from 'react-dropzone'
import { FileText, Globe, Mic, Upload, Square, Circle } from 'lucide-react'
import { clsx } from 'clsx'

const TABS = [
  { id: 'note', label: 'Note', icon: FileText },
  { id: 'file', label: 'File', icon: Upload },
  { id: 'url', label: 'URL', icon: Globe },
  { id: 'voice', label: 'Voice', icon: Mic },
]

function NoteTab() {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const { mutate, isPending } = useIngestNote()

  const submit = () => {
    if (!title.trim() || !content.trim()) return toast.error('Title and content are required.')
    mutate({ title, content }, {
      onSuccess: (data) => {
        toast.success(`Saved! Found ${data.entities_found} entities.`)
        setTitle('')
        setContent('')
      },
      onError: () => toast.error('Failed to save note.'),
    })
  }

  return (
    <div className="space-y-4">
      <input
        className="input text-lg font-medium"
        placeholder="Note title…"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        className="input resize-none h-52 font-mono text-sm"
        placeholder="Start writing your thoughts…"
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <div className="flex items-center justify-between">
        <span className="text-gray-500 text-xs">{content.split(/\s+/).filter(Boolean).length} words</span>
        <button className="btn-primary flex items-center gap-2" onClick={submit} disabled={isPending}>
          {isPending ? <LoadingSpinner size="sm" /> : null}
          Save Note
        </button>
      </div>
    </div>
  )
}

function FileTab() {
  const { mutate, isPending } = useIngestFile()
  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'], 'text/plain': ['.txt'] },
    maxFiles: 1,
    onDrop: (files) => {
      if (!files[0]) return
      mutate(files[0], {
        onSuccess: (d) => toast.success(`Imported "${d.title}" — ${d.word_count} words`),
        onError: () => toast.error('Failed to import file.'),
      })
    },
  })

  return (
    <div
      {...getRootProps()}
      className={clsx(
        'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors',
        isDragActive ? 'border-brand-500 bg-brand-500/10' : 'border-gray-700 hover:border-gray-500'
      )}
    >
      <input {...getInputProps()} />
      <Upload size={32} className="mx-auto text-gray-500 mb-3" />
      {isPending ? (
        <div className="flex flex-col items-center gap-2">
          <LoadingSpinner />
          <p className="text-gray-400 text-sm">Processing…</p>
        </div>
      ) : (
        <>
          <p className="text-gray-300 font-medium">Drop a file here or click to browse</p>
          <p className="text-gray-500 text-sm mt-1">PDF, DOCX, TXT — up to 50 MB</p>
        </>
      )}
    </div>
  )
}

function UrlTab() {
  const [url, setUrl] = useState('')
  const { mutate, isPending } = useIngestUrl()

  const submit = () => {
    if (!url.trim()) return
    mutate({ url }, {
      onSuccess: (d) => { toast.success(`Scraped: ${d.title}`); setUrl('') },
      onError: () => toast.error('Could not scrape URL.'),
    })
  }

  return (
    <div className="space-y-4">
      <input className="input text-sm" placeholder="https://…" value={url} onChange={(e) => setUrl(e.target.value)} />
      <button className="btn-primary flex items-center gap-2" onClick={submit} disabled={isPending || !url.trim()}>
        {isPending ? <LoadingSpinner size="sm" /> : <Globe size={16} />}
        Scrape & Ingest
      </button>
    </div>
  )
}

function VoiceTab() {
  const [recording, setRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [chunks, setChunks] = useState([])
  const { mutate, isPending } = useIngestAudio()

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mr = new MediaRecorder(stream)
    const c = []
    mr.ondataavailable = (e) => c.push(e.data)
    mr.onstop = () => {
      const blob = new Blob(c, { type: 'audio/webm' })
      const file = new File([blob], `voice-${Date.now()}.webm`, { type: 'audio/webm' })
      mutate(file, {
        onSuccess: (d) => toast.success(`Transcribed: ${d.word_count} words`),
        onError: () => toast.error('Transcription failed.'),
      })
    }
    mr.start()
    setMediaRecorder(mr)
    setChunks(c)
    setRecording(true)
  }

  const stopRecording = () => {
    mediaRecorder?.stop()
    setRecording(false)
  }

  return (
    <div className="flex flex-col items-center gap-6 py-10">
      <button
        onClick={recording ? stopRecording : startRecording}
        disabled={isPending}
        className={clsx(
          'w-20 h-20 rounded-full flex items-center justify-center text-white transition-all',
          recording ? 'bg-red-600 hover:bg-red-700 animate-pulse' : 'bg-brand-600 hover:bg-brand-700'
        )}
      >
        {recording ? <Square size={28} /> : <Circle size={28} />}
      </button>
      <p className="text-gray-400 text-sm">
        {isPending ? 'Transcribing…' : recording ? 'Recording — click to stop' : 'Click to start recording'}
      </p>
      {isPending && <LoadingSpinner />}
    </div>
  )
}

export default function Capture() {
  const [activeTab, setActiveTab] = useState('note')

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-100 mb-6">Capture</h1>

      <div className="flex gap-1 mb-6 bg-gray-900 border border-gray-800 rounded-xl p-1">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={clsx(
              'flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === id ? 'bg-brand-600 text-white' : 'text-gray-400 hover:text-gray-100'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      <div className="card">
        {activeTab === 'note' && <NoteTab />}
        {activeTab === 'file' && <FileTab />}
        {activeTab === 'url' && <UrlTab />}
        {activeTab === 'voice' && <VoiceTab />}
      </div>
    </div>
  )
}
