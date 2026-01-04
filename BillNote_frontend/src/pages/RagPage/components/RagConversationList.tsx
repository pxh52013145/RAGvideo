import { useMemo } from 'react'
import { MessageCircle, Trash2 } from 'lucide-react'

import { useRagStore } from '@/store/ragStore'

const formatTime = (iso: string) => {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

const normalizePreview = (text: string) => {
  const t = (text || '').replace(/\s+/g, ' ').trim()
  if (!t) return ''
  return t.length > 60 ? t.slice(0, 60) + '…' : t
}

const RagConversationList = ({ onPicked }: { onPicked?: () => void }) => {
  const conversations = useRagStore(state => state.conversations)
  const currentConversationId = useRagStore(state => state.currentConversationId)
  const setCurrentConversation = useRagStore(state => state.setCurrentConversation)
  const clearConversations = useRagStore(state => state.clearConversations)
  const removeConversation = useRagStore(state => state.removeConversation)

  const sorted = useMemo(() => {
    return [...conversations].sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))
  }, [conversations])

  return (
    <>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {sorted.length === 0 ? (
          <div className="p-6 text-sm text-slate-500 text-center">还没有对话记录。</div>
        ) : (
          sorted.map(conv => {
            const active = conv.id === currentConversationId
            const last = conv.messages?.[conv.messages.length - 1]
            const preview = last ? normalizePreview(last.content) : '（暂无消息）'
            return (
              <div
                key={conv.id}
                className={[
                  'w-full rounded-xl group transition-all border flex items-stretch gap-2 p-1',
                  active
                    ? 'bg-white border-brand-200 shadow-sm ring-1 ring-brand-100'
                    : 'border-transparent hover:border-slate-100 hover:bg-slate-50',
                ].join(' ')}
              >
                <button
                  type="button"
                  className="flex-1 min-w-0 text-left p-2 rounded-lg flex gap-3 hover:bg-transparent"
                  onClick={() => {
                    setCurrentConversation(conv.id)
                    onPicked?.()
                  }}
                >
                  <div className="mt-1">
                    <div className="w-8 h-8 rounded-lg bg-brand-50 flex items-center justify-center text-brand-600 group-hover:bg-brand-100 transition-colors">
                      <MessageCircle className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-0.5">
                      <h4 className="font-medium text-slate-800 truncate pr-2 group-hover:text-brand-700 transition-colors">
                        {conv.title || '新对话'}
                      </h4>
                      <span className="text-[10px] text-slate-400 whitespace-nowrap">{formatTime(conv.updatedAt)}</span>
                    </div>
                    <p className="text-xs text-slate-500 truncate group-hover:text-slate-600">{preview}</p>
                  </div>
                </button>

                <button
                  type="button"
                  title="删除该对话"
                  className="self-center mr-1 p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 opacity-0 group-hover:opacity-100 transition-all"
                  onClick={() => {
                    if (!window.confirm('确认删除该对话？')) return
                    removeConversation(conv.id)
                  }}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )
          })
        )}
      </div>

      <div className="p-3 border-t border-slate-100 bg-slate-50">
        <button
          type="button"
          onClick={() => {
            if (!window.confirm('确认清除所有对话历史？')) return
            clearConversations()
          }}
          className="w-full py-2 text-xs font-medium text-rose-600 hover:bg-rose-50 rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          清除所有历史
        </button>
      </div>
    </>
  )
}

export default RagConversationList
