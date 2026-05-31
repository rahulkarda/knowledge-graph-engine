import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import client from '../client'

export function useNodes(params = {}) {
  return useQuery({
    queryKey: ['nodes', params],
    queryFn: () => client.get('/nodes', { params }).then((r) => r.data),
  })
}

export function useNode(id) {
  return useQuery({
    queryKey: ['nodes', id],
    queryFn: () => client.get(`/nodes/${id}`).then((r) => r.data),
    enabled: !!id,
  })
}

export function useNodeNeighbors(id) {
  return useQuery({
    queryKey: ['nodes', id, 'neighbors'],
    queryFn: () => client.get(`/nodes/${id}/neighbors`).then((r) => r.data),
    enabled: !!id,
  })
}

export function useDeleteNode() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id) => client.delete(`/nodes/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['nodes'] }),
  })
}
