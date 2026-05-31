import { useMutation, useQueryClient } from '@tanstack/react-query'
import client from '../client'

export function useIngestNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload) => client.post('/ingest/note', payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['nodes'] }),
  })
}

export function useIngestFile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file) => {
      const form = new FormData()
      form.append('file', file)
      return client.post('/ingest/file', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['nodes'] }),
  })
}

export function useIngestUrl() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload) => client.post('/ingest/url', payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['nodes'] }),
  })
}

export function useIngestAudio() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (audioFile) => {
      const form = new FormData()
      form.append('file', audioFile)
      return client.post('/ingest/audio', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['nodes'] }),
  })
}
