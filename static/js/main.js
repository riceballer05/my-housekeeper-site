document.addEventListener('DOMContentLoaded', () => {
    // 1. スムーススクロール (Header navigation links)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            const target = document.querySelector(targetId);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // 2. フォームの非同期(AJAX)送信
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const submitText = submitBtn.querySelector('.btn-text');
            const loader = submitBtn.querySelector('.loader');
            const formMessage = document.getElementById('formMessage');

            // 送信中のUI変化
            submitBtn.disabled = true;
            submitText.textContent = '送信中...';
            if (loader) loader.classList.remove('hidden');
            formMessage.classList.add('hidden');

            const formData = new FormData(contactForm);

            try {
                const response = await fetch('/api/contact', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();

                if (response.ok && result.success) {
                    formMessage.textContent = '送信が完了しました。自動返信メールをご確認ください。';
                    formMessage.className = 'form-message success';
                    formMessage.classList.remove('hidden');
                    contactForm.reset();
                    // ファイルプレビューのリセット
                    const filePreview = document.getElementById('filePreview');
                    if (filePreview) filePreview.textContent = '写真を選択、またはドラッグ＆ドロップ';
                } else {
                    throw new Error(result.detail || '送信に失敗しました。');
                }
            } catch (error) {
                formMessage.textContent = error.message;
                formMessage.className = 'form-message error';
                formMessage.classList.remove('hidden');
            } finally {
                // UIリセット
                submitBtn.disabled = false;
                submitText.textContent = '送信する';
                if (loader) loader.classList.add('hidden');
            }
        });

        // 3. ファイルアップロードのプレビュー表示
        const photoInput = document.getElementById('photo');
        const filePreview = document.getElementById('filePreview');
        if (photoInput && filePreview) {
            photoInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    filePreview.textContent = `選択済: ${file.name}`;
                } else {
                    filePreview.textContent = '写真を選択、またはドラッグ＆ドロップ';
                }
            });
        }
    }
});
