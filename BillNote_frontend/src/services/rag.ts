import request from '@/utils/request'

export interface RagRetrieverResource {
  position: number
  dataset_id: string
  dataset_name: string
  document_id: string
  document_name: string
  segment_id: string
  score: number
  content: string
}

export interface RagChatRequest {
  query: string
  conversation_id?: string
  user?: string
}

export interface RagChatResponse {
  answer: string
  conversation_id?: string
  message_id?: string
  task_id?: string
  retriever_resources: RagRetrieverResource[]
  raw?: any
}

export const ragChat = (data: RagChatRequest) => {
  return request.post('/rag/chat', data) as Promise<RagChatResponse>
}
