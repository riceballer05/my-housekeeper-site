import logging
import os
import httpx

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join("static", "ig_cache")
IG_PROFILE_URL = "https://www.instagram.com/shunou_bikatsu/"


def _get_cached_posts(limit: int) -> list:
    """
    ローカルにキャッシュされた ig_cache フォルダの画像から投稿情報を生成する。
    Instagram APIへの接続を必要としないため、確実に動作する。
    """
    posts = []
    if not os.path.exists(CACHE_DIR):
        return posts

    cached_files = sorted(
        [f for f in os.listdir(CACHE_DIR) if f.endswith(".jpg")],
        key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)),
        reverse=True  # 新しいファイルを優先
    )

    for i, filename in enumerate(cached_files[:limit]):
        shortcode = os.path.splitext(filename)[0]
        posts.append({
            "id": shortcode,
            "image_url": f"/static/ig_cache/{filename}",
            "caption": "お片付け事例 — スッキリした空間へ。 #整理収納 #お片付け #札幌",
            "permalink": f"https://www.instagram.com/p/{shortcode}/",
        })
    return posts


def get_latest_posts(limit: int = 9) -> list:
    """
    キャッシュ優先でInstagram投稿リストを返す。
    1. ローカルキャッシュ(ig_cache)が存在する → キャッシュを即返却（API接続なし）
    2. キャッシュが空 → InstagramからInstaloaderで取得を試みる
    """
    # --- 優先1: キャッシュを確認 ---
    cached = _get_cached_posts(limit)
    if cached:
        logger.info(f"Returning {len(cached)} posts from local cache.")
        return cached

    # --- 優先2: Instaloaderを使ってAPIから取得を試みる ---
    username = "shunou_bikatsu"
    base_url = IG_PROFILE_URL
    posts = []

    try:
        import instaloader
        L = instaloader.Instaloader(
            download_pictures=False,
            download_video_thumbnails=False,
            download_videos=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True,
        )
        logger.info("No cache found. Fetching from Instagram...")
        profile = instaloader.Profile.from_username(L.context, username)
        os.makedirs(CACHE_DIR, exist_ok=True)

        count = 0
        for post in profile.get_posts():
            if count >= limit:
                break

            image_filename = f"{post.shortcode}.jpg"
            image_path = os.path.join(CACHE_DIR, image_filename)
            local_url = f"/static/ig_cache/{image_filename}"

            if not os.path.exists(image_path):
                try:
                    target_url = getattr(post, "display_url", getattr(post, "url", ""))
                    r = httpx.get(target_url, timeout=10.0)
                    if r.status_code == 200:
                        with open(image_path, "wb") as f:
                            f.write(r.content)
                    else:
                        local_url = target_url
                except Exception as dl_err:
                    logger.warning(f"Could not download image {post.shortcode}: {dl_err}")
                    local_url = getattr(post, "display_url", getattr(post, "url", ""))

            posts.append({
                "id": post.shortcode,
                "image_url": local_url,
                "caption": post.caption if post.caption else "お片付け事例。スッキリとした空間へ。",
                "permalink": f"https://www.instagram.com/p/{post.shortcode}/",
            })
            count += 1

    except Exception as e:
        logger.error(f"Instagram fetch failed: {e}")
        # フォールバック: ダミー画像
        for i in range(1, limit + 1):
            posts.append({
                "id": f"fallback_{i}",
                "image_url": f"https://picsum.photos/seed/clean{i}/600/600",
                "caption": "Instagram事例はこちらからご覧いただけます。",
                "permalink": base_url,
            })

    return posts
