from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_event import AuditEvent
from app.api.v1.auth import get_current_user


router = APIRouter(
    prefix="/audit",
    tags=["Audit Trail"],
)


@router.get("/")
def get_audit_events(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    events = (
        db.query(AuditEvent)
        .order_by(AuditEvent.created_at.desc())
        .all()
    )

    return [
        {
            "id": event.id,
            "merchant_id": event.merchant_id,
            "event_type": event.event_type,
            "transaction_id": event.transaction_id,
            "action": event.action,
            "reason": event.reason,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]