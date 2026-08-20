import os
import glob
from flask import Flask, render_template_string, request, session, redirect, url_for, send_file
import yt_dlp

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ==========================================
# 🌐 قاموس الترجمات (مخصص بالكامل لهوية تيك توك)
# ==========================================
TRANSLATIONS = {
    'en': {
        'lang_name': 'English', 'title': 'AekDownloader | TikTok Downloader',
        'nav_home': 'Home', 'nav_contact': 'Contact Us', 'nav_privacy': 'Privacy Policy', 'nav_terms': 'Terms of Use',
        'tiktok_badge': '🎵 The #1 TikTok Downloader',
        'hero_title': 'TikTok Video Downloader', 
        'hero_desc': 'Download TikTok videos without watermark, stories, and MP3 audio instantly.',
        'placeholder': 'Paste TikTok link here...', 'paste': 'Paste 📋', 'download': 'Download',
        'opt_video': 'Video (MP4)', 'opt_audio': 'Audio (MP3)', 'opt_story': 'Story', 'opt_photo': 'Photos',
        'feat_title': 'Why Choose Us?',
        'f1_title': 'No Watermark', 'f1_desc': 'Download TikTok videos in HD without any logos.',
        'f2_title': 'Unlimited & Free', 'f2_desc': 'Save as many TikToks as you want without restrictions.',
        'f3_title': 'Multiple Formats', 'f3_desc': 'Extract MP3 audio or download TikTok image slideshows.',
        'how_title': 'How to download from TikTok?',
        'step1_t': '1. Copy the Link', 'step1_d': 'Open the TikTok app, find the video, tap Share, and select "Copy Link".',
        'step2_t': '2. Paste it here', 'step2_d': 'Come back to our site, paste the link in the input field above.',
        'step3_t': '3. Download', 'step3_d': 'Choose your format and click Download to save it.',
        'faq_title': 'FAQ',
        'q1': 'Are the downloaded files safe?', 'a1': 'Absolutely. All files are processed securely from official TikTok servers.',
        'q2': 'Where are files saved?', 'a2': 'They are saved in your device\'s "Downloads" folder.',
        'q3': 'Can I download private TikToks?', 'a3': 'No, we can only process publicly available videos.',
        'footer_text': '© 2026 AekDownloader. We are not affiliated with TikTok.'
    },
    'ar': {
        'lang_name': 'العربية', 'title': 'AekDownloader | تحميل تيك توك',
        'nav_home': 'الرئيسية', 'nav_contact': 'اتصل بنا', 'nav_privacy': 'الخصوصية', 'nav_terms': 'شروط الاستخدام',
        'tiktok_badge': '🎵 المنصة الأولى لتحميل تيك توك',
        'hero_title': 'أداة تحميل تيك توك الشاملة', 
        'hero_desc': 'قم بتحميل فيديوهات تيك توك بدون علامة مائية، الستوريات، وصوتيات MP3 بضغطة زر.',
        'placeholder': 'ألصق رابط تيك توك هنا...', 'paste': 'لصق 📋', 'download': 'تحميل',
        'opt_video': 'فيديو (بدون علامة)', 'opt_audio': 'صوت (MP3)', 'opt_story': 'ستوري', 'opt_photo': 'صور',
        'feat_title': 'لماذا تختار منصتنا؟',
        'f1_title': 'بدون علامة مائية', 'f1_desc': 'احصل على فيديوهات تيك توك الأصلية خالية تماماً من الشعار.',
        'f2_title': 'مجاني وغير محدود', 'f2_desc': 'حمل ما تشاء من مقاطع تيك توك مجاناً بدون قيود.',
        'f3_title': 'صيغ متعددة', 'f3_desc': 'استخرج الصوتيات أو حمل صور تيك توك كفيديو مدمج.',
        'how_title': 'كيفية التحميل من تيك توك؟',
        'step1_t': '1. انسخ الرابط', 'step1_d': 'افتح تطبيق تيك توك، اضغط مشاركة ثم "نسخ الرابط".',
        'step2_t': '2. ألصق الرابط', 'step2_d': 'عد لموقعنا وألصق الرابط في المربع بالأعلى.',
        'step3_t': '3. اضغط تحميل', 'step3_d': 'اختر الصيغة المناسبة واضغط تحميل.',
        'faq_title': 'الأسئلة الشائعة',
        'q1': 'هل الملفات آمنة؟', 'a1': 'نعم، يتم جلبها مباشرة من سيرفرات تيك توك الرسمية بأمان تام.',
        'q2': 'أين أجد الفيديوهات؟', 'a2': 'في مجلد "التنزيلات" أو الاستوديو بهاتفك.',
        'q3': 'هل يمكن تحميل مقطع خاص؟', 'a3': 'لا، ندعم فقط الحسابات العامة المتاحة للجميع.',
        'footer_text': '© 2026 AekDownloader. نحن غير تابعين لشركة TikTok.'
    },
    'fr': {
        'lang_name': 'Français', 'title': 'AekDownloader | Téléchargeur TikTok',
        'nav_home': 'Accueil', 'nav_contact': 'Contact', 'nav_privacy': 'Confidentialité', 'nav_terms': 'Conditions',
        'tiktok_badge': '🎵 Téléchargeur TikTok #1',
        'hero_title': 'Téléchargeur Vidéo TikTok', 'hero_desc': 'Téléchargez des vidéos TikTok sans filigrane et MP3.',
        'placeholder': 'Collez le lien TikTok ici...', 'paste': 'Coller 📋', 'download': 'Télécharger',
        'opt_video': 'Vidéo (MP4)', 'opt_audio': 'Audio (MP3)', 'opt_story': 'Story', 'opt_photo': 'Photos',
        'feat_title': 'Pourquoi nous choisir?',
        'f1_title': 'Sans Filigrane', 'f1_desc': 'Vidéos TikTok HD sans logo.',
        'f2_title': 'Illimité & Gratuit', 'f2_desc': 'Téléchargez des TikToks sans restriction.',
        'f3_title': 'Formats Multiples', 'f3_desc': 'Extraire MP3 ou télécharger des photos TikTok.',
        'how_title': 'Comment télécharger sur TikTok?',
        'step1_t': '1. Copier le lien', 'step1_d': 'Ouvrez TikTok, cliquez sur Partager et copier le lien.',
        'step2_t': '2. Coller ici', 'step2_d': 'Collez le lien dans le champ ci-dessus.',
        'step3_t': '3. Télécharger', 'step3_d': 'Choisissez le format et cliquez sur Télécharger.',
        'faq_title': 'FAQ',
        'q1': 'Est-ce sûr?', 'a1': 'Oui, depuis les serveurs officiels de TikTok.',
        'q2': 'Où sont les fichiers?', 'a2': 'Dans votre dossier Téléchargements.',
        'q3': 'Vidéos privées?', 'a3': 'Non, uniquement les vidéos publiques.',
        'footer_text': '© 2026 AekDownloader. Non affilié à TikTok.'
    },
    'es': {
        'lang_name': 'Español', 'title': 'AekDownloader | Descargador de TikTok',
        'nav_home': 'Inicio', 'nav_contact': 'Contacto', 'nav_privacy': 'Privacidad', 'nav_terms': 'Términos',
        'tiktok_badge': '🎵 Descargador de TikTok #1',
        'hero_title': 'Descargador de Videos TikTok', 'hero_desc': 'Descarga videos de TikTok sin marca de agua.',
        'placeholder': 'Pega el enlace de TikTok...', 'paste': 'Pegar 📋', 'download': 'Descargar',
        'opt_video': 'Video (MP4)', 'opt_audio': 'Audio (MP3)', 'opt_story': 'Historia', 'opt_photo': 'Fotos',
        'feat_title': '¿Por qué elegirnos?',
        'f1_title': 'Sin Marca de Agua', 'f1_desc': 'Videos TikTok HD sin logos.',
        'f2_title': 'Ilimitado y Gratis', 'f2_desc': 'Descarga TikToks sin restricciones.',
        'f3_title': 'Múltiples Formatos', 'f3_desc': 'Extrae MP3 o fotos de TikTok.',
        'how_title': '¿Cómo descargar de TikTok?',
        'step1_t': '1. Copiar Enlace', 'step1_d': 'Abre TikTok, comparte y copia el enlace.',
        'step2_t': '2. Pegar Aquí', 'step2_d': 'Pega el enlace arriba.',
        'step3_t': '3. Descargar', 'step3_d': 'Elige formato y descarga.',
        'faq_title': 'Preguntas Frecuentes',
        'q1': '¿Es seguro?', 'a1': 'Sí, procesado desde servidores oficiales de TikTok.',
        'q2': '¿Dónde se guardan?', 'a2': 'En tu carpeta de Descargas.',
        'q3': '¿Videos privados?', 'a3': 'No, solo contenido público.',
        'footer_text': '© 2026 AekDownloader. No afiliados a TikTok.'
    },
    'ru': {
        'lang_name': 'Русский', 'title': 'AekDownloader | TikTok Загрузчик',
        'nav_home': 'Главная', 'nav_contact': 'Контакты', 'nav_privacy': 'Конфиденциальность', 'nav_terms': 'Условия',
        'tiktok_badge': '🎵 Лучший Загрузчик TikTok',
        'hero_title': 'Загрузчик Видео TikTok', 'hero_desc': 'Скачивайте видео TikTok без водяных знаков и MP3.',
        'placeholder': 'Вставьте ссылку TikTok...', 'paste': 'Вставить 📋', 'download': 'Скачать',
        'opt_video': 'Видео (MP4)', 'opt_audio': 'Аудио (MP3)', 'opt_story': 'История', 'opt_photo': 'Фото',
        'feat_title': 'Почему мы?',
        'f1_title': 'Без водяных знаков', 'f1_desc': 'TikTok HD без логотипов.',
        'f2_title': 'Бесплатно', 'f2_desc': 'Качайте TikTok без ограничений.',
        'f3_title': 'Разные форматы', 'f3_desc': 'MP3 и фото из TikTok.',
        'how_title': 'Как скачать из TikTok?',
        'step1_t': '1. Скопировать', 'step1_d': 'В TikTok нажмите поделиться и скопировать.',
        'step2_t': '2. Вставить', 'step2_d': 'Вставьте ссылку выше.',
        'step3_t': '3. Скачать', 'step3_d': 'Выберите формат и качайте.',
        'faq_title': 'Частые Вопросы',
        'q1': 'Безопасно?', 'a1': 'Да, с официальных серверов TikTok.',
        'q2': 'Где файлы?', 'a2': 'В папке Загрузки.',
        'q3': 'Приватные видео?', 'a3': 'Только публичные.',
        'footer_text': '© 2026 AekDownloader. Не связано с TikTok.'
    },
    'zh': {
        'lang_name': '中文', 'title': 'AekDownloader | TikTok下载器',
        'nav_home': '首页', 'nav_contact': '联系', 'nav_privacy': '隐私', 'nav_terms': '条款',
        'tiktok_badge': '🎵 最佳 TikTok 下载器',
        'hero_title': 'TikTok 视频下载器', 'hero_desc': '下载无水印 TikTok 视频和 MP3。',
        'placeholder': '粘贴 TikTok 链接...', 'paste': '粘贴 📋', 'download': '下载',
        'opt_video': '视频 (MP4)', 'opt_audio': '音频 (MP3)', 'opt_story': '故事', 'opt_photo': '照片',
        'feat_title': '为什么选择我们？',
        'f1_title': '无水印', 'f1_desc': '高清 TikTok 视频，无标志。',
        'f2_title': '免费无限', 'f2_desc': '无限制下载 TikTok。',
        'f3_title': '多种格式', 'f3_desc': '提取 MP3 或下载 TikTok 照片。',
        'how_title': '如何从 TikTok 下载？',
        'step1_t': '1. 复制链接', 'step1_d': '打开 TikTok，复制链接。',
        'step2_t': '2. 粘贴至此', 'step2_d': '在上方粘贴链接。',
        'step3_t': '3. 下载', 'step3_d': '选择格式并下载。',
        'faq_title': '常见问题',
        'q1': '安全吗？', 'a1': '安全，来自 TikTok 官方服务器。',
        'q2': '文件在哪？', 'a2': '在下载文件夹中。',
        'q3': '私人视频？', 'a3': '仅限公开视频。',
        'footer_text': '© 2026 AekDownloader. 与 TikTok 无关。'
    },
    'ja': {
        'lang_name': '日本語', 'title': 'AekDownloader | TikTokダウンローダー',
        'nav_home': 'ホーム', 'nav_contact': 'お問い合わせ', 'nav_privacy': 'プライバシー', 'nav_terms': '利用規約',
        'tiktok_badge': '🎵 No.1 TikTok ダウンローダー',
        'hero_title': 'TikTok 動画ダウンローダー', 'hero_desc': '透かしなしのTikTok動画とMP3をダウンロード。',
        'placeholder': 'TikTokリンクを貼り付け...', 'paste': '貼り付け 📋', 'download': 'ダウンロード',
        'opt_video': '動画 (MP4)', 'opt_audio': '音声 (MP3)', 'opt_story': 'ストーリー', 'opt_photo': '写真',
        'feat_title': '選ばれる理由',
        'f1_title': '透かしなし', 'f1_desc': 'ロゴなしのTikTok HD動画。',
        'f2_title': '無制限＆無料', 'f2_desc': 'TikTokを制限なしでダウンロード。',
        'f3_title': '複数フォーマット', 'f3_desc': 'TikTokのMP3や写真を抽出。',
        'how_title': 'TikTokからのダウンロード方法',
        'step1_t': '1. リンクをコピー', 'step1_d': 'TikTokでリンクをコピーします。',
        'step2_t': '2. ここに貼り付け', 'step2_d': '上にリンクを貼り付け。',
        'step3_t': '3. ダウンロード', 'step3_d': 'フォーマットを選んでダウンロード。',
        'faq_title': 'よくある質問',
        'q1': '安全ですか？', 'a1': 'はい、TikTok公式サーバーから安全に処理されます。',
        'q2': 'ファイルはどこ？', 'a2': 'ダウンロードフォルダにあります。',
        'q3': '非公開動画は？', 'a3': '公開動画のみ対応。',
        'footer_text': '© 2026 AekDownloader. TikTokとは提携していません。'
    }
}

