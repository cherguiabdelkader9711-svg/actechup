import os
import glob
from flask import Flask, render_template_string, request, session, redirect, url_for, send_file
import yt_dlp

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ==========================================
# 🌐 قاموس الترجمات الشامل
# ==========================================
TRANSLATIONS = {
    'en': {
        'lang_name': 'English', 'title': 'AekDownloader | TikTok Downloader',
        'nav_home': 'Home', 'nav_contact': 'Contact Us', 'nav_privacy': 'Privacy Policy', 'nav_terms': 'Terms of Use',
        'tiktok_badge': '🎵 The #1 TikTok Downloader',
        'hero_title': 'TikTok Video Downloader', 'hero_desc': 'Download TikTok videos without watermark, stories, and MP3 audio instantly.',
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
        'privacy_text': 'We respect your privacy. All downloads are processed in real-time. We do not store your IP address, downloaded media, or personal data on our servers. Your connection is fully secured.',
        'terms_text': 'By using AekDownloader, you agree to use it for personal purposes only. You must not download copyrighted materials without the owner\'s permission. We are not responsible for any misuse of the downloaded content.',
        'c_name': 'Full Name', 'c_email': 'Email Address', 'c_msg': 'Your Message...', 'c_send': 'Send Message',
        'footer_text': '© 2026 AekDownloader. We are not affiliated with TikTok.'
    },
    'ar': {
        'lang_name': 'العربية', 'title': 'AekDownloader | تحميل تيك توك',
        'nav_home': 'الرئيسية', 'nav_contact': 'اتصل بنا', 'nav_privacy': 'سياسة الخصوصية', 'nav_terms': 'شروط الاستخدام',
        'tiktok_badge': '🎵 المنصة الأولى لتحميل تيك توك',
        'hero_title': 'أداة تحميل تيك توك الشاملة', 'hero_desc': 'قم بتحميل فيديوهات تيك توك بدون علامة مائية، الستوريات، وصوتيات MP3 بضغطة زر.',
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
        'privacy_text': 'نحن نولي أولوية قصوى لخصوصيتك. جميع عمليات التحميل تتم بشكل لحظي. نحن لا نقوم بتخزين عنوان الـ IP الخاص بك، أو الملفات المحملة، أو أي بيانات شخصية على خوادمنا.',
        'terms_text': 'باستخدامك لمنصة AekDownloader، فإنك توافق على استخدام الأداة للأغراض الشخصية فقط. يُمنع تحميل المواد المحمية بحقوق الطبع والنشر دون إذن. نحن نخلي مسؤوليتنا عن أي سوء استخدام للمحتوى.',
        'c_name': 'الاسم الكامل', 'c_email': 'البريد الإلكتروني', 'c_msg': 'اكتب رسالتك هنا...', 'c_send': 'إرسال الرسالة',
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
        'f3_title': 'Formats Multiples', 'f3_desc': 'Extraire MP3 ou télécharger des photos.',
        'how_title': 'Comment télécharger?',
        'step1_t': '1. Copier le lien', 'step1_d': 'Ouvrez TikTok, cliquez sur Partager et copier le lien.',
        'step2_t': '2. Coller ici', 'step2_d': 'Collez le lien dans le champ ci-dessus.',
        'step3_t': '3. Télécharger', 'step3_d': 'Choisissez le format et téléchargez.',
        'faq_title': 'FAQ',
        'q1': 'Est-ce sûr?', 'a1': 'Oui, depuis les serveurs officiels de TikTok.',
        'q2': 'Où sont les fichiers?', 'a2': 'Dans votre dossier Téléchargements.',
        'q3': 'Vidéos privées?', 'a3': 'Non, uniquement les vidéos publiques.',
        'privacy_text': 'Nous respectons votre vie privée. Aucun téléchargement n\'est stocké sur nos serveurs.',
        'terms_text': 'En utilisant ce site, vous acceptez de l\'utiliser uniquement à des fins personnelles.',
        'c_name': 'Nom', 'c_email': 'Email', 'c_msg': 'Message', 'c_send': 'Envoyer',
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
        'how_title': '¿Cómo descargar?',
        'step1_t': '1. Copiar Enlace', 'step1_d': 'Abre TikTok, comparte y copia el enlace.',
        'step2_t': '2. Pegar Aquí', 'step2_d': 'Pega el enlace arriba.',
        'step3_t': '3. Descargar', 'step3_d': 'Elige formato y descarga.',
        'faq_title': 'FAQ',
        'q1': '¿Es seguro?', 'a1': 'Sí, procesado desde servidores oficiales de TikTok.',
        'q2': '¿Dónde se guardan?', 'a2': 'En tu carpeta de Descargas.',
        'q3': '¿Videos privados?', 'a3': 'No, solo contenido público.',
        'privacy_text': 'Respetamos su privacidad. No almacenamos medios descargados ni datos personales.',
        'terms_text': 'Al utilizar este sitio, acepta usarlo solo para fines personales.',
        'c_name': 'Nombre', 'c_email': 'Correo', 'c_msg': 'Mensaje', 'c_send': 'Enviar',
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
        'f3_title': 'Форматы', 'f3_desc': 'MP3 и фото из TikTok.',
        'how_title': 'Как скачать?',
        'step1_t': '1. Скопировать', 'step1_d': 'В TikTok нажмите поделиться и скопировать.',
        'step2_t': '2. Вставить', 'step2_d': 'Вставьте ссылку выше.',
        'step3_t': '3. Скачать', 'step3_d': 'Выберите формат и качайте.',
        'faq_title': 'Частые Вопросы',
        'q1': 'Безопасно?', 'a1': 'Да, с официальных серверов TikTok.',
        'q2': 'Где файлы?', 'a2': 'В папке Загрузки.',
        'q3': 'Приватные видео?', 'a3': 'Только публичные.',
        'privacy_text': 'Мы уважаем вашу конфиденциальность. Мы не храним загруженные медиафайлы.',
        'terms_text': 'Вы соглашаетесь использовать этот сайт только в личных целях.',
        'c_name': 'Имя', 'c_email': 'Email', 'c_msg': 'Сообщение', 'c_send': 'Отправить',
        'footer_text': '© 2026 AekDownloader. Не связано с TikTok.'
    },
    'zh': {
        'lang_name': '中文', 'title': 'AekDownloader | TikTok下载器',
        'nav_home': '首页', 'nav_contact': '联系我们', 'nav_privacy': '隐私政策', 'nav_terms': '使用条款',
        'tiktok_badge': '🎵 最佳 TikTok 下载器',
        'hero_title': 'TikTok 视频下载器', 'hero_desc': '下载无水印 TikTok 视频和 MP3。',
        'placeholder': '粘贴 TikTok 链接...', 'paste': '粘贴 📋', 'download': '下载',
        'opt_video': '视频 (MP4)', 'opt_audio': '音频 (MP3)', 'opt_story': '故事', 'opt_photo': '照片',
        'feat_title': '为什么选择我们？',
        'f1_title': '无水印', 'f1_desc': '高清 TikTok 视频，无标志。',
        'f2_title': '免费无限', 'f2_desc': '无限制下载 TikTok。',
        'f3_title': '多种格式', 'f3_desc': '提取 MP3 或下载 TikTok 照片。',
        'how_title': '如何下载？',
        'step1_t': '1. 复制链接', 'step1_d': '打开 TikTok，复制链接。',
        'step2_t': '2. 粘贴至此', 'step2_d': '在上方粘贴链接。',
        'step3_t': '3. 下载', 'step3_d': '选择格式并下载。',
        'faq_title': '常见问题',
        'q1': '安全吗？', 'a1': '安全，来自 TikTok 官方服务器。',
        'q2': '文件在哪？', 'a2': '在下载文件夹中。',
        'q3': '私人视频？', 'a3': '仅限公开视频。',
        'privacy_text': '我们不存储下载的媒体或个人数据。',
        'terms_text': '使用本网站即表示您同意仅将其用于个人目的。',
        'c_name': '姓名', 'c_email': '邮箱', 'c_msg': '留言', 'c_send': '发送',
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
        'how_title': 'ダウンロード方法',
        'step1_t': '1. リンクをコピー', 'step1_d': 'TikTokでリンクをコピーします。',
        'step2_t': '2. ここに貼り付け', 'step2_d': '上にリンクを貼り付け。',
        'step3_t': '3. ダウンロード', 'step3_d': 'フォーマットを選んでダウンロード。',
        'faq_title': 'よくある質問',
        'q1': '安全ですか？', 'a1': 'はい、TikTok公式サーバーから安全に処理されます。',
        'q2': 'ファイルはどこ？', 'a2': 'ダウンロードフォルダにあります。',
        'q3': '非公開動画は？', 'a3': '公開動画のみ対応。',
        'privacy_text': 'ダウンロードしたメディアや個人データは保存されません。',
        'terms_text': '個人的な目的でのみ使用することに同意するものとします。',
        'c_name': '名前', 'c_email': 'メール', 'c_msg': 'メッセージ', 'c_send': '送信',
        'footer_text': '© 2026 AekDownloader. TikTokとは提携していません。'
    }
}

