import os
import glob
from flask import Flask, render_template_string, request, session, redirect, url_for, send_file
import yt_dlp

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ==========================================
# 🌐 قاموس الترجمات الشامل (7 لغات عالمية)
# ==========================================
TRANSLATIONS = {
    'en': {
        'lang_name': 'English', 'title': 'AekDownloader | TikTok Downloader',
        'nav_home': 'Home', 'nav_contact': 'Contact Us', 'nav_privacy': 'Privacy Policy', 'nav_terms': 'Terms of Use',
        'hero_title': 'Universal Media Downloader', 'hero_desc': 'Download TikTok videos, stories, and audio quickly and safely.',
        'placeholder': 'Paste your link here...', 'paste': 'Paste 📋', 'download': 'Download',
        'opt_video': 'Video (MP4)', 'opt_audio': 'Audio (MP3)', 'opt_story': 'Story', 'opt_photo': 'Photos',
        'feat_title': 'Why Choose Us?',
        'f1_title': 'No Watermark', 'f1_desc': 'Download videos in crystal clear HD without any logos.',
        'f2_title': 'Unlimited & Free', 'f2_desc': 'Save as many videos as you want without any restrictions.',
        'f3_title': 'Multiple Formats', 'f3_desc': 'Extract high-quality MP3 audio or download image slideshows.',
        'how_title': 'How to download?',
        'step1_t': '1. Copy the Link', 'step1_d': 'Open the app, find the video, tap Share, and select "Copy Link".',
        'step2_t': '2. Paste it here', 'step2_d': 'Come back to this page, paste the link in the input field above.',
        'step3_t': '3. Download', 'step3_d': 'Choose your format and click Download to save it.',
        'faq_title': 'FAQ',
        'q1': 'Are the downloaded files safe?', 'a1': 'Absolutely. All files are processed securely from official servers.',
        'q2': 'Where are files saved?', 'a2': 'They are saved in your device\'s "Downloads" folder.',
        'q3': 'Can I download private videos?', 'a3': 'No, we can only process publicly available videos.',
        'footer_text': '© 2026 AekDownloader. All rights reserved.'
    },
    'ar': {
        'lang_name': 'العربية', 'title': 'AekDownloader | تحميل تيك توك',
        'nav_home': 'الرئيسية', 'nav_contact': 'اتصل بنا', 'nav_privacy': 'الخصوصية', 'nav_terms': 'شروط الاستخدام',
        'hero_title': 'أداة التحميل الشاملة', 'hero_desc': 'قم بتحميل الفيديوهات، الستوريات، والصوتيات بأمان وسرعة.',
        'placeholder': 'ألصق الرابط هنا...', 'paste': 'لصق 📋', 'download': 'تحميل',
        'opt_video': 'فيديو (MP4)', 'opt_audio': 'صوت (MP3)', 'opt_story': 'ستوري', 'opt_photo': 'صور',
        'feat_title': 'لماذا تختارنا؟',
        'f1_title': 'بدون علامة مائية', 'f1_desc': 'احصل على الفيديوهات بجودة HD الأصلية خالية من الشعار.',
        'f2_title': 'مجاني وغير محدود', 'f2_desc': 'حمل ما تشاء مجاناً بدون قيود يومية.',
        'f3_title': 'صيغ متعددة', 'f3_desc': 'استخرج الصوتيات أو حمل الصور كفيديو مدمج.',
        'how_title': 'كيفية التحميل؟',
        'step1_t': '1. انسخ الرابط', 'step1_d': 'افتح التطبيق، اضغط مشاركة ثم "نسخ الرابط".',
        'step2_t': '2. ألصق الرابط', 'step2_d': 'عد لموقعنا وألصق الرابط في المربع بالأعلى.',
        'step3_t': '3. اضغط تحميل', 'step3_d': 'اختر الصيغة المناسبة واضغط تحميل.',
        'faq_title': 'الأسئلة الشائعة',
        'q1': 'هل الملفات آمنة؟', 'a1': 'نعم، يتم جلبها مباشرة من السيرفرات الرسمية بأمان تام.',
        'q2': 'أين أجد الفيديوهات؟', 'a2': 'في مجلد "التنزيلات" أو الاستوديو بهاتفك.',
        'q3': 'هل يمكن تحميل مقطع خاص؟', 'a3': 'لا، ندعم فقط الحسابات العامة.',
        'footer_text': '© 2026 AekDownloader. جميع الحقوق محفوظة.'
    },
    'fr': {
        'lang_name': 'Français', 'title': 'AekDownloader | Téléchargeur',
        'nav_home': 'Accueil', 'nav_contact': 'Contact', 'nav_privacy': 'Confidentialité', 'nav_terms': 'Conditions',
        'hero_title': 'Téléchargeur Universel', 'hero_desc': 'Téléchargez vidéos, stories et audios rapidement.',
        'placeholder': 'Collez le lien ici...', 'paste': 'Coller 📋', 'download': 'Télécharger',
        'opt_video': 'Vidéo (MP4)', 'opt_audio': 'Audio (MP3)', 'opt_story': 'Story', 'opt_photo': 'Photos',
        'feat_title': 'Pourquoi nous choisir?',
        'f1_title': 'Sans Filigrane', 'f1_desc': 'Vidéos HD sans logo.',
        'f2_title': 'Illimité & Gratuit', 'f2_desc': 'Téléchargez sans restriction.',
        'f3_title': 'Formats Multiples', 'f3_desc': 'Extraire MP3 ou télécharger des photos.',
        'how_title': 'Comment télécharger?',
        'step1_t': '1. Copier le lien', 'step1_d': 'Trouvez la vidéo, cliquez sur Partager et copier le lien.',
        'step2_t': '2. Coller ici', 'step2_d': 'Collez le lien dans le champ ci-dessus.',
        'step3_t': '3. Télécharger', 'step3_d': 'Choisissez le format et cliquez sur Télécharger.',
        'faq_title': 'FAQ',
        'q1': 'Est-ce sûr?', 'a1': 'Oui, 100% sûr et sans logiciel tiers.',
        'q2': 'Où sont les fichiers?', 'a2': 'Dans votre dossier Téléchargements.',
        'q3': 'Vidéos privées?', 'a3': 'Non, uniquement les vidéos publiques.',
        'footer_text': '© 2026 AekDownloader. Tous droits réservés.'
    },
    'es': {
        'lang_name': 'Español', 'title': 'AekDownloader | Descargador',
        'nav_home': 'Inicio', 'nav_contact': 'Contacto', 'nav_privacy': 'Privacidad', 'nav_terms': 'Términos',
        'hero_title': 'Descargador Universal', 'hero_desc': 'Descarga videos, historias y audio rápido y seguro.',
        'placeholder': 'Pega tu enlace aquí...', 'paste': 'Pegar 📋', 'download': 'Descargar',
        'opt_video': 'Video (MP4)', 'opt_audio': 'Audio (MP3)', 'opt_story': 'Historia', 'opt_photo': 'Fotos',
        'feat_title': '¿Por qué elegirnos?',
        'f1_title': 'Sin Marca de Agua', 'f1_desc': 'Videos HD sin logos.',
        'f2_title': 'Ilimitado y Gratis', 'f2_desc': 'Descarga sin restricciones.',
        'f3_title': 'Múltiples Formatos', 'f3_desc': 'Extrae MP3 o descarga fotos.',
        'how_title': '¿Cómo descargar?',
        'step1_t': '1. Copiar Enlace', 'step1_d': 'Busca el video, toca compartir y copiar enlace.',
        'step2_t': '2. Pegar Aquí', 'step2_d': 'Pega el enlace en la caja de arriba.',
        'step3_t': '3. Descargar', 'step3_d': 'Elige tu formato y descarga.',
        'faq_title': 'Preguntas Frecuentes',
        'q1': '¿Es seguro?', 'a1': 'Sí, 100% seguro desde servidores oficiales.',
        'q2': '¿Dónde se guardan?', 'a2': 'En tu carpeta de Descargas.',
        'q3': '¿Videos privados?', 'a3': 'No, solo contenido público.',
        'footer_text': '© 2026 AekDownloader. Todos los derechos reservados.'
    },
    'ru': {
        'lang_name': 'Русский', 'title': 'AekDownloader | Скачать',
        'nav_home': 'Главная', 'nav_contact': 'Контакты', 'nav_privacy': 'Конфиденциальность', 'nav_terms': 'Условия',
        'hero_title': 'Универсальный Загрузчик', 'hero_desc': 'Скачивайте видео, истории и аудио быстро и безопасно.',
        'placeholder': 'Вставьте ссылку здесь...', 'paste': 'Вставить 📋', 'download': 'Скачать',
        'opt_video': 'Видео (MP4)', 'opt_audio': 'Аудио (MP3)', 'opt_story': 'История', 'opt_photo': 'Фото',
        'feat_title': 'Почему мы?',
        'f1_title': 'Без водяных знаков', 'f1_desc': 'HD видео без логотипов.',
        'f2_title': 'Безлимитно и Бесплатно', 'f2_desc': 'Скачивайте без ограничений.',
        'f3_title': 'Разные форматы', 'f3_desc': 'Извлекайте MP3 или фото.',
        'how_title': 'Как скачать?',
        'step1_t': '1. Скопировать', 'step1_d': 'Найдите видео, нажмите поделиться и скопировать ссылку.',
        'step2_t': '2. Вставить', 'step2_d': 'Вставьте ссылку в поле выше.',
        'step3_t': '3. Скачать', 'step3_d': 'Выберите формат и нажмите скачать.',
        'faq_title': 'Частые Вопросы',
        'q1': 'Это безопасно?', 'a1': 'Да, 100% безопасно.',
        'q2': 'Где файлы?', 'a2': 'В папке Загрузки.',
        'q3': 'Приватные видео?', 'a3': 'Нет, только публичные.',
        'footer_text': '© 2026 AekDownloader. Все права защищены.'
    },
    'zh': {
        'lang_name': '中文', 'title': 'AekDownloader | 下载器',
        'nav_home': '首页', 'nav_contact': '联系我们', 'nav_privacy': '隐私政策', 'nav_terms': '使用条款',
        'hero_title': '通用媒体下载器', 'hero_desc': '快速安全地下载视频、故事和音频。',
        'placeholder': '在此粘贴链接...', 'paste': '粘贴 📋', 'download': '下载',
        'opt_video': '视频 (MP4)', 'opt_audio': '音频 (MP3)', 'opt_story': '故事', 'opt_photo': '照片',
        'feat_title': '为什么选择我们？',
        'f1_title': '无水印', 'f1_desc': '下载无标志的高清视频。',
        'f2_title': '免费无限', 'f2_desc': '无限制地下载。',
        'f3_title': '多种格式', 'f3_desc': '提取 MP3 或下载照片。',
        'how_title': '如何下载？',
        'step1_t': '1. 复制链接', 'step1_d': '找到视频，点击分享并复制链接。',
        'step2_t': '2. 粘贴至此', 'step2_d': '在上方框内粘贴链接。',
        'step3_t': '3. 下载', 'step3_d': '选择格式并点击下载。',
        'faq_title': '常见问题',
        'q1': '安全吗？', 'a1': '是的，100% 安全。',
        'q2': '文件在哪？', 'a2': '在您的下载文件夹中。',
        'q3': '私人视频？', 'a3': '不支持，仅限公开视频。',
        'footer_text': '© 2026 AekDownloader. 保留所有权利。'
    },
    'ja': {
        'lang_name': '日本語', 'title': 'AekDownloader | ダウンローダー',
        'nav_home': 'ホーム', 'nav_contact': 'お問い合わせ', 'nav_privacy': 'プライバシー', 'nav_terms': '利用規約',
        'hero_title': 'ユニバーサルダウンローダー', 'hero_desc': '動画、ストーリー、音声を安全かつ迅速にダウンロード。',
        'placeholder': 'ここにリンクを貼り付け...', 'paste': '貼り付け 📋', 'download': 'ダウンロード',
        'opt_video': '動画 (MP4)', 'opt_audio': '音声 (MP3)', 'opt_story': 'ストーリー', 'opt_photo': '写真',
        'feat_title': '選ばれる理由',
        'f1_title': '透かしなし', 'f1_desc': 'ロゴなしのHD動画。',
        'f2_title': '無制限＆無料', 'f2_desc': '制限なしでダウンロード。',
        'f3_title': '複数フォーマット', 'f3_desc': 'MP3抽出や写真ダウンロード。',
        'how_title': 'ダウンロード方法',
        'step1_t': '1. リンクをコピー', 'step1_d': '動画を見つけ、共有からリンクをコピーします。',
        'step2_t': '2. ここに貼り付け', 'step2_d': '上のフィールドにリンクを貼り付けます。',
        'step3_t': '3. ダウンロード', 'step3_d': 'フォーマットを選んでダウンロード。',
        'faq_title': 'よくある質問',
        'q1': '安全ですか？', 'a1': 'はい、100%安全です。',
        'q2': 'ファイルはどこ？', 'a2': 'ダウンロードフォルダに保存されます。',
        'q3': '非公開動画は？', 'a3': 'いいえ、公開動画のみです。',
        'footer_text': '© 2026 AekDownloader. 無断複写・転載を禁じます。'
    }
}

