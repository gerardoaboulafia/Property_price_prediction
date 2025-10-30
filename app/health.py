from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class PipelineStatus(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    pipeline_components: List[str]

# Nota: el modelo se importa dinámicamente desde main.py
@router.get("/health", response_model=PipelineStatus)
async def health_check():
    """Health check endpoint"""
    from app.main import model  # import dinámico para acceder al modelo

    return PipelineStatus(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        pipeline_components=[
            "filter_by_currency_place",
            "extract_features_regex",
            "validate_geo",
            "calculate_subte_distance",
            "clean_data_outliers"
        ]
    )

#para que corra bien primero hay que activar la api y depsues pegar en el buscador
#http://127.0.0.1:8000/health