def get_t():
    lang = session.get('lang', 'en') 
    if lang not in TRANSLATIONS:
        lang = 'en'
    return TRANSLATIONS[lang], lang

# ==========================================
# 🎨 القالب الأساسي (تمت إضافة حيلة لمعالجة أخطاء سفاري/آيفون)
# ==========================================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ 'rtl' if lang == 'ar' else 'ltr' }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t['title'] }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800;900&display=swap" rel="stylesheet">

    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8318835663506534"
     crossorigin="anonymous"></script>
    
    <!-- منع وميض الشاشة وقراءة الوضع مباشرة -->
    <script>
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
    
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
            --primary: #fe2c55;
            --primary-hover: #e61e45;
            --bg: #090b14;
            --text: #f8fafc;
            --box-bg: rgba(30, 41, 59, 0.75); 
            --border: rgba(51, 65, 85, 0.8);
            --footer-bg: rgba(2, 6, 23, 0.95);
            --footer-text: #94a3b8;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; }
        
        /* إزالة انتقال الخلفيات عن العناصر الزجاجية لتجنب بطء الآيفون */
        body { transition: background-color 0.3s ease, color 0.3s ease; }
        
        body { background: var(--bg); color: var(--text); display: flex; flex-direction: column; min-height: 100vh; overflow-x: hidden; position: relative; }
        
        #animated-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; overflow: hidden; pointer-events: none; }
        .world-element { position: absolute; border-radius: 50%; animation: floatWorld linear infinite; }
        @keyframes floatWorld {
            0% { transform: translateY(110vh) translateX(0) rotate(0deg); opacity: 0; }
            20% { opacity: 0.6; }
            80% { opacity: 0.6; }
            100% { transform: translateY(-10vh) translateX(100px) rotate(360deg); opacity: 0; }
        }

        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 15px 5%; background: var(--box-bg); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); position: relative; z-index: 10; }
        .logo { font-size: 24px; font-weight: 900; color: var(--text); text-decoration: none; }
        .logo span { color: var(--primary); }
        .nav-controls { display: flex; gap: 15px; align-items: center; }
        
        .theme-toggle { background: transparent; border: 2px solid var(--primary); color: var(--text); padding: 5px 12px; border-radius: 20px; cursor: pointer; font-weight: bold; font-size: 14px; transition: 0.3s; }
        
        .lang-menu { position: relative; display: inline-block; }
        .lang-btn { background: var(--box-bg); border: 1px solid var(--border); padding: 8px 15px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; color: var(--text); transition: 0.3s; }
        .lang-dropdown { display: none; position: absolute; top: 110%; right: 0; background: var(--box-bg); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); min-width: 140px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
        [dir="rtl"] .lang-dropdown { right: auto; left: 0; }
        .lang-menu:hover .lang-dropdown { display: block; }
        .lang-dropdown a { display: block; padding: 10px 15px; color: var(--text); text-decoration: none; border-bottom: 1px solid var(--border); font-weight: 600; transition: 0.3s; }
        .lang-dropdown a:hover { background: var(--primary); color: #fff; }

        .main-content { flex: 1; display: flex; flex-direction: column; align-items: center; z-index: 2; position: relative; }
        .alert-error { background: rgba(220, 38, 38, 0.8); color: #fff; padding: 15px; text-align: center; font-weight: bold; width: 100%; backdrop-filter: blur(5px); }
        
        footer { background: var(--footer-bg); color: var(--footer-text); text-align: center; padding: 40px 20px; margin-top: auto; z-index: 2; position: relative; }
        .footer-links { display: flex; justify-content: center; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
        .footer-links a { color: var(--footer-text); text-decoration: none; font-weight: 600; font-size: 15px; transition: 0.3s; }
        .footer-links a:hover { color: var(--primary); text-decoration: underline; }
        footer p { opacity: 0.7; font-size: 14px; }

        @media (max-width: 768px) {
            .lang-btn span { display: none; }
        }
    </style>
</head>
<body>
    <div id="animated-bg"></div>

    <nav class="navbar" id="glass-nav">
        <a href="/" class="logo">Aek<span>Downloader</span></a>
        
        <div class="nav-controls">
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌓</button>
            <div class="lang-menu">
                <button class="lang-btn">🌐 <span>{{ t['lang_name'] }}</span></button>
                <div class="lang-dropdown" id="glass-lang">
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
        <div class="footer-links">
            <a href="/">{{ t['nav_home'] }}</a>
            <a href="/contact">{{ t['nav_contact'] }}</a>
            <a href="/privacy">{{ t['nav_privacy'] }}</a>
            <a href="/terms">{{ t['nav_terms'] }}</a>
        </div>
        <p>{{ t['footer_text'] }}</p>
    </footer>

    <script>
        const html = document.documentElement;
        const themeBtn = document.getElementById('themeBtn');
        const animBg = document.getElementById('animated-bg');
        
        const currentTheme = html.getAttribute('data-theme');
        updateUI(currentTheme);
        generateWorlds(currentTheme);

       function toggleTheme() {
            const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateUI(newTheme);
            generateWorlds(newTheme);
            
            document.body.style.display = 'none';
            document.body.offsetHeight; 
            document.body.style.display = '';
        }


        function updateUI(theme) {
            themeBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
        }

        function generateWorlds(theme) {
            animBg.innerHTML = ''; 
            const count = window.innerWidth > 768 ? 15 : 8; 
            for(let i=0; i<count; i++) {
                let el = document.createElement('div');
                el.className = 'world-element';
                let size = Math.random() * 80 + 20; 
                let left = Math.random() * 100;
                let duration = Math.random() * 10 + 15; 
                let delay = Math.random() * 10;
                
                el.style.width = size + 'px';
                el.style.height = size + 'px';
                el.style.left = left + 'vw';
                el.style.animationDuration = duration + 's';
                el.style.animationDelay = delay + 's';
                
                if(theme === 'dark') {
                    el.style.background = 'radial-gradient(circle, rgba(254, 44, 85, 0.6) 0%, rgba(0,0,0,0) 70%)';
                } else {
                    el.style.background = 'rgba(255, 255, 255, 0.6)';
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
                alert('Please paste manually.');
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

                // التحقق مما إذا تم إرسال الرسالة بنجاح لإظهار التنبيه المنبثق
        window.addEventListener('DOMContentLoaded', () => {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('success') === 'true') {
                const toast = document.createElement('div');
                toast.id = 'toast-msg';
                
                // تحديد النص حسب لغة الموقع الحالية
                const isAr = document.documentElement.lang === 'ar';
                toast.innerHTML = isAr ? '✅ تم إرسال رسالتك بنجاح! شكراً لتواصلك معنا.' : '✅ Your message has been sent successfully! Thank you.';
                
                document.body.appendChild(toast);
                
                // إزالة علامة النجاح من الرابط نظيفاً بعد ظهورها
                setTimeout(() => {
                    window.history.replaceState({}, document.title, window.location.pathname);
                }, 4000);
            }
        });

    </script>
</body>
</html>
"""

# ==========================================
# 📄 محتوى الواجهة الرئيسية
# ==========================================
HOME_HTML = """
<style>
    .hero { text-align: center; padding: 60px 20px 40px; width: 100%; }
    .badge-tt { background: rgba(37, 99, 235, 0.1); color: var(--primary); border: 1px solid var(--primary); padding: 5px 15px; border-radius: 20px; display: inline-block; font-weight: bold; margin-bottom: 15px; font-size: 14px; backdrop-filter: blur(5px); -webkit-backdrop-filter: blur(5px); }
    [data-theme="dark"] .badge-tt { background: rgba(254, 44, 85, 0.1); }
    .hero h1 { font-size: 38px; font-weight: 900; margin-bottom: 15px; text-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .hero p { opacity: 0.8; font-size: 18px; margin-bottom: 40px; }
    
    .search-container { max-width: 700px; margin: 0 auto; background: var(--box-bg); padding: 10px; border-radius: 16px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); border: 1px solid var(--border); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); display: flex; gap: 8px; flex-wrap: wrap; }
    .search-container input { flex: 1; min-width: 250px; border: none; padding: 15px 20px; font-size: 16px; outline: none; background: transparent; color: var(--text); }
    .btn-paste { background: transparent; color: var(--text); border: 1px solid var(--border); padding: 0 15px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.3s; }
    .btn-paste:hover { background: var(--bg); }
    .btn-dl { background: var(--primary); color: #fff; border: none; padding: 15px 30px; font-size: 16px; font-weight: bold; border-radius: 10px; cursor: pointer; transition: 0.3s; }
    .btn-dl:hover { transform: scale(1.05); opacity: 0.9; }

    .options-row { display: flex; justify-content: center; gap: 15px; margin-top: 25px; flex-wrap: wrap; }
    .opt-radio { display: flex; align-items: center; gap: 5px; cursor: pointer; font-weight: 600; padding: 8px 15px; border-radius: 20px; background: var(--box-bg); border: 1px solid var(--border); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); }
    .opt-radio input { accent-color: var(--primary); }

    .section-wrap { width: 100%; padding: 60px 20px; display: flex; flex-direction: column; align-items: center; }
    .sec-title { font-size: 32px; margin-bottom: 40px; font-weight: 800; text-align: center; }

    .features-grid { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; max-width: 1000px; }
    .f-card { background: var(--box-bg); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); padding: 30px; border-radius: 16px; width: 300px; text-align: center; border: 1px solid var(--border); }
    .f-card h3 { color: var(--primary); margin-bottom: 15px; font-size: 20px; }
    .f-card p { opacity: 0.8; font-size: 15px; line-height: 1.6; }

    .how-box { background: rgba(30, 58, 138, 0.8); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); color: #fff; padding: 40px; border-radius: 24px; max-width: 800px; width: 100%; border: 1px solid rgba(255,255,255,0.1); }
    [data-theme="dark"] .how-box { background: rgba(15, 23, 42, 0.8); border-color: rgba(254, 44, 85, 0.3); }
    .step { position: relative; padding: 0 40px; margin-bottom: 30px; }
    [dir="ltr"] .step { padding: 0 0 0 40px; }
    .step::before { content: "✓"; position: absolute; right: 0; top: 0; color: #38bdf8; font-size: 24px; font-weight: bold; }
    [dir="ltr"] .step::before { right: auto; left: 0; }
    [data-theme="dark"] .step::before { color: var(--primary); }
    .step h4 { font-size: 18px; margin-bottom: 5px; }
    .step p { opacity: 0.8; font-size: 15px; }

    .faq-container { max-width: 800px; width: 100%; }
    details { background: var(--box-bg); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); margin-bottom: 15px; border-radius: 12px; border: 1px solid var(--border); overflow: hidden; }
    summary { padding: 20px; font-weight: 700; cursor: pointer; font-size: 16px; list-style: none; display: flex; justify-content: space-between; align-items: center; }
    summary::-webkit-details-marker { display: none; }
    summary::after { content: "+"; color: var(--primary); font-size: 20px; }
    details[open] summary::after { content: "-"; }
    details p { padding: 0 20px 20px 20px; opacity: 0.8; line-height: 1.7; font-size: 15px; }

            /* تصميم الرسالة المنبثقة الخفيفة واللطيفة */
        #toast-msg {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--box-bg);
            color: var(--text);
            border: 1px solid var(--border);
            padding: 15px 25px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            font-weight: bold;
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideInUp 0.4s ease, fadeOut 0.4s ease 3.6s forwards;
        }
        [dir="rtl"] #toast-msg { right: auto; left: 30px; }
        @keyframes slideInUp {
            from { transform: translateY(100px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        @keyframes fadeOut {
            to { opacity: 0; visibility: hidden; }
        }


    
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
# 📄 محتوى الصفحات الفرعية الزجاجية
# ==========================================
PAGE_STYLE = """
<style>
    .page-box { max-width: 800px; margin: 40px auto; padding: 40px; background: var(--box-bg); border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid var(--border); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); text-align: center; }
    .page-box h2 { color: var(--primary); margin-bottom: 20px; font-size: 32px; }
    .page-box p { color: var(--text); opacity: 0.9; line-height: 1.8; font-size: 16px; margin-bottom: 20px; text-align: justify; }
    .contact-form { display: flex; flex-direction: column; gap: 15px; text-align: right; }
    [dir="ltr"] .contact-form { text-align: left; }
    .contact-form input, .contact-form textarea { width: 100%; padding: 15px; border-radius: 10px; border: 1px solid var(--border); background: transparent; color: var(--text); font-size: 15px; outline: none; }
    .contact-form button { background: var(--primary); color: #fff; border: none; padding: 15px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.3s; font-size: 16px; }
    .contact-form button:hover { background: var(--primary-hover); transform: scale(1.02); }
</style>
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

@app.route('/privacy')
def privacy():
    t, lang = get_t()
    content = PAGE_STYLE + f'<div class="page-box"><h2>{t["nav_privacy"]}</h2><p>{t["privacy_text"]}</p></div>'
    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content)

@app.route('/terms')
def terms():
    t, lang = get_t()
    content = PAGE_STYLE + f'<div class="page-box"><h2>{t["nav_terms"]}</h2><p>{t["terms_text"]}</p></div>'
    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content)

@app.route('/contact')
def contact():
    t, lang = get_t()
    
    # اختيار الترجمة حسب لغة المستخدم
    contact_texts = {
        'en': {
            'p1': 'Do you have any questions, suggestions, or business inquiries?',
            'p2': 'We’d love to hear from you!',
            'p3': '📧 You can email us directly at:',
            'p4': 'We typically respond within 24–48 hours. Thank you for reaching out!',
            'name': 'Name', 'email': 'Email', 'email_sup': 'Valid email is required',
            'mobile': 'Mobile Number', 'mobile_sup': 'This field is optional',
            'msg': 'Message', 'msg_sup': 'Must not contain more than 3000 characters', 'send': 'Send'
        },
        'ar': {
            'p1': 'هل لديك أي أسئلة أو اقتراحات أو استفسارات تجارية؟',
            'p2': 'يسعدنا جداً سماع صوتك!',
            'p3': '📧 يمكنك مراسلتنا مباشرة عبر البريد:',
            'p4': 'عادة ما نرد خلال 24-48 ساعة. شكراً لتواصلك معنا!',
            'name': 'الاسم', 'email': 'البريد الإلكتروني', 'email_sup': 'البريد الإلكتروني مطلوب وصحيح',
            'mobile': 'رقم الهاتف', 'mobile_sup': 'هذا الحقل اختياري',
            'msg': 'الرسالة', 'msg_sup': 'يجب ألا تتجاوز الرسالة 3000 حرف', 'send': 'إرسال'
        },
        'fr': {
            'p1': 'Avez-vous des questions ou des suggestions ?', 'p2': 'Nous serions ravis de vous entendre !',
            'p3': '📧 Écrivez-nous à :', 'p4': 'Réponse sous 24–48 heures.',
            'name': 'Nom', 'email': 'Email', 'email_sup': 'Email valide requis',
            'mobile': 'Numéro de mobile', 'mobile_sup': 'Optionnel',
            'msg': 'Message', 'msg_sup': 'Max 3000 caractères', 'send': 'Envoyer'
        },
        'es': {
            'p1': '¿Tiene alguna pregunta o sugerencia?', 'p2': '¡Nos encantaría saber de usted!',
            'p3': '📧 Escríbanos a:', 'p4': 'Respondemos en 24–48 horas.',
            'name': 'Nombre', 'email': 'Correo', 'email_sup': 'Correo válido requerido',
            'mobile': 'Móvil', 'mobile_sup': 'Opcional',
            'msg': 'Mensaje', 'msg_sup': 'Máximo 3000 caracteres', 'send': 'Enviar'
        },
        'ru': {
            'p1': 'У вас есть вопросы или предложения?', 'p2': 'Мы будем рады услышать вас!',
            'p3': '📧 Напишите нам:', 'p4': 'Мы отвечаем в течение 24–48 часов.',
            'name': 'Имя', 'email': 'Email', 'email_sup': 'Требуется действительный email',
            'mobile': 'Телефон', 'mobile_sup': 'Необязательно',
            'msg': 'Сообщение', 'msg_sup': 'Максимум 3000 символов', 'send': 'Отправить'
        },
        'zh': {
            'p1': '您有任何问题或建议吗？', 'p2': '我们很高兴听到您的声音！',
            'p3': '📧 直接发邮件给我们：', 'p4': '我们通常会在 24-48 小时内回复。',
            'name': '姓名', 'email': '邮箱', 'email_sup': '需要有效的邮箱',
            'mobile': '手机号码', 'mobile_sup': '可选',
            'msg': '留言', 'msg_sup': '最多3000个字符', 'send': '发送'
        },
        'ja': {
            'p1': 'ご質問やご意見はありますか？', 'p2': 'お気軽にお問い合わせください！',
            'p3': '📧 直接メールを送る：', 'p4': '通常24〜48時間以内に返信いたします。',
            'name': 'お名前', 'email': 'メールアドレス', 'email_sup': '有効なメールが必要です',
            'mobile': '電話番号', 'mobile_sup': '任意',
            'msg': 'メッセージ', 'msg_sup': '3000文字以内', 'send': '送信'
        }
    }
    
    ct = contact_texts.get(lang, contact_texts['en'])
    dir_val = 'rtl' if lang == 'ar' else 'ltr'
    
    # استخدام النص العادي (بدون f-string) لحماية أكواد CSS و JS من الأخطاء
    html_content = """
    <div class="page-box" style="max-width: 650px; text-align: left;">
        <div style="margin-bottom: 25px; text-align: left;" dir="LANG_DIR">
            <p style="margin-bottom: 8px;">P1_VAL</p>
            <p style="margin-bottom: 8px;">P2_VAL</p>
            <p style="margin-bottom: 8px;">P3_VAL <strong>aekchergui8@gmail.com</strong></p>
            <p>P4_VAL</p>
        </div>

        <div class="formB">
          <form action="https://formsubmit.co/aekchergui8@gmail.com" method="post">
            
            <div class="area">
              <input type="text" name="name" required autocomplete="off" oninput="checkInput(this)" onblur="checkInput(this)">
              <label class="n">NAME_VAL</label>
            </div>
            
            <div class="area">
              <input type="email" name="email" required autocomplete="off" oninput="checkInput(this)" onblur="checkInput(this)">
              <label class="n">EMAIL_VAL</label>
              <span class="sup">ESUP_VAL</span>
            </div>

            <div class="area">
              <input type="text" name="mobile" autocomplete="off" oninput="checkInput(this)" onblur="checkInput(this)">
              <label class="n">MOB_VAL</label>
              <span class="sup">MSUP_VAL</span>
            </div>

            <div class="area">
              <textarea name="message" maxlength="3000" required autocomplete="off" oninput="checkInput(this)" onblur="checkInput(this)"></textarea>
              <label class="n">MSG_VAL</label>
              <span class="sup">MSGSUP_VAL</span>
            </div>
            
            <input name="_captcha" type="hidden" value="false" />
            <input name="_template" type="hidden" value="box" />
            <input name="_next" type="hidden" value="https://www.actechup.online/?success=true" />


            <button type="submit">SEND_VAL</button>
          </form>
        </div>
    </div>

    <style>
        .formB { max-width: 100%; font-size: 1rem; margin: auto; text-align: left; }
        [dir="rtl"] .formB { text-align: right; }
        .formB form { display: flex; flex-direction: column; gap: 20px; }
        .formB .area { position: relative; margin-top: 10px; }
        .formB .area input, .formB .area textarea {
            width: 100%; padding: 16px; border: 1px solid var(--border);
            border-radius: 8px; color: var(--text); background-color: var(--box-bg);
            font-size: 1rem; outline: none; transition: border-color 0.3s;
        }
        .formB .area input:focus, .formB .area textarea:focus { border-color: var(--primary); }
        .formB .area .n {
            position: absolute; top: 16px; left: 16px; padding: 0 5px;
            color: var(--text); opacity: 0.7; background: transparent;
            pointer-events: none; transition: 0.25s ease all; font-size: 1rem;
        }
        [dir="rtl"] .formB .area .n { left: auto; right: 16px; }
        .formB .area input:focus ~ .n,
        .formB .area input.has-value ~ .n,
        .formB .area textarea:focus ~ .n,
        .formB .area textarea.has-value ~ .n {
            top: -11px; left: 12px; font-size: 0.85rem; opacity: 1;
            background: var(--box-bg); color: var(--primary); font-weight: bold;
        }
        [dir="rtl"] .formB .area input:focus ~ .n,
        [dir="rtl"] .formB .area input.has-value ~ .n,
        [dir="rtl"] .formB .area textarea:focus ~ .n,
        [dir="rtl"] .formB .area textarea.has-value ~ .n { left: auto; right: 12px; }
        .formB .area .sup { display: block; padding-inline: 4px; padding-block-start: 4px; font-size: small; opacity: 0.6; }
        .formB textarea { min-height: 120px; resize: vertical; }
        .formB button[type=submit] {
            padding: 14px 20px; border: none; background: var(--primary);
            color: #fff; font-weight: bold; border-radius: 8px; cursor: pointer;
            transition: background 0.3s, transform 0.2s; font-size: 1rem; width: 100%;
        }
        .formB button[type=submit]:hover { background: var(--primary-hover); transform: translateY(-2px); }
    </style>

    <script>
        function checkInput(element) {
            if (element.value.trim() !== "") {
                element.classList.add('has-value');
            } else {
                element.classList.remove('has-value');
            }
        }
    </script>
    """
    
    # استبدال النصوص المؤقتة بالترجمة الحقيقية بأمان تام
    html_content = html_content.replace("LANG_DIR", dir_val)\
                               .replace("P1_VAL", ct['p1'])\
                               .replace("P2_VAL", ct['p2'])\
                               .replace("P3_VAL", ct['p3'])\
                               .replace("P4_VAL", ct['p4'])\
                               .replace("NAME_VAL", ct['name'])\
                               .replace("EMAIL_VAL", ct['email'])\
                               .replace("ESUP_VAL", ct['email_sup'])\
                               .replace("MOB_VAL", ct['mobile'])\
                               .replace("MSUP_VAL", ct['mobile_sup'])\
                               .replace("MSG_VAL", ct['msg'])\
                               .replace("MSGSUP_VAL", ct['msg_sup'])\
                               .replace("SEND_VAL", ct['send'])

    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=html_content)





            
            
@app.route('/robots.txt')
def robots_txt():
    content = "User-agent: *\nAllow: /\nSitemap: https://www.actechup.online/sitemap.xml"
    return content, 200, {'Content-Type': 'text/plain'}

          
@app.route('/sitemap.xml')
def sitemap():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.actechup.online/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.actechup.online/contact</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://www.actechup.online/privacy</loc>
    <changefreq>yearly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://www.actechup.online/terms</loc>
    <changefreq>yearly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>"""
    return xml_content, 200, {'Content-Type': 'application/xml; charset=utf-8'}




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