def get_t():
    lang = session.get('lang', 'en') # الإنجليزية هي الأساسية
    if lang not in TRANSLATIONS:
        lang = 'en'
    return TRANSLATIONS[lang], lang

# ==========================================
# 🎨 القالب الأساسي (يحتوي على الأنيميشن والوضع الليلي)
# ==========================================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ 'rtl' if lang == 'ar' else 'ltr' }}" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t['title'] }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800;900&display=swap" rel="stylesheet">
    <style>
        /* المتغيرات للأوضاع (ليلي/نهاري) */
        :root {
            --primary: #2563eb;
            --primary-hover: #1e40af;
            --bg: #f0f8ff;
            --text: #0f172a;
            --box-bg: rgba(255, 255, 255, 0.85); /* شفافية لظهور الأنيميشن */
            --border: rgba(226, 232, 240, 0.8);
            --footer-bg: rgba(15, 23, 42, 0.95);
            --footer-text: #cbd5e1;
        }
        [data-theme="dark"] {
            --primary: #38bdf8;
            --primary-hover: #0ea5e9;
            --bg: #090b14;
            --text: #f8fafc;
            --box-bg: rgba(30, 41, 59, 0.75); /* شفافية زجاجية داكنة */
            --border: rgba(51, 65, 85, 0.8);
            --footer-bg: rgba(2, 6, 23, 0.95);
            --footer-text: #94a3b8;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; transition: background-color 0.4s, color 0.4s; }
        body { background: var(--bg); color: var(--text); display: flex; flex-direction: column; min-height: 100vh; overflow-x: hidden; position: relative; }
        
        /* 🌌 خلفيات العوالم المتحركة (CSS Animations) */
        #animated-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; overflow: hidden; pointer-events: none; }
        .world-element { position: absolute; border-radius: 50%; animation: floatWorld linear infinite; }
        @keyframes floatWorld {
            0% { transform: translateY(110vh) translateX(0) rotate(0deg); opacity: 0; }
            20% { opacity: 0.6; }
            80% { opacity: 0.6; }
            100% { transform: translateY(-10vh) translateX(100px) rotate(360deg); opacity: 0; }
        }

        /* Navbar */
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 15px 5%; background: var(--box-bg); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); position: relative; z-index: 10; }
        .logo { font-size: 24px; font-weight: 900; color: var(--text); text-decoration: none; }
        .logo span { color: var(--primary); }
        .nav-controls { display: flex; gap: 15px; align-items: center; }
        
        /* زر الوضع الليلي والنهاري */
        .theme-toggle { background: transparent; border: 2px solid var(--primary); color: var(--text); padding: 5px 12px; border-radius: 20px; cursor: pointer; font-weight: bold; font-size: 14px; }
        
        /* Language Dropdown */
        .lang-menu { position: relative; display: inline-block; }
        .lang-btn { background: var(--box-bg); border: 1px solid var(--border); padding: 8px 15px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; color: var(--text); }
        .lang-dropdown { display: none; position: absolute; top: 110%; right: 0; background: var(--box-bg); backdrop-filter: blur(15px); min-width: 140px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
        [dir="rtl"] .lang-dropdown { right: auto; left: 0; }
        .lang-menu:hover .lang-dropdown { display: block; }
        .lang-dropdown a { display: block; padding: 10px 15px; color: var(--text); text-decoration: none; border-bottom: 1px solid var(--border); font-weight: 600; }
        .lang-dropdown a:hover { background: var(--primary); color: #fff; }

        .main-content { flex: 1; display: flex; flex-direction: column; align-items: center; z-index: 2; position: relative; }
        .alert-error { background: rgba(220, 38, 38, 0.8); color: #fff; padding: 15px; text-align: center; font-weight: bold; width: 100%; backdrop-filter: blur(5px); }
        
        footer { background: var(--footer-bg); color: var(--footer-text); text-align: center; padding: 40px 20px; margin-top: auto; z-index: 2; position: relative; }
        footer a { color: var(--footer-text); text-decoration: none; margin: 0 15px; font-weight: 600; }
        footer a:hover { color: #fff; }

        @media (max-width: 768px) {
            .lang-btn span { display: none; }
        }
    </style>
</head>
<body>
    <!-- خلفية الأنيميشن -->
    <div id="animated-bg"></div>

    <nav class="navbar">
        <a href="/" class="logo">Aek<span>Downloader</span></a>
        
        <div class="nav-controls">
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌙</button>
            <div class="lang-menu">
                <button class="lang-btn">🌐 <span>{{ t['lang_name'] }}</span></button>
                <div class="lang-dropdown">
                    <a href="/set_lang/en">🇬🇧 English</a>
                    <a href="/set_lang/ar">🇸🇦 العربية</a>
                    <a href="/set_lang/fr">🇫🇷 Français</a>
                    <a href="/set_lang/es">🇪🇸 Español</a>
                    <a href="/set_lang/ru">🇷🇺 Русский</a>
                    <a href="/set_lang/zh">🇨🇳 中文</a>
                    <a href="/set_lang/ja">🇯🇵 日本語</a>
                </div>
            </div>
        </div>
    </nav>

    {% if error %}
    <div class="alert-error">⚠️ {{ error }}</div>
    {% endif %}

    <main class="main-content">
        {{ content|safe }}
    </main>

    <footer>
        <p>{{ t['footer_text'] }}</p>
    </footer>

    <script>
        // سكربت الوضع الليلي/النهاري والأنيميشن الخاص بكل وضع
        const html = document.documentElement;
        const themeBtn = document.getElementById('themeBtn');
        const animBg = document.getElementById('animated-bg');
        
        const currentTheme = localStorage.getItem('theme') || 'light';
        setTheme(currentTheme);

        function toggleTheme() {
            const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        }

        function setTheme(theme) {
            html.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            themeBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
            generateWorlds(theme);
        }

        // توليد العوالم المتحركة برمجياً (غيوم لـ النهاري / نجوم لـ الليلي)
        function generateWorlds(theme) {
            animBg.innerHTML = ''; // مسح القديم
            const count = 15;
            for(let i=0; i<count; i++) {
                let el = document.createElement('div');
                el.className = 'world-element';
                
                // أحجام وأماكن عشوائية
                let size = Math.random() * 80 + 20; 
                let left = Math.random() * 100;
                let duration = Math.random() * 10 + 10;
                let delay = Math.random() * 10;
                
                el.style.width = size + 'px';
                el.style.height = size + 'px';
                el.style.left = left + 'vw';
                el.style.animationDuration = duration + 's';
                el.style.animationDelay = delay + 's';
                
                // تغيير الألوان حسب الوضع
                if(theme === 'dark') {
                    el.style.background = 'radial-gradient(circle, rgba(56,189,248,0.8) 0%, rgba(0,0,0,0) 70%)';
                    el.style.boxShadow = '0 0 20px rgba(56,189,248,0.5)';
                } else {
                    el.style.background = 'rgba(255, 255, 255, 0.7)';
                    el.style.boxShadow = '0 10px 30px rgba(0,0,0,0.05)';
                }
                
                animBg.appendChild(el);
            }
        }

        // سكربتات التحميل واللصق
        async function pasteText() {
            try {
                const text = await navigator.clipboard.readText();
                document.getElementById('linkInput').value = text;
            } catch (err) {
                alert('يرجى اللصق يدوياً.');
            }
        }
        function startDownload() {
            const btn = document.getElementById('dlBtn');
            btn.innerHTML = '... ⏳';
            btn.style.opacity = '0.7';
            btn.style.pointerEvents = 'none';
            setTimeout(() => {
                btn.innerHTML = '{{ t["download"] }}';
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
                document.getElementById('linkInput').value = '';
            }, 8000);
        }
    </script>
</body>
</html>
"""

# ==========================================
# 📄 محتوى الصفحة الرئيسية (UI زجاجي فخم)
# ==========================================
HOME_HTML = """
<style>
    .hero { text-align: center; padding: 60px 20px 40px; width: 100%; }
    .hero h1 { font-size: 38px; font-weight: 900; margin-bottom: 15px; text-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .hero p { opacity: 0.8; font-size: 18px; margin-bottom: 40px; }
    
    .search-container { max-width: 700px; margin: 0 auto; background: var(--box-bg); padding: 10px; border-radius: 16px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); border: 1px solid var(--border); backdrop-filter: blur(15px); display: flex; gap: 8px; flex-wrap: wrap; }
    .search-container input { flex: 1; min-width: 250px; border: none; padding: 15px 20px; font-size: 16px; outline: none; background: transparent; color: var(--text); }
    .btn-paste { background: transparent; color: var(--text); border: 1px solid var(--border); padding: 0 15px; border-radius: 10px; font-weight: bold; cursor: pointer; }
    .btn-dl { background: var(--primary); color: #fff; border: none; padding: 15px 30px; font-size: 16px; font-weight: bold; border-radius: 10px; cursor: pointer; transition: 0.3s; }
    .btn-dl:hover { background: var(--primary-hover); transform: scale(1.05); }

    .options-row { display: flex; justify-content: center; gap: 15px; margin-top: 25px; flex-wrap: wrap; }
    .opt-radio { display: flex; align-items: center; gap: 5px; cursor: pointer; font-weight: 600; padding: 8px 15px; border-radius: 20px; background: var(--box-bg); border: 1px solid var(--border); backdrop-filter: blur(10px); }
    .opt-radio input { accent-color: var(--primary); }

    .section-wrap { width: 100%; padding: 60px 20px; display: flex; flex-direction: column; align-items: center; }
    .sec-title { font-size: 32px; margin-bottom: 40px; font-weight: 800; text-align: center; }

    .features-grid { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; max-width: 1000px; }
    .f-card { background: var(--box-bg); backdrop-filter: blur(10px); padding: 30px; border-radius: 16px; width: 300px; text-align: center; border: 1px solid var(--border); }
    .f-card h3 { color: var(--primary); margin-bottom: 15px; font-size: 20px; }
    .f-card p { opacity: 0.8; font-size: 15px; line-height: 1.6; }

    .how-box { background: rgba(30, 58, 138, 0.8); backdrop-filter: blur(15px); color: #fff; padding: 40px; border-radius: 24px; max-width: 800px; width: 100%; border: 1px solid rgba(255,255,255,0.1); }
    .step { position: relative; padding: 0 40px; margin-bottom: 30px; }
    [dir="ltr"] .step { padding: 0 0 0 40px; }
    .step::before { content: "✓"; position: absolute; right: 0; top: 0; color: #38bdf8; font-size: 24px; font-weight: bold; }
    [dir="ltr"] .step::before { right: auto; left: 0; }
    .step h4 { font-size: 18px; margin-bottom: 5px; }
    .step p { opacity: 0.8; font-size: 15px; }

    .faq-container { max-width: 800px; width: 100%; }
    details { background: var(--box-bg); backdrop-filter: blur(10px); margin-bottom: 15px; border-radius: 12px; border: 1px solid var(--border); overflow: hidden; }
    summary { padding: 20px; font-weight: 700; cursor: pointer; font-size: 16px; list-style: none; display: flex; justify-content: space-between; align-items: center; }
    summary::-webkit-details-marker { display: none; }
    summary::after { content: "+"; color: var(--primary); font-size: 20px; }
    details[open] summary::after { content: "-"; }
    details p { padding: 0 20px 20px 20px; opacity: 0.8; line-height: 1.7; font-size: 15px; }
</style>

<div class="hero">
    <h1>{{ t['hero_title'] }}</h1>
    <p>{{ t['hero_desc'] }}</p>
    
    <form method="POST" action="/download" onsubmit="startDownload()">
        <div class="search-container">
            <input type="text" name="url" id="linkInput" placeholder="{{ t['placeholder'] }}" required autocomplete="off">
            <button type="button" class="btn-paste" onclick="pasteText()">{{ t['paste'] }}</button>
            <button type="submit" class="btn-dl" id="dlBtn">{{ t['download'] }}</button>
        </div>
        
        <div class="options-row">
            <label class="opt-radio"><input type="radio" name="format_type" value="video" checked> {{ t['opt_video'] }}</label>
            <label class="opt-radio"><input type="radio" name="format_type" value="mp3"> {{ t['opt_audio'] }}</label>
            <label class="opt-radio"><input type="radio" name="format_type" value="story"> {{ t['opt_story'] }}</label>
            <label class="opt-radio"><input type="radio" name="format_type" value="photo"> {{ t['opt_photo'] }}</label>
        </div>
    </form>
</div>

<div class="section-wrap">
    <h2 class="sec-title">{{ t['feat_title'] }}</h2>
    <div class="features-grid">
        <div class="f-card"><h3>{{ t['f1_title'] }}</h3><p>{{ t['f1_desc'] }}</p></div>
        <div class="f-card"><h3>{{ t['f2_title'] }}</h3><p>{{ t['f2_desc'] }}</p></div>
        <div class="f-card"><h3>{{ t['f3_title'] }}</h3><p>{{ t['f3_desc'] }}</p></div>
    </div>
</div>

<div class="section-wrap">
    <h2 class="sec-title">{{ t['how_title'] }}</h2>
    <div class="how-box">
        <div class="step"><h4>{{ t['step1_t'] }}</h4><p>{{ t['step1_d'] }}</p></div>
        <div class="step"><h4>{{ t['step2_t'] }}</h4><p>{{ t['step2_d'] }}</p></div>
        <div class="step"><h4>{{ t['step3_t'] }}</h4><p>{{ t['step3_d'] }}</p></div>
    </div>
</div>

<div class="section-wrap">
    <h2 class="sec-title">{{ t['faq_title'] }}</h2>
    <div class="faq-container">
        <details><summary>{{ t['q1'] }}</summary><p>{{ t['a1'] }}</p></details>
        <details><summary>{{ t['q2'] }}</summary><p>{{ t['a2'] }}</p></details>
        <details><summary>{{ t['q3'] }}</summary><p>{{ t['a3'] }}</p></details>
    </div>
</div>
"""

# ==========================================
# 🚦 مسارات الموقع (Routes) ومنطق التحميل
# ==========================================

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route('/')
def home():
    t, lang = get_t()
    content = render_template_string(HOME_HTML, t=t)
    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content)

# منطق التحميل الفعلي (yt-dlp)
@app.route('/download', methods=['POST'])
def download_video():
    t, lang = get_t()
    url = request.form.get('url')
    format_type = request.form.get('format_type', 'video')
    
    # تنظيف السيرفر
    for file in glob.glob("downloaded_media*"):
        try: os.remove(file)
        except: pass

    ydl_opts = {'quiet': True, 'no_warnings': True}

    try:
        if format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': 'downloaded_media', 
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            })
        else:
            ydl_opts.update({'format': 'best', 'outtmpl': 'downloaded_media.%(ext)s'})

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        downloaded_files = glob.glob("downloaded_media*")
        if downloaded_files:
            final_file = downloaded_files[0]
            ext = os.path.splitext(final_file)[1]
            return send_file(final_file, as_attachment=True, download_name=f"AekDownloader_{format_type}{ext}")
        else:
            raise Exception("File not found")
            
    except Exception as e:
        content = render_template_string(HOME_HTML, t=t)
        error_msg = "❌ Error: Link is invalid or video is private." if lang == 'en' else "❌ عذراً، تأكد من صحة الرابط أو أن المقطع متاح للعامة."
        return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content, error=error_msg)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
