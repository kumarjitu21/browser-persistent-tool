from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db, init_db
from app.models import Session as WorkspaceSession
from app.models import Tab
from app.schemas import (
    SessionDetail,
    SessionSummary,
    SnapshotRequest,
    SnapshotResponse,
    TabOut,
)

app = FastAPI(
    title="Tab Manager",
    description="Local workspace session persistence and recovery",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/snapshot", response_model=SnapshotResponse)
def create_snapshot(payload: SnapshotRequest, db: Session = Depends(get_db)):
    if not payload.tabs:
        raise HTTPException(status_code=400, detail="Snapshot must include at least one tab")

    session = WorkspaceSession(browser=payload.browser)
    db.add(session)
    db.flush()

    for tab in payload.tabs:
        db.add(
            Tab(
                session_id=session.id,
                window_id=tab.window_id,
                url=tab.url,
                title=tab.title,
                active=tab.active,
                pinned=tab.pinned,
                index=tab.index,
            )
        )

    db.commit()
    db.refresh(session)

    return SnapshotResponse(
        session_id=session.id,
        tab_count=len(payload.tabs),
        created_at=session.created_at,
    )


@app.get("/sessions", response_model=list[SessionSummary])
def list_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    tab_counts = (
        select(Tab.session_id, func.count(Tab.id).label("tab_count"))
        .group_by(Tab.session_id)
        .subquery()
    )

    rows = db.execute(
        select(WorkspaceSession, tab_counts.c.tab_count)
        .outerjoin(tab_counts, WorkspaceSession.id == tab_counts.c.session_id)
        .order_by(WorkspaceSession.created_at.desc())
        .limit(limit)
    ).all()

    return [
        SessionSummary(
            id=session.id,
            browser=session.browser,
            label=session.label,
            created_at=session.created_at,
            tab_count=tab_count or 0,
        )
        for session, tab_count in rows
    ]


@app.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.scalar(
        select(WorkspaceSession)
        .options(selectinload(WorkspaceSession.tabs))
        .where(WorkspaceSession.id == session_id)
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    tabs = sorted(session.tabs, key=lambda t: (t.window_id, t.index))
    return SessionDetail(
        id=session.id,
        browser=session.browser,
        label=session.label,
        created_at=session.created_at,
        tabs=[TabOut.model_validate(tab) for tab in tabs],
    )


@app.get("/restore/latest", response_model=SessionDetail)
def restore_latest(db: Session = Depends(get_db)):
    session = db.scalar(
        select(WorkspaceSession)
        .options(selectinload(WorkspaceSession.tabs))
        .order_by(WorkspaceSession.created_at.desc())
        .limit(1)
    )
    if not session:
        raise HTTPException(status_code=404, detail="No sessions available")

    tabs = sorted(session.tabs, key=lambda t: (t.window_id, t.index))
    return SessionDetail(
        id=session.id,
        browser=session.browser,
        label=session.label,
        created_at=session.created_at,
        tabs=[TabOut.model_validate(tab) for tab in tabs],
    )


@app.get("/restore/{session_id}", response_model=SessionDetail)
def restore_session(session_id: int, db: Session = Depends(get_db)):
    return get_session(session_id, db)
