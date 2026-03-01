import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_thanks_email(name: str, email: str, menu: str):
    """
    サンクスメール自動配信のモック関数。
    実際にはSMTPサーバーやSendGridなどのAPIを利用して送信します。
    """
    subject = "【お片付け専門ハウスキーパー】お問い合わせありがとうございます"
    body = f"""
{name} 様

この度はお問い合わせいただき、誠にありがとうございます。
以下の内容で承りました。

■ご希望のメニュー: {menu}

内容を確認のうえ、担当者より通常2営業日以内にご連絡いたします。
引き続きよろしくお願いいたします。
"""
    logger.info("========== EMAIL MOCK START ==========")
    logger.info(f"To: {email}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Body: {body.strip()}")
    logger.info("========== EMAIL MOCK END ==========")
    return True
