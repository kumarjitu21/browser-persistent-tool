export interface TabSnapshot {
  window_id: number;
  url: string;
  title: string;
  active: boolean;
  pinned: boolean;
  index: number;
}

export interface SnapshotPayload {
  browser: string;
  tabs: TabSnapshot[];
}

export interface SnapshotResponse {
  session_id: number;
  tab_count: number;
  created_at: string;
}

export interface SessionDetail {
  id: number;
  browser: string;
  label: string | null;
  created_at: string;
  tabs: TabSnapshot[];
}
