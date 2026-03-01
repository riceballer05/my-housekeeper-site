from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import io
from PIL import Image
from app.services.mail_service import send_thanks_email

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ContactResponse(BaseModel):
    success: bool
    message: str

@router.post("/contact", response_model=ContactResponse)
async def submit_contact(
    name: str = Form(...),
    email: str = Form(...),
    menu: str = Form(...),
    message: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None)
):
    try:
        print(f"Received contact from {name} ({email}) for {menu}")
        
        # 画像のリサイズ（Pillow）、保存処理
        if photo and photo.filename:
            print(f"Photo uploaded: {photo.filename}")
            content = await photo.read()
            image = Image.open(io.BytesIO(content))
            
            # RGBモードに変換（PNGのアルファチャンネル等の対策）
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
                
            # 最大1200x1200でリサイズ
            max_size = (1200, 1200)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # セキュアなファイル名の生成
            safe_filename = "".join(c for c in photo.filename.split('.')[0] if c.isalnum()) or "upload"
            webp_path = os.path.join(UPLOAD_DIR, f"{safe_filename}.webp")
            
            # WebPとして保存
            image.save(webp_path, "WEBP", quality=80)
            print(f"Saved optimized image to {webp_path}")

        # メール送信処理
        send_thanks_email(name=name, email=email, menu=menu)

        return {"success": True, "message": "お問い合わせを受け付けました。自動返信メールをご確認ください。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
