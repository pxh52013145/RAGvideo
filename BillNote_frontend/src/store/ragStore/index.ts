import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { v4 as uuidv4 } from 'uuid'

import type { RagRetrieverResource } from '@/services/rag'

export type RagChatRole = 'user' | 'assistant'

export interface RagChatMessage {
  id: string
  role: RagChatRole
  content: string
  createdAt: string
  resources?: RagRetrieverResource[]
}

export interface RagConversation {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  difyConversationId?: string
  messages: RagChatMessage[]
}

interface RagStore {
  userId: string
  conversations: RagConversation[]
  currentConversationId: string | null

  createConversation: (title?: string) => string
  updateConversation: (id: string, patch: Partial<Omit<RagConversation, 'id' | 'createdAt' | 'messages'>>) => void
  removeConversation: (id: string) => void
  clearConversations: () => void

  setCurrentConversation: (id: string | null) => void
  getCurrentConversation: () => RagConversation | null

  appendMessage: (conversationId: string, msg: RagChatMessage) => void
}

const DEFAULT_CONVERSATION_TITLE = '新对话'
const MAX_CONVERSATIONS = 30
const MAX_MESSAGES_PER_CONVERSATION = 60

const normalizeTitle = (text: string) => {
  const t = (text || '').replace(/\s+/g, ' ').trim()
  if (!t) return DEFAULT_CONVERSATION_TITLE
  return t.length > 32 ? t.slice(0, 32) + '…' : t
}

export const useRagStore = create<RagStore>()(
  persist(
    (set, get) => ({
      userId: `rag-${uuidv4()}`,
      conversations: [],
      currentConversationId: null,

      createConversation: (title?: string) => {
        const id = uuidv4()
        const now = new Date().toISOString()
        const conv: RagConversation = {
          id,
          title: normalizeTitle(title || DEFAULT_CONVERSATION_TITLE),
          createdAt: now,
          updatedAt: now,
          messages: [],
        }

        set(state => ({
          conversations: [conv, ...state.conversations].slice(0, MAX_CONVERSATIONS),
          currentConversationId: id,
        }))

        return id
      },

      updateConversation: (id, patch) =>
        set(state => ({
          conversations: state.conversations.map(c =>
            c.id === id ? { ...c, ...patch, updatedAt: new Date().toISOString() } : c
          ),
        })),

      removeConversation: id =>
        set(state => {
          const conversations = state.conversations.filter(c => c.id !== id)
          const currentConversationId =
            state.currentConversationId === id ? (conversations[0]?.id ?? null) : state.currentConversationId
          return { conversations, currentConversationId }
        }),

      clearConversations: () => set({ conversations: [], currentConversationId: null }),

      setCurrentConversation: id => set({ currentConversationId: id }),
      getCurrentConversation: () => {
        const currentConversationId = get().currentConversationId
        return get().conversations.find(c => c.id === currentConversationId) || null
      },

      appendMessage: (conversationId, msg) =>
        set(state => ({
          conversations: state.conversations.map(c => {
            if (c.id !== conversationId) return c

            const nextMessages = [...(c.messages || []), msg].slice(-MAX_MESSAGES_PER_CONVERSATION)
            const nextTitle =
              c.title === DEFAULT_CONVERSATION_TITLE && msg.role === 'user'
                ? normalizeTitle(msg.content)
                : c.title

            return { ...c, title: nextTitle, messages: nextMessages, updatedAt: new Date().toISOString() }
          }),
        })),
    }),
    {
      name: 'rag-storage',
    }
  )
)
