import { useMutation } from '@tanstack/react-query'
import client from '../client'

export function useAskQuestion() {
  return useMutation({
    mutationFn: ({ question, top_k = 5 }) =>
      client.post('/qa/ask', { question, top_k }).then((r) => r.data),
  })
}
