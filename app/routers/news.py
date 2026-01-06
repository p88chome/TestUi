from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api import deps
from app.models.user import User
from app.models.news import PlatformNews
from app.schemas.news import NewsCreate, NewsOut

router = APIRouter(prefix="/news", tags=["news"])

@router.get("", response_model=List[NewsOut])
def get_news(
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get latest published news.
    """
    return db.query(PlatformNews).filter(
        PlatformNews.is_published == True
    ).order_by(PlatformNews.created_at.desc()).limit(limit).all()

@router.post("", response_model=NewsOut)
def publish_news(
    news: NewsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser) # Only Admin
):
    """
    Publish new platform news (Admin Only).
    """
    db_news = PlatformNews(
        title=news.title,
        content=news.content,
        is_published=news.is_published,
        author_id=current_user.id
    )
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

@router.delete("/{news_id}", status_code=204)
def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    news = db.query(PlatformNews).filter(PlatformNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    db.delete(news)
    db.commit()
    return None

@router.put("/{news_id}", response_model=NewsOut)
def update_news(
    news_id: int,
    news_in: NewsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    news = db.query(PlatformNews).filter(PlatformNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
        
    news.title = news_in.title
    news.content = news_in.content
    news.is_published = news_in.is_published
    
    db.commit()
    db.refresh(news)
    return news
