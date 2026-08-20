import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ==========================================
# 1. كود FRONTEND (HTML + CSS + JS) المدمج
# ==========================================
HTML_CODE = """
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AETECHUP - TikTok Video Downloader</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #f8f9fa; --bg-surface: #ffffff;
            --bg-hero: linear-gradient(135deg, #7000ff 0%, #a100ff 100%);
            --bg-card: #6d28d9; --text-primary: #1f2937; --text-secondary: #4b5563;
            --text-light: #ffffff; --border-color: #e5e7eb; --accent-purple: #7c3aed;
            --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        }
        [data-theme="dark"] {
            --bg-primary: #0f172a; --bg-surface: #1e293b;
            --bg-hero: linear-gradient(135deg, #4c1d95 0%, #5b21b6 100%);
            --bg-card: #3b0764; --text-primary: #f8fafc; --text-secondary: #cbd5e1;
            --border-color: #334155; --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; transition: 0.3s; }
        body { background-color: var(--bg-primary); color: var(--text-primary); direction: ltr; }
        [dir="rtl"] { direction: rtl; }
        header { background-color: var(--bg-surface); border-bottom: 1px solid var(--border-color); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
        .logo { display: flex; align-items: center; gap: 0.5rem; font-size: 1.5rem; font-weight: 800; color: var(--accent-purple); text-decoration: none; }
        .nav-controls { display: flex; align-items: center; gap: 1rem; }
        .lang-select, .theme-toggle { background-color: var(--bg-primary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; font-weight: 500; }
        .hero { background: var(--bg-hero); padding: 4rem 1rem; text-align: center; color: var(--text-light); }
        .hero h1 { font-size: 2.5rem; margin-bottom: 2rem; font-weight: 700; }
        .downloader-box { max-width: 800px; margin: 0 auto; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); padding: 8px; border-radius: 12px; display: flex; gap: 8px; }
        .input-wrapper { flex: 1; background: white; border-radius: 8px; display: flex; align-items: center; }
        .input-wrapper input { width: 100%; padding: 1rem; border: none; outline: none; border-radius: 8px; font-size: 1rem; color: #000; }
        .btn-paste { background: #f3f4f6; color: #374151; border: none; padding: 0.5rem 1rem; margin-right: 0.5rem; border-radius: 6px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 0.3rem; }
        .btn-download { background-color: #5b21b6; color: white; border: none; padding: 1rem 2rem; border-radius: 8px; font-size: 1rem; font-weight: 700; cursor: pointer; }
        .btn-download:hover { opacity: 0.9; }
        .download-result { max-width: 800px; margin: 1.5rem auto 0; background: var(--bg-surface); padding: 1.5rem; border-radius: 12px; display: none; color: var(--text-primary); box-shadow: var(--shadow); }
        .result-actions { display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap; }
        .btn-action { flex: 1; padding: 0.75rem 1rem; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; color: white; }
        .btn-nowatermark { background: #10b981; } .btn-watermark { background: #3b82f6; } .btn-mp3 { background: #f59e0b; }
        .loader { display: none; margin: 1.5rem auto 0; border: 4px solid rgba(255,255,255,0.3); border-top: 4px solid #ffffff; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .features { max-width: 1000px; margin: 4rem auto; padding: 0 1rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; text-align: center; }
        .feature-card { background: var(--bg-surface); padding: 2rem; border-radius: 12px; border: 1px solid var(--border-color); box-shadow: var(--shadow); }
        .feature-card i { font-size: 2.5rem; color: var(--accent-purple); margin-bottom: 1rem; }
        .feature-card h3 { margin-bottom: 0.5rem; font-size: 1.25rem; }
        .feature-card p { color: var(--text-secondary); font-size: 0.95rem; line-height: 1.5; }
        .how-to-section { max-width: 900px; margin: 4rem auto; padding: 0 1rem; }
        .how-to-box { background-color: var(--bg-card); color: var(--text-light); padding: 3rem 2rem; border-radius: 24px; }
        .how-to-box h2 { font-size: 1.75rem; margin-bottom: 2rem; text-align: center; }
        .step-item { margin-bottom: 1.5rem; display: flex; gap: 1rem; }
        .step-number { font-size: 2rem; font-weight: 800; opacity: 0.5; }
        .faq-section { max-width: 800px; margin: 4rem auto; padding: 0 1rem; }
        .faq-item { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; margin-bottom: 1rem; overflow: hidden; }
        .faq-question { width: 100%; padding: 1.25rem; text-align: left; background: none; border: none; color: var(--text-primary); font-size: 1rem; font-weight: 600; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
        [dir="rtl"] .faq-question { text-align: right; }
        .faq-answer { padding: 0 1.25rem 1.25rem 1.25rem; color: var(--text-secondary); display: none; line-height: 1.6; }
        footer { background-color: #0f172a; color: #94a3b8; padding: 3rem 1rem; text-align: center; margin-top: 4rem; }
        footer p { margin-top: 1rem; font-size: 0.85rem; }
        @media (max-width: 640px) { .downloader-box { flex-direction: column; } .btn-download { width: 100%; } .hero h1 { font-size: 1.75rem; } }
    </style>
</head>
<body>
    <header>
        <a href="#" class="logo"><i class="fa-solid fa-cloud-arrow-down"></i> aetechup</a>
        <div class="nav-controls">
            <button class="theme-toggle" id="themeToggleBtn"><i class="fa-solid fa-moon"></i></button>
            <select class="lang-select" id="langSelect">
                <option value="en">English</option>
                <option value="ar">العربية</option>
                <option value="fr">Français</option>
                <option value="ru">Русский</option>
            </select>
        </div>
    </header>

    <section class="hero">
        <h1 data-i18n="hero_title">TikTok Video Downloader</h1>
        <div class="downloader-box">
            <div class="input-wrapper">
                <input type="text" id="videoUrl" data-i18n-placeholder="input_placeholder" placeholder="Insert a link here">
                <button class="btn-paste" id="pasteBtn"><i class="fa-regular fa-clipboard"></i> <span data-i18n="btn_paste">Paste</span></button>
            </div>
            <button class="btn-download" id="downloadBtn" data-i18n="btn_download">Download</button>
        </div>

        <div class="loader" id="loader"></div>

        <div class="download-result" id="downloadResult">
            <h3 id="resTitle" data-i18n="result_ready">Your Video is Ready!</h3>
            <p id="videoTitleDisplay" style="margin-top: 8px; font-size: 0.95rem; font-weight: 500;"></p>
            <div class="result-actions">
                <a href="#" class="btn-action btn-nowatermark" id="btnNoWm" target="_blank" data-i18n="btn_no_wm">Without Watermark</a>
                <a href="#" class="btn-action btn-watermark" id="btnWm" target="_blank" data-i18n="btn_wm">With Watermark</a>
                <a href="#" class="btn-action btn-mp3" id="btnMp3" target="_blank" data-i18n="btn_mp3">Download MP3 Audio</a>
            </div>
        </div>
    </section>

    <section class="features">
        <div class="feature-card"><i class="fa-solid fa-infinity"></i><h3 data-i18n="feat_1_title">Unlimited Downloads</h3><p data-i18n="feat_1_desc">Save TikTok videos as much as you need without any limits or restrictions.</p></div>
        <div class="feature-card"><i class="fa-solid fa-ban"></i><h3 data-i18n="feat_2_title">No Watermark!</h3><p data-i18n="feat_2_desc">Download TikTok videos in high quality without the official watermark logo.</p></div>
        <div class="feature-card"><i class="fa-solid fa-music"></i><h3 data-i18n="feat_3_title">MP4 and MP3</h3><p data-i18n="feat_3_desc">Convert and save files in HD quality MP4 video or MP3 audio format.</p></div>
    </section>

    <section class="how-to-section">
        <div class="how-to-box">
            <h2 data-i18n="howto_title">How to download TikTok without watermark?</h2>
            <div class="step-item"><div class="step-number">1</div><div><h3 data-i18n="step_1_title">Find a Video</h3><p data-i18n="step_1_desc">Open the TikTok app, scroll to find the video you'd like to save, and copy its share link.</p></div></div>
            <div class="step-item"><div class="step-number">2</div><div><h3 data-i18n="step_2_title">Paste the Link</h3><p data-i18n="step_2_desc">Paste the copied URL link into the input field above and click the Download button.</p></div></div>
            <div class="step-item"><div class="step-number">3</div><div><h3 data-i18n="step_3_title">Save TikTok</h3><p data-i18n="step_3_desc">Choose your preferred format (Without Watermark, Watermark, or MP3) to start downloading.</p></div></div>
        </div>
    </section>

    <section class="faq-section">
        <div class="faq-item"><button class="faq-question"><span data-i18n="faq_1_q">Do I have to pay to download TikTok videos?</span><i class="fa-solid fa-chevron-down"></i></button><div class="faq-answer" data-i18n="faq_1_a">No, our service is completely free and unlimited for all users worldwide.</div></div>
        <div class="faq-item"><button class="faq-question"><span data-i18n="faq_2_q">Do I need to install browser extensions?</span><i class="fa-solid fa-chevron-down"></i></button><div class="faq-answer" data-i18n="faq_2_a">No extensions or software installations are required. Everything works directly in your web browser.</div></div>
        <div class="faq-item"><button class="faq-question"><span data-i18n="faq_3_q">Where are videos saved after downloading?</span><i class="fa-solid fa-chevron-down"></i></button><div class="faq-answer" data-i18n="faq_3_a">Files are automatically saved in your device's default 'Downloads' folder.</div></div>
    </section>

    <footer>
        <p>aetechup &copy; 2018-2026. All rights reserved.</p>
        <p data-i18n="disclaimer">We are not affiliated with TikTok, ByteDance, or Douyin.</p>
    </footer>

    <script>
        const translations = {
            en: { hero_title: "TikTok Video Downloader", input_placeholder: "Insert a link here", btn_paste: "Paste", btn_download: "Download", result_ready: "Your Video is Ready!", btn_no_wm: "Without Watermark", btn_wm: "With Watermark", btn_mp3: "Download MP3 Audio", feat_1_title: "Unlimited Downloads", feat_1_desc: "Save TikTok videos as much as you need without any limits or restrictions.", feat_2_title: "No Watermark!", feat_2_desc: "Download TikTok videos in high quality without the official watermark logo.", feat_3_title: "MP4 and MP3", feat_3_desc: "Convert and save files in HD quality MP4 video or MP3 audio format.", howto_title: "How to download TikTok without watermark?", step_1_title: "Find a Video", step_1_desc: "Open the TikTok app, scroll to find the video you'd like to save, and copy its share link.", step_2_title: "Paste the Link", step_2_desc: "Paste the copied URL link into the input field above and click the Download button.", step_3_title: "Save TikTok", step_3_desc: "Choose your preferred format (Without Watermark, Watermark, or MP3) to start downloading.", faq_1_q: "Do I have to pay to download TikTok videos?", faq_1_a: "No, our service is completely free and unlimited for all users worldwide.", faq_2_q: "Do I need to install browser extensions?", faq_2_a: "No extensions or software installations are required. Everything works directly in your web browser.", faq_3_q: "Where are videos saved after downloading?", faq_3_a: "Files are automatically saved in your device's default 'Downloads' folder.", disclaimer: "We are not affiliated with TikTok, ByteDance, or Douyin." },
            ar: { hero_title: "أداة تحميل فيديوهات تيك توك", input_placeholder: "ضع رابط الفيديو هنا", btn_paste: "لصق", btn_download: "تحميل", result_ready: "الفيديو الخاص بك جاهز!", btn_no_wm: "بدون علامة مائية", btn_wm: "مع العلامة المائية", btn_mp3: "تحميل ملف صوتي MP3", feat_1_title: "تحميل غير محدود", feat_1_desc: "احفظ فيديوهات تيك توك بالقدر الذي تحتاجه دون أي حدود أو قيود.", feat_2_title: "بدون علامة مائية!", feat_2_desc: "قم بتنزيل فيديوهات تيك توك بجودة عالية وبدون شعار العلامة المائية.", feat_3_title: "صيغ MP4 و MP3", feat_3_desc: "قم بتحويل وحفظ الملفات بصيغة فيديو HD MP4 أو صوت MP3.", howto_title: "كيفية تنزيل تيك توك بدون علامة مائية؟", step_1_title: "اختر الفيديو", step_1_desc: "افتح تطبيق تيك توك، اختر الفيديو الذي تريد حفظه، وقم بنسخ رابط المشاركة.", step_2_title: "الصق الرابط", step_2_desc: "الصق رابط URL المنسوخ في حقل الإدخال أعلاه وانقر على زر التحميل.", step_3_title: "احفظ الفيديو", step_3_desc: "اختر الصيغة المفضلة لديك (بدون علامة مائية، بعلامة مائية، أو MP3) لبدء التنزيل.", faq_1_q: "هل يجب علي الدفع مقابل تنزيل فيديوهات تيك توك؟", faq_1_a: "لا، خدمتنا مجانية بالكامل وغير محدودة لجميع المستخدمين.", faq_2_q: "هل أحتاج إلى تثبيت إضافات على المتصفح؟", faq_2_a: "لا داعي لتثبيت أي برامج أو إضافات، الخدمة تعمل مباشرة عبر المتصفح.", faq_3_q: "أين يتم حفظ الفيديوهات بعد التنزيل؟", faq_3_a: "يتم حفظ الملفات تلقائياً في مجلد 'التنزيلات' الافتراضي على جهازك.", disclaimer: "نحن لسنا التابعين لتطبيق تيك توك أو ByteDance أو Douyin." },
            fr: { hero_title: "Téléchargeur de vidéos TikTok", input_placeholder: "Collez un lien ici", btn_paste: "Coller", btn_download: "Télécharger", result_ready: "Votre vidéo est prête !", btn_no_wm: "Sans filigrane", btn_wm: "Avec filigrane", btn_mp3: "Télécharger MP3", feat_1_title: "Téléchargements illimités", feat_1_desc: "Enregistrez autant de vidéos TikTok que vous le souhaitez sans aucune limite.", feat_2_title: "Sans filigrane !", feat_2_desc: "Téléchargez des vidéos TikTok en haute qualité sans le filigrane officiel.", feat_3_title: "MP4 et MP3", feat_3_desc: "Convertissez et enregistrez des fichiers au format vidéo MP4 HD ou audio MP3.", howto_title: "Comment télécharger TikTok sans filigrane ?", step_1_title: "Trouver une vidéo", step_1_desc: "Ouvrez l'application TikTok, trouvez la vidéo et copiez son lien de partage.", step_2_title: "Coller le lien", step_2_desc: "Collez le lien dans le champ ci-dessus et cliquez sur Télécharger.", step_3_title: "Enregistrer TikTok", step_3_desc: "Choisissez votre format préféré pour démarrer le téléchargement.", faq_1_q: "Dois-je payer pour télécharger des vidéos ?", faq_1_a: "Non, notre service est entièrement gratuit et illimité.", faq_2_q: "Dois-je installer une extension ?", faq_2_a: "Aucune extension ou logiciel n'est requis. Tout fonctionne dans votre navigateur.", faq_3_q: "Où sont enregistrées les vidéos ?", faq_3_a: "Les fichiers sont automatiquement enregistrés dans le dossier 'Téléchargements' de votre appareil.", disclaimer: "Nous ne sommes pas affiliés à TikTok, ByteDance ou Douyin." },
            ru: { hero_title: "Загрузчик видео TikTok", input_placeholder: "Вставьте ссылку сюда", btn_paste: "Вставить", btn_download: "Скачать", result_ready: "Ваше видео готово!", btn_no_wm: "Без водяного знака", btn_wm: "С водяным знаком", btn_mp3: "Скачать MP3 аудио", feat_1_title: "Безлимитное скачивание", feat_1_desc: "Сохраняйте столько видео из TikTok, сколько вам нужно, без ограничений.", feat_2_title: "Без водяного знака!", feat_2_desc: "Скачивайте видео TikTok в высоком качестве без логотипа.", feat_3_title: "MP4 и MP3", feat_3_desc: "Конвертируйте и сохраняйте файлы в формате MP4 HD или MP3 аудио.", howto_title: "Как скачать TikTok без водяного знака?", step_1_title: "Найдите видео", step_1_desc: "Откройте TikTok, найдите нужное видео и скопируйте ссылку.", step_2_title: "Вставьте ссылку", step_2_desc: "Вставьте ссылку в поле выше и нажмите кнопку Скачать.", step_3_title: "Сохраните видео", step_3_desc: "Выберите нужный формат для начала скачивания.", faq_1_q: "Нужно ли платить за скачивание видео?", faq_1_a: "Нет, наш сервис абсолютно бесплатен и безлимитен.", faq_2_q: "Нужно ли устанавливать расширения?", faq_2_a: "Установка дополнительных программ не требуется.", faq_3_q: "Куда сохраняются видео после скачивания?", faq_3_a: "Файлы автоматически сохраняются в папку 'Загрузки'.", disclaimer: "Мы не связаны с TikTok, ByteDance или Douyin." }
        };

        // Theme Toggle
        document.getElementById('themeToggleBtn').addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            document.getElementById('themeToggleBtn').innerHTML = newTheme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
        });

        // Multi-Language Switcher
        document.getElementById('langSelect').addEventListener('change', (e) => {
            const lang = e.target.value;
            document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (translations[lang] && translations[lang][key]) el.textContent = translations[lang][key];
            });
            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                const key = el.getAttribute('data-i18n-placeholder');
                if (translations[lang] && translations[lang][key]) el.placeholder = translations[lang][key];
            });
        });

        // Paste Link Functionality
        document.getElementById('pasteBtn').addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                document.getElementById('videoUrl').value = text;
            } catch (err) { alert("Clipboard access permission required."); }
        });

        // Real API Fetch Functionality
        document.getElementById('downloadBtn').addEventListener('click', async () => {
            const input = document.getElementById('videoUrl').value.trim();
            if (!input) return alert("Please enter a TikTok URL!");

            const loader = document.getElementById('loader');
            const resultBox = document.getElementById('downloadResult');
            
            loader.style.display = 'block';
            resultBox.style.display = 'none';

            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: input })
                });

                const data = await response.json();
                loader.style.display = 'none';

                if (data.status === 'success') {
                    document.getElementById('videoTitleDisplay').innerText = data.title;
                    document.getElementById('btnNoWm').href = data.video_nowm;
                    document.getElementById('btnWm').href = data.video_wm;
                    document.getElementById('btnMp3').href = data.music;
                    resultBox.style.display = 'block';
                } else {
                    alert("Error: " + (data.message || "Failed to fetch video"));
                }
            } catch (err) {
                loader.style.display = 'none';
                alert("Server Error! Check connection.");
            }
        });

        // FAQ Accordions
        document.querySelectorAll('.faq-question').forEach(button => {
            button.addEventListener('click', () => {
                const answer = button.nextElementSibling;
                const icon = button.querySelector('i');
                const isOpen = answer.style.display === 'block';
                document.querySelectorAll('.faq-answer').forEach(a => a.style.display = 'none');
                document.querySelectorAll('.faq-question i').forEach(i => i.className = 'fa-solid fa-chevron-down');
                if (!isOpen) { answer.style.display = 'block'; icon.className = 'fa-solid fa-chevron-up'; }
            });
        });
    </script>
</body>
</html>
"""

# ==========================================
# 2. كود BACKEND (Flask API)
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/api/download', methods=['POST'])
def handle_download():
    try:
        data = request.get_json()
        target_url = data.get('url', '').strip()

        if not target_url:
            return jsonify({'status': 'error', 'message': 'URL is required'}), 400

        # الاتصال بـ API استخراج الفيديوهات المباشر
        api_endpoint = f"https://www.tikwm.com/api/?url={target_url}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        response = requests.get(api_endpoint, headers=headers, timeout=12)
        res_data = response.json()

        if res_data.get('code') == 0:
            v_data = res_data.get('data', {})
            return jsonify({
                'status': 'success',
                'title': v_data.get('title', 'TikTok Video'),
                'video_nowm': v_data.get('play'),
                'video_wm': v_data.get('wmplay'),
                'music': v_data.get('music')
            })
        else:
            return jsonify({'status': 'error', 'message': 'Invalid video URL or private content'}), 400

    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
