import RagVideoPanel from '@/pages/RagPage/components/RagVideoPanel'
import RagChatPanel from '@/pages/RagPage/components/RagChatPanel'
import RagReferencesPanel from '@/pages/RagPage/components/RagReferencesPanel'

const RagPage = () => {
  return (
    <div className="flex h-full w-full">
      <div className="w-80 lg:w-96 bg-white border-r border-slate-200 flex flex-col z-10 shadow-sm">
        <RagVideoPanel />
      </div>

      <div className="flex-1 flex flex-col bg-slate-50/50 relative">
        <RagChatPanel />
      </div>

      <div className="hidden xl:flex w-80 bg-white border-l border-slate-200 flex-col">
        <RagReferencesPanel />
      </div>
    </div>
  )
}

export default RagPage
