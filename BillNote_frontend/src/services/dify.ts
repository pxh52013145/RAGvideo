import request from '@/utils/request'

export interface DifyConfigPayload {
  base_url: string
  dataset_id: string
  note_dataset_id?: string
  transcript_dataset_id?: string
  indexing_technique: string
  app_user: string
  timeout_seconds: number
  service_api_key_set: boolean
  app_api_key_set: boolean
  service_api_key_masked?: string
  app_api_key_masked?: string
  config_path?: string
  active_profile?: string
}

export interface DifyConfigUpdateRequest {
  base_url?: string
  dataset_id?: string
  note_dataset_id?: string
  transcript_dataset_id?: string
  service_api_key?: string
  app_api_key?: string
  app_user?: string
  indexing_technique?: string
  timeout_seconds?: number
}

export const getDifyConfig = async () => {
  return (await request.get('/dify_config')) as DifyConfigPayload
}

export const updateDifyConfig = async (data: DifyConfigUpdateRequest) => {
  return (await request.post('/dify_config', data)) as DifyConfigPayload
}

export interface DifyProfileSummary {
  name: string
  base_url?: string
  dataset_id?: string
  note_dataset_id?: string
  transcript_dataset_id?: string
  indexing_technique?: string
  app_user?: string
  timeout_seconds?: number
  service_api_key_set?: boolean
  app_api_key_set?: boolean
  service_api_key_masked?: string
  app_api_key_masked?: string
}

export interface DifyProfilesPayload {
  active_profile: string
  profiles: DifyProfileSummary[]
  config_path?: string
}

export interface DifyProfileActivateRequest {
  name: string
}

export type DifyProfileUpsertRequest = DifyConfigUpdateRequest & {
  name: string
  clone_from?: string
  activate?: boolean
}

export const getDifyProfiles = async () => {
  return (await request.get('/dify_profiles')) as DifyProfilesPayload
}

export const activateDifyProfile = async (name: string) => {
  return (await request.post('/dify_profiles/activate', { name } as DifyProfileActivateRequest)) as DifyProfilesPayload
}

export const upsertDifyProfile = async (data: DifyProfileUpsertRequest) => {
  return (await request.post('/dify_profiles', data)) as DifyProfilesPayload
}

export const deleteDifyProfile = async (name: string) => {
  const encoded = encodeURIComponent(name)
  return (await request.delete(`/dify_profiles/${encoded}`)) as DifyProfilesPayload
}
