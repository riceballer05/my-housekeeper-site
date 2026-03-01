import logging
import instaloader
import os
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

# インスタンスをモジュールレベルで保持して再利用（必要に応じてログイン処理等を追加可能）
L = instaloader.Instaloader(
    download_pictures=False,
    download_video_thumbnails=False,
    download_videos=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False
)

def get_latest_posts(limit: int = 9):
    """
    Instaloaderを利用してInstagramの公開プロフィールから最新投稿を取得。
    """
    username = "shunou_bikatsu"
    base_url = f"https://www.instagram.com/{username}/"
    posts = []
    
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        
        count = 0
        cache_dir = os.path.join("static", "ig_cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        for post in profile.get_posts():
            if count >= limit:
                break
            
            # CDN制限回避のため画像をサーバーにキャッシュして配信する
            image_filename = f"{post.shortcode}.jpg"
            image_path = os.path.join(cache_dir, image_filename)
            local_url = f"/static/ig_cache/{image_filename}"
            
            if not os.path.exists(image_path):
                # ダウンロードを試行
                try:
                    target_url = getattr(post, 'display_url', getattr(post, 'url', ''))
                    r = httpx.get(target_url, timeout=10.0)
                    if r.status_code == 200:
                        with open(image_path, "wb") as f:
                            f.write(r.content)
                    else:
                        local_url = target_url # Fallback to original url
                except Exception as e:
                    logger.warning(f"Could not download image {post.shortcode}: {e}")
                    local_url = getattr(post, 'display_url', getattr(post, 'url', ''))
                
            posts.append({
                "id": post.shortcode,
                "image_url": local_url,
                "caption": post.caption if post.caption else "お片付け事例。スッキリとした空間へ。",
                "permalink": f"https://www.instagram.com/p/{post.shortcode}/"
            })
            count += 1
            
        if not posts:
            logger.warning("No posts found for user.")
            
    except Exception as e:
        logger.error(f"Error fetching Instagram posts with instaloader: {e}")
        # フォールバック処理
        for i in range(1, limit + 1):
            posts.append({
                "id": f"mock_error_{i}",
                "image_url": f"https://picsum.photos/seed/error{i}/600/600",
                "caption": f"現在読み込み中... ({i})",
                "permalink": base_url
            })
            
    return posts
