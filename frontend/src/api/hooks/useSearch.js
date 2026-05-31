import { useQuery, useMutation } from '@tanstack/react-query'
import client from '../client'

export function useSemanticSearch(query, enabled = false) {
  return useQuery({
    queryKey: ['search', 'semantic', query],
    queryFn: () => client.post('/search/semantic', { query, top_k: 10 }).then((r) => r.data),
    enabled: enabled && !!query,
  })
}

export function useKeywordSearch(q, enabled = false) {
  return useQuery({
    queryKey: ['search', 'keyword', q],
    queryFn: () => client.get('/search/keyword', { params: { q } }).then((r) => r.data),
    enabled: enabled && !!q,
  })
}

export function useSearchMutation() {
  return useMutation({
    mutationFn: ({ query, semantic = true }) =>
      semantic
        ? client.post('/search/semantic', { query, top_k: 10 }).then((r) => r.data)
        : client.get('/search/keyword', { params: { q: query } }).then((r) => r.data),
  })
}
