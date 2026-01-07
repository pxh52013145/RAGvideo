import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useSystemStore, type DuplicateStrategy } from '@/store/configStore'

const IngestSetting = () => {
  const duplicateStrategy = useSystemStore(state => state.duplicateStrategy)
  const setDuplicateStrategy = useSystemStore(state => state.setDuplicateStrategy)

  return (
    <div className="h-full overflow-auto p-6">
      <div className="max-w-2xl">
        <div className="text-xl font-semibold text-slate-900">入库设置</div>
        <div className="mt-1 text-sm text-slate-600">设置批量入库时遇到重复视频的处理方式。</div>

        <div className="mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="space-y-2">
            <div className="text-sm font-medium text-slate-900">重复处理策略</div>
            <Select
              value={duplicateStrategy}
              onValueChange={v => setDuplicateStrategy(v as DuplicateStrategy)}
            >
              <SelectTrigger className="h-9 w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ask">每次提示</SelectItem>
                <SelectItem value="skip">跳过已存在</SelectItem>
                <SelectItem value="regenerate">直接重新生成</SelectItem>
              </SelectContent>
            </Select>
            <div className="text-xs text-slate-500">
              “已存在”基于同一平台的视频 ID（或本地文件 URL）判断；选择“直接重新生成”会覆盖原任务。
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default IngestSetting

