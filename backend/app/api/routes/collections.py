from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime

from app.database.session import get_db
from app.database.models import Collection, CollectionSong, User, Song
from app.api.deps import get_current_user

router = APIRouter(prefix="/collections", tags=["collections"])

# ------------------------------------------------------------------
# Pydantic Models
# ------------------------------------------------------------------

class CollectionBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = False

class CollectionCreate(CollectionBase):
    pass

class CollectionUpdate(CollectionBase):
    title: Optional[str] = None
    is_public: Optional[bool] = None

class CollectionItem(BaseModel):
    song_id: str
    order_index: int
    notes: Optional[str] = None
    added_at: datetime
    
    # Nested song data for frontend convenience
    song_title: str
    song_artist: Optional[str] = None
    song_duration: Optional[float] = None

class CollectionDetail(CollectionBase):
    id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    item_count: int
    items: List[CollectionItem] = []

    class Config:
        from_attributes = True

class CollectionList(CollectionBase):
    id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    item_count: int

    class Config:
        from_attributes = True

class AddItemRequest(BaseModel):
    song_id: str
    notes: Optional[str] = None

# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@router.post("/", response_model=CollectionDetail)
async def create_collection(
    collection: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new collection"""
    import uuid
    new_id = str(uuid.uuid4())
    
    db_collection = Collection(
        id=new_id,
        user_id=current_user.id,
        title=collection.title,
        description=collection.description,
        is_public=collection.is_public
    )
    
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    
    # Return with empty items
    return {
        **db_collection.__dict__,
        "item_count": 0,
        "items": []
    }

@router.get("/", response_model=List[CollectionList])
async def list_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's collections"""
    # Create subquery for item count
    count_subquery = (
        select(func.count(CollectionSong.song_id))
        .where(CollectionSong.collection_id == Collection.id)
        .correlate(Collection)
        .scalar_subquery()
    )

    stmt = (
        select(Collection, count_subquery.label("item_count"))
        .where(Collection.user_id == current_user.id)
        .order_by(Collection.updated_at.desc())
    )
    
    results = db.execute(stmt).all()
    
    # Map results to Pydantic model
    return [
        {
            **collection.__dict__,
            "item_count": item_count
        }
        for collection, item_count in results
    ]

@router.get("/{collection_id}", response_model=CollectionDetail)
async def get_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get collection details with items"""
    collection = db.scalar(
        select(Collection)
        .where(Collection.id == collection_id)
        .where(Collection.user_id == current_user.id)
    )
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
        
    # Fetch items with song details
    items_query = (
        select(CollectionSong, Song)
        .join(Song, CollectionSong.song_id == Song.id)
        .where(CollectionSong.collection_id == collection_id)
        .order_by(CollectionSong.order_index)
    )
    
    items_results = db.execute(items_query).all()
    
    items = [
        {
            "song_id": item.song_id,
            "order_index": item.order_index,
            "notes": item.notes,
            "added_at": item.added_at,
            "song_title": song.title,
            "song_artist": song.artist,
            "song_duration": song.duration
        }
        for item, song in items_results
    ]
    
    return {
        **collection.__dict__,
        "item_count": len(items),
        "items": items
    }

@router.put("/{collection_id}", response_model=CollectionDetail)
async def update_collection(
    collection_id: str,
    update_data: CollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update collection metadata"""
    collection = db.scalar(
        select(Collection)
        .where(Collection.id == collection_id)
        .where(Collection.user_id == current_user.id)
    )
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
        
    if update_data.title is not None:
        collection.title = update_data.title
    if update_data.description is not None:
        collection.description = update_data.description
    if update_data.is_public is not None:
        collection.is_public = update_data.is_public
        
    db.commit()
    db.refresh(collection)
    
    # lazy load items to satisfy response model
    # (In a real app, might want to optimize this or return a simpler model)
    items_query = (
        select(CollectionSong, Song)
        .join(Song, CollectionSong.song_id == Song.id)
        .where(CollectionSong.collection_id == collection_id)
        .order_by(CollectionSong.order_index)
    )
    items_results = db.execute(items_query).all()
    items = [
        {
            "song_id": item.song_id,
            "order_index": item.order_index,
            "notes": item.notes,
            "added_at": item.added_at,
            "song_title": song.title,
            "song_artist": song.artist,
            "song_duration": song.duration
        }
        for item, song in items_results
    ]

    return {
        **collection.__dict__,
        "item_count": len(items),
        "items": items
    }

@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a collection"""
    collection = db.scalar(
        select(Collection)
        .where(Collection.id == collection_id)
        .where(Collection.user_id == current_user.id)
    )
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
        
    db.delete(collection)
    db.commit()
    return {"ok": True}

@router.post("/{collection_id}/items")
async def add_item_to_collection(
    collection_id: str,
    item_data: AddItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a song to a collection"""
    collection = db.scalar(
        select(Collection)
        .where(Collection.id == collection_id)
        .where(Collection.user_id == current_user.id)
    )
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    song = db.scalar(select(Song).where(Song.id == item_data.song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
        
    # Check if already exists
    exists = db.scalar(
        select(CollectionSong)
        .where(CollectionSong.collection_id == collection_id)
        .where(CollectionSong.song_id == item_data.song_id)
    )
    
    if exists:
        raise HTTPException(status_code=400, detail="Song already in collection")
        
    # Get max order index
    max_order = db.scalar(
        select(func.max(CollectionSong.order_index))
        .where(CollectionSong.collection_id == collection_id)
    )
    new_order = (max_order or 0) + 1
    
    new_item = CollectionSong(
        collection_id=collection_id,
        song_id=item_data.song_id,
        order_index=new_order,
        notes=item_data.notes
    )
    
    db.add(new_item)
    db.commit()
    
    return {"ok": True}

@router.delete("/{collection_id}/items/{song_id}")
async def remove_item_from_collection(
    collection_id: str,
    song_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a song from a collection"""
    collection = db.scalar(
        select(Collection)
        .where(Collection.id == collection_id)
        .where(Collection.user_id == current_user.id)
    )
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
        
    item = db.scalar(
        select(CollectionSong)
        .where(CollectionSong.collection_id == collection_id)
        .where(CollectionSong.song_id == song_id)
    )
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in collection")
        
    db.delete(item)
    db.commit()
    return {"ok": True}
