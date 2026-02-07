from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from lattice_lock.config.feature_flags import Feature, is_feature_enabled, override_feature

router = APIRouter(prefix="", tags=["Admin UI"])

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


class ToggleRequest(BaseModel):
    enabled: bool


@router.get("/admin/flags", response_class=HTMLResponse)
async def flags_ui(request: Request):
    """Serve the feature flags UI."""
    return templates.TemplateResponse("flags.html", {"request": request})


@router.get("/api/v1/flags")
async def list_flags():
    """List all feature flags and their status."""
    features = []
    for f in Feature:
        features.append({"name": f.value, "enabled": is_feature_enabled(f)})
    return {"features": features}


@router.post("/api/v1/flags/{feature}/toggle")
async def toggle_flag(feature: str, request: ToggleRequest):
    """Toggle a feature flag."""
    # Find matching enum
    target_feature = None
    for f in Feature:
        if f.value == feature:
            target_feature = f
            break

    if not target_feature:
        raise HTTPException(status_code=404, detail=f"Feature '{feature}' not found")

    override_feature(target_feature, request.enabled)

    return {
        "name": feature,
        "enabled": is_feature_enabled(target_feature),
        "message": f"Feature '{feature}' set to {request.enabled}",
    }
