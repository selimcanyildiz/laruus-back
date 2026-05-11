from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.parameters import get_int
from app.db.models.credit_usage import CreditUsage


def get_today_usage(db: Session, user_id: UUID) -> int:
    row = (
        db.query(CreditUsage)
        .filter(
            CreditUsage.user_id == user_id,
            CreditUsage.usage_date == date.today(),
        )
        .first()
    )
    return row.amount if row else 0


def get_daily_limit(db: Session) -> int:
    return get_int(db, "daily_credit_limit")


def consume_credits(db: Session, user_id: UUID, amount: int) -> int:
    """`amount` kredi düşmeye çalışır. Limit aşılırsa 403 fırlatır.

    Başarılı olursa bugün için yeni kalan krediyi döner.
    """
    if amount < 0:
        raise HTTPException(status_code=400, detail="Negative amount not allowed")
    if amount == 0:
        return get_daily_limit(db) - get_today_usage(db, user_id)

    limit = get_daily_limit(db)
    today = date.today()

    row = (
        db.query(CreditUsage)
        .filter(CreditUsage.user_id == user_id, CreditUsage.usage_date == today)
        .first()
    )
    current = row.amount if row else 0

    if current + amount > limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Günlük kredi limiti aşıldı. Bugünkü kullanım: {current}/{limit}, "
                f"istenen ek: {amount}"
            ),
        )

    if row:
        row.amount = current + amount
    else:
        row = CreditUsage(user_id=user_id, usage_date=today, amount=amount)
        db.add(row)
    db.commit()

    return limit - (current + amount)
