from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api import deps
from app.models.user import User
from app.models.stats import UsageLog
from datetime import datetime, timedelta

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Returns aggregated stats for the User Dashboard.
    """
    # 1. Total Tokens (User)
    total_tokens = db.query(func.sum(UsageLog.total_tokens)).filter(UsageLog.user_id == current_user.id).scalar() or 0
    
    # 2. Total Cost
    total_cost = db.query(func.sum(UsageLog.estimated_cost)).filter(UsageLog.user_id == current_user.id).scalar() or 0.0

    # 3. Daily Usage (Last 7 Days)
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)
    
    chart_data = {
        "labels": [],
        "datasets": [
            {
                "label": "Tokens",
                "backgroundColor": "#10b981", 
                "data": []
            },
            {
                "label": "Cost ($)",
                "backgroundColor": "#3b82f6",
                "data": []
            }
        ]
    }
    
    # Init dictionary for 7 days
    daily_stats = {}
    for i in range(7):
        day = start_date + timedelta(days=i)
        daily_stats[day] = {"tokens": 0, "cost": 0.0}
        
    # Query logs
    logs = db.query(UsageLog).filter(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= start_date
    ).all()
    
    for log in logs:
        # Check if timestamp is datetime or date (SQLAlchemy usually returns datetime)
        log_date = log.timestamp.date()
        if log_date in daily_stats:
            daily_stats[log_date]["tokens"] += log.total_tokens
            daily_stats[log_date]["cost"] += log.estimated_cost
            
    for day in sorted(daily_stats.keys()):
        chart_data["labels"].append(day.strftime("%a")) # Mon, Tue...
        chart_data["datasets"][0]["data"].append(daily_stats[day]["tokens"])
        chart_data["datasets"][1]["data"].append(round(daily_stats[day]["cost"], 4))

    # 4. Recent Activity (Last 5)
    recent_logs = db.query(UsageLog).filter(
        UsageLog.user_id == current_user.id
    ).order_by(UsageLog.timestamp.desc()).limit(5).all()
    
    recent_activity = []
    for log in recent_logs:
        recent_activity.append({
            "action": "AI Usage",
            "app": log.app_name,
            "details": f"{log.total_tokens} tokens ({log.model_name})",
            "time": log.timestamp.isoformat(), 
            "cost": f"${log.estimated_cost:.4f}"
        })
        
    # 5. Get Active Model Name
    from app.models.domain import AIModel
    active_model = db.query(AIModel).filter(AIModel.is_active == True).first()
    active_model_name = active_model.name if active_model else "No Active Model"

    return {
        "total_tokens": total_tokens,
        "current_cost": f"{total_cost:.4f}",
        "active_model": active_model_name,
        "chart_data": chart_data,
        "recent_activity": recent_activity
    }
