from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.services.instagram_service import get_latest_posts

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def index(request: Request):
    ig_posts = get_latest_posts(limit=9)
    return templates.TemplateResponse("index.html", {"request": request, "ig_posts": ig_posts})

@router.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})
