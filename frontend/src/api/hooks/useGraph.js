import { useQuery } from '@tanstack/react-query'
import client from '../client'

export function useFullGraph() {
  return useQuery({
    queryKey: ['graph', 'full'],
    queryFn: () => client.get('/graph/full').then((r) => r.data),
    staleTime: 1000 * 30,
  })
}

export function useSubgraph(nodeId, hops = 2) {
  return useQuery({
    queryKey: ['graph', 'subgraph', nodeId, hops],
    queryFn: () => client.get(`/graph/subgraph/${nodeId}`, { params: { hops } }).then((r) => r.data),
    enabled: !!nodeId,
  })
}

export function useDiscoveredConnections() {
  return useQuery({
    queryKey: ['graph', 'connections'],
    queryFn: () => client.get('/graph/connections').then((r) => r.data),
  })
}
