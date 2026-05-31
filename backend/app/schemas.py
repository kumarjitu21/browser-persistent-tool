from datetime import datetime

from pydantic import BaseModel, Field


class TabSnapshot(BaseModel):
    window_id: int
    url: str
    title: str = ""
    active: bool = False
    pinned: bool = False
    index: int = 0


class SnapshotRequest(BaseModel):
    browser: str = "chrome"
    tabs: list[TabSnapshot] = Field(default_factory=list)


class SnapshotResponse(BaseModel):
    session_id: int
    tab_count: int
    created_at: datetime


class TabOut(BaseModel):
    window_id: int
    url: str
    title: str
    active: bool
    pinned: bool
    index: int

    model_config = {"from_attributes": True}


class SessionSummary(BaseModel):
    id: int
    browser: str
    label: str | None
    created_at: datetime
    tab_count: int

    model_config = {"from_attributes": True}


class SessionDetail(BaseModel):
    id: int
    browser: str
    label: str | None
    created_at: datetime
    tabs: list[TabOut]

    model_config = {"from_attributes": True}
