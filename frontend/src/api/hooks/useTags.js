import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import client from '../client'

export function useTags() {
  return useQuery({
    queryKey: ['tags'],
    queryFn: () => client.get('/tags').then((r) => r.data),
  })
}

export function useTimeline(limit = 20, offset = 0) {
  return useQuery({
    queryKey: ['timeline', limit, offset],
    queryFn: () => client.get('/timeline', { params: { limit, offset } }).then((r) => r.data),
  })
}
