import request from '@/utils/request'

export interface RagState {
  user_id: string
  current_conversation_id: string | null
  conversations: any[]
  storage_path?: string
}

export const getRagState = () => {
  return request.get('/rag/state') as Promise<RagState>
}

export const setRagState = (data: Partial<RagState>) => {
  return request.post('/rag/state', data) as Promise<RagState>
}

export const setRagCurrentConversation = (conversationId: string) => {
  return request.put(`/rag/current/${conversationId}`) as Promise<RagState>
}

export const upsertRagConversation = (
  conversationId: string,
  patch: { title?: string; difyConversationId?: string; dify_conversation_id?: string } = {}
) => {
  return request.put(`/rag/conversations/${conversationId}`, patch) as Promise<any>
}

export const appendRagMessage = (conversationId: string, msg: any) => {
  return request.post(`/rag/conversations/${conversationId}/messages`, msg) as Promise<any>
}

export const deleteRagConversation = (conversationId: string) => {
  return request.delete(`/rag/conversations/${conversationId}`) as Promise<RagState>
}

export const clearRagConversations = () => {
  return request.delete('/rag/conversations') as Promise<RagState>
}

