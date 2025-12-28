from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime, timezone
from typing import List, Any, Dict
from app.models.version import Version, VersionCreate
from app.database import get_database
from app.services.agent import CanvasAgent

router = APIRouter(prefix="/chats", tags=["versions"])
agent = CanvasAgent()


def generate_components_for_prompt(prompt: str) -> List[Dict[str, Any]]:
    """
    Normalize agent output and always return a LIST of component dicts:
      - If agent returns {"components": {...}} -> return list(values)
      - If agent returns {"components": [...]} -> return the list
      - If agent returns { "comp-1": {...}, ... } -> return list(values)
      - If agent returns [...] -> return as-is
      - If agent returns (payload, meta) -> unwrap payload
    """
    raw = agent.generate_canvas(prompt, {})

    # Unwrap tuple returns like (payload, meta)
    payload = raw[0] if isinstance(raw, tuple) and len(raw) > 0 else raw

    # If payload is a dict with top-level "components"
    if isinstance(payload, dict) and "components" in payload:
        comps = payload["components"]
        if isinstance(comps, list):
            return comps
        if isinstance(comps, dict):
            return list(comps.values())

    # If payload itself is a dict of components (comp-1 -> {...})
    if isinstance(payload, dict):
        return list(payload.values())

    # If payload is already a list
    if isinstance(payload, list):
        return payload

    # Fallback: empty list
    return []


def serialize_version(doc: dict) -> Version:
    """
    Normalize DB doc to match Version model: ensure components is a list.
    """
    # mutate a shallow copy to avoid surprising callers
    d = dict(doc)

    if "_id" in d and isinstance(d["_id"], ObjectId):
        d["_id"] = str(d["_id"])
    if "chatId" in d and isinstance(d["chatId"], ObjectId):
        d["chatId"] = str(d["chatId"])

    comps = d.get("components")

    # If someone stored a dict (comp-1 -> {...}), convert to list
    if isinstance(comps, dict):
        # If the dict is a wrapper { "components": [...] }, handle it
        inner = comps.get("components") if isinstance(comps, dict) else None
        if isinstance(inner, list):
            d["components"] = inner
        else:
            d["components"] = list(comps.values())
    # If missing or some other type, ensure it's at least an empty list
    elif not isinstance(comps, list):
        d["components"] = []

    return Version(**d)


@router.post("/{chat_id}/versions", response_model=Version, status_code=status.HTTP_201_CREATED)
async def create_version(chat_id: str, data: VersionCreate):
    try:
        db = get_database()
        versions_collection = db["versions"]

        now = datetime.now(timezone.utc)

        # Normalize agent output to a list
        components = generate_components_for_prompt(data.prompt)

        version_doc: Dict[str, Any] = {
            "chatId": chat_id,
            "versionNumber": data.versionNumber,
            "prompt": data.prompt,
            "components": components,  # ALWAYS a LIST now
            "createdAt": now,
        }

        result = await versions_collection.insert_one(version_doc)
        created = await versions_collection.find_one({"_id": result.inserted_id})
        if not created:
            raise HTTPException(status_code=500, detail="Failed to fetch created version")
        return serialize_version(created)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{chat_id}/versions", response_model=List[Version])
async def get_versions(chat_id: str):
    try:
        db = get_database()
        versions_collection = db["versions"]
        docs = await versions_collection.find({"chatId": chat_id}).sort("versionNumber", -1).to_list(length=None)
        return [serialize_version(doc) for doc in docs]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{chat_id}/versions/latest", response_model=Version)
async def get_latest_version(chat_id: str):
    try:
        db = get_database()
        versions_collection = db["versions"]
        doc = await versions_collection.find_one({"chatId": chat_id}, sort=[("versionNumber", -1)])
        if not doc:
            raise HTTPException(status_code=404, detail="No versions found")
        return serialize_version(doc)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