def get_t():
    lang = session.get('lang', 'ar') # العربية الافتراضية
    if lang not in TRANSLATIONS:
        lang = 'ar'
    return TRANSLATIONS[lang], lang

# ==========================================
# 🎨 القالب الأساسي (الأنيميشن + الليلي والنهاري)
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
        :root {
            --primary: #2563eb;
            --primary-hover: #1e40af;
            --bg: #f0f8ff;
            --text: #0f172a;
            --box-bg: rgba(255, 255, 255, 0.85); 
            --border: rgba(226, 232, 240, 0.8);
            --footer-bg: rgba(15, 23, 42, 0.95);
            --footer-text: #cbd5e1;
        }
        [data-theme="dark"] {
            --primary: #fe2c55; /* لون تيك توك مميز في الليلي */
            --primary-hover: #e61e45;
            --bg: #090b14;
            --text: #f8fafc;
            --box-bg: rgba(30, 41, 59, 0.75); 
            --border: rgba(51, 65, 85, 0.8);
            --footer-bg: rgba(2, 6, 23, 0.95);
            --footer-text: #94a3b8;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; transition: background-color 0.4s, color 0.4s; }
        body { background: var(--bg); color: var(--text); display: flex; flex-direction: column; min-height: 100vh; overflow-x: hidden; position: relative; }
        
        #animated-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; overflow: hidden; pointer-events: none; }
        .world-element { position: absolute; border-radius: 50%; animation: floatWorld linear infinite; }
        @keyframes floatWorld {
            0% { transform: translateY(110vh) translateX(0) rotate(0deg); opacity: 0; }
            20% { opacity: 0.6; }
            80% { opacity: 0.6; }
            100% { transform: translateY(-10vh) translateX(100px) rotate(360deg); opacity: 0; }
        }

        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 15px 5%; background: var(--box-bg); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); position: relative; z-index: 10; }
        .logo { font-size: 24px; font-weight: 900; color: var(--text); text-decoration: none; }
        .logo span { color: var(--primary); }
        .nav-controls { display: flex; gap: 15px; align-items: center; }
        
        .theme-toggle { background: transparent; border: 2px solid var(--primary); color: var(--text); padding: 5px 12px; border-radius: 20px; cursor: pointer; font-weight: bold; font-size: 14px; }
        
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

        function generateWorlds(theme) {
            animBg.innerHTML = ''; 
            const count = 15;
            for(let i=0; i<count; i++) {
                let el = document.createElement('div');
                el.className = 'world-element';
                
                let size = Math.random() * 80 + 20; 
                let left = Math.random() * 100;
                let duration = Math.random() * 10 + 10;
                let delay = Math.random() * 10;
                
                el.style.width = size + 'px';
                el.style.height = size + 'px';
                el.style.left = left + 'vw';
                el.style.animationDuration = duration + 's';
                el.style.animationDelay = delay + 's';
                
                if(theme === 'dark') {
                    // نجوم متوهجة في الليلي
                    el.style.background = 'radial-gradient(circle, rgba(254, 44, 85, 0.8) 0%, rgba(0,0,0,0) 70%)';
                    el.style.boxShadow = '0 0 20px rgba(254, 44, 85, 0.5)';
                } else {
                    // غيوم ناعمة في النهاري
                    el.style.background = 'rgba(255, 255, 255, 0.7)';
                    el.style.boxShadow = '0 10px 30px rgba(0,0,0,0.05)';
                }
                
                animBg.appendChild(el);
            }
        }

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
# 📄 محتوى الواجهة (مع شارة تيك توك)
# ==========================================
HOME_HTML = """
<style>
    .hero { text-align: center; padding: 60px 20px 40px; width: 100%; }
    
    /* الشارة التوضيحية لتيك توك */
    .badge-tt {
        background: rgba(37, 99, 235, 0.1); 
        color: var(--primary); 
        border: 1px solid var(--primary); 
        padding: 5px 15px; 
        border-radius: 20px; 
        display: inline-block; 
        font-weight: bold; 
        margin-bottom: 15px; 
        font-size: 14px; 
        backdrop-filter: blur(5px);
    }
    [data-theme="dark"] .badge-tt { background: rgba(254, 44, 85, 0.1); }

    .hero h1 { font-size: 38px; font-weight: 900; margin-bottom: 15px; text-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .hero p { opacity: 0.8; font-size: 18px; margin-bottom: 40px; }
    
    .search-container { max-width: 700px; margin: 0 auto; background: var(--box-bg); padding: 10px; border-radius: 16px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); border: 1px solid var(--border); backdrop-filter: blur(15px); display: flex; gap: 8px; flex-wrap: wrap; }
    .search-container input { flex: 1; min-width: 250px; border: none; padding: 15px 20px; font-size: 16px; outline: none; background: transparent; color: var(--text); }
    .btn-paste { background: transparent; color: var(--text); border: 1px solid var(--border); padding: 0 15px; border-radius: 10px; font-weight: bold; cursor: pointer; }
    .btn-dl { background: var(--primary); color: #fff; border: none; padding: 15px 30px; font-size: 16px; font-weight: bold; border-radius: 10px; cursor: pointer; transition: 0.3s; }
    .btn-dl:hover { transform: scale(1.05); opacity: 0.9; }

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
    [data-theme="dark"] .how-box { background: rgba(15, 23, 42, 0.8); border-color: rgba(254, 44, 85, 0.3); }
    .step { position: relative; padding: 0 40px; margin-bottom: 30px; }
    [dir="ltr"] .step { padding: 0 0 0 40px; }
    .step::before { content: "✓"; position: absolute; right: 0; top: 0; color: #38bdf8; font-size: 24px; font-weight: bold; }
    [dir="ltr"] .step::before { right: auto; left: 0; }
    [data-theme="dark"] .step::before { color: var(--primary); }
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
    <div class="badge-tt">{{ t['tiktok_badge'] }}</div>
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
# 🚦 مسارات الموقع والتحميل (Routes)
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

@app.route('/download', methods=['POST'])
def download_video():
    t, lang = get_t()
    url = request.form.get('url')
    format_type = request.form.get('format_type', 'video')
    
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
            return send_file(final_file, as_attachment=True, download_name=f"TikTok_{format_type}{ext}")
        else:
            raise Exception("File not found")
            
    except Exception as e:
        content = render_template_string(HOME_HTML, t=t)
        error_msg = "❌ Error: Link is invalid or TikTok video is private." if lang == 'en' else "❌ عذراً، تأكد من صحة الرابط أو أن مقطع تيك توك متاح للعامة."
        return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content, error=error_msg)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
