import os
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
# مفتاح سري لتشفير الجلسات وحفظ لغة المستخدم
app.secret_key = os.urandom(24)

# ==========================================
# 🌐 قاموس الترجمات (يسهل تعديله من هنا مباشرة)
# ==========================================
TRANSLATIONS = {
    'en': {
        'lang_name': 'English',
        'title': 'AekDownloader | Universal Tool',
        'nav_home': 'Home',
        'nav_contact': 'Contact Us',
        'nav_privacy': 'Privacy Policy',
        'nav_terms': 'Terms of Use',
        'hero_title': 'Universal Media Downloader',
        'hero_desc': 'Download your favorite content safely and securely from any platform.',
        'placeholder': 'Paste your link here...',
        'download': 'Download Now',
        'download_alert': 'Note: Backend download logic has been removed as per template settings.',
        'contact_name': 'Your Full Name',
        'contact_email': 'Your Email Address',
        'contact_msg': 'How can we help you?',
        'contact_send': 'Send Message',
        'privacy_text': 'We prioritize your privacy and security. We do not store, track, or share your personal data or download history. All operations are processed in real-time, and any links provided are immediately discarded from our servers after the operation is complete. By using our site, you consent to our basic data handling practices aimed solely at providing you with the best user experience.',
        'terms_text': 'By accessing this website, you agree to be bound by these Terms of Use. Our service is provided "as is" for personal, non-commercial use only. You agree not to use this service for downloading copyrighted material without the owner\'s permission. We reserve the right to modify or terminate the service at any time without prior notice.',
        'footer_text': '© 2026 AekDownloader. All rights reserved.'
    },
    'ar': {
        'lang_name': 'العربية',
        'title': 'أداة التحميل الشاملة | AekDownloader',
        'nav_home': 'الرئيسية',
        'nav_contact': 'اتصل بنا',
        'nav_privacy': 'سياسة الخصوصية',
        'nav_terms': 'شروط الاستخدام',
        'hero_title': 'أداة التحميل الشاملة للوسائط',
        'hero_desc': 'قم بتحميل محتواك المفضل بأمان وسرعة من أي منصة.',
        'placeholder': 'ألصق الرابط هنا...',
        'download': 'تحميل الآن',
        'download_alert': 'تنبيه: تمت إزالة المعالجة الخلفية للتحميل في هذا القالب كما طلبت.',
        'contact_name': 'الاسم الكامل',
        'contact_email': 'البريد الإلكتروني',
        'contact_msg': 'كيف يمكننا مساعدتك؟',
        'contact_send': 'إرسال الرسالة',
        'privacy_text': 'نحن نولي أولوية قصوى لخصوصيتك وأمانك. نحن لا نقوم بتخزين أو تتبع أو مشاركة بياناتك الشخصية أو سجل التحميلات. تتم جميع العمليات في الوقت الفعلي، ويتم التخلص من أي روابط مدخلة من سيرفراتنا فور اكتمال العملية.',
        'terms_text': 'بدخولك إلى هذا الموقع، فإنك توافق على الالتزام بشروط الاستخدام هذه. تُقدم خدمتنا "كما هي" للاستخدام الشخصي وغير التجاري فقط. أنت توافق على عدم استخدام هذه الخدمة لتحميل مواد محمية بحقوق الطبع والنشر دون إذن. نحتفظ بالحق في تعديل الخدمة أو إنهائها في أي وقت.',
        'footer_text': '© 2026 AekDownloader. جميع الحقوق محفوظة.'
    },
    'fr': {
        'lang_name': 'Français',
        'title': 'AekDownloader | Outil Universel',
        'nav_home': 'Accueil',
        'nav_contact': 'Contactez-nous',
        'nav_privacy': 'Confidentialité',
        'nav_terms': 'Conditions d\'utilisation',
        'hero_title': 'Téléchargeur de Médias Universel',
        'hero_desc': 'Téléchargez votre contenu préféré en toute sécurité.',
        'placeholder': 'Collez votre lien ici...',
        'download': 'Télécharger',
        'download_alert': 'Remarque : La logique de téléchargement a été supprimée.',
        'contact_name': 'Votre Nom',
        'contact_email': 'Votre Email',
        'contact_msg': 'Votre Message',
        'contact_send': 'Envoyer',
        'privacy_text': 'Nous accordons la priorité à votre vie privée. Nous ne stockons, ne suivons ni ne partageons vos données personnelles. Tous les processus sont effectués en temps réel.',
        'terms_text': 'Utilisez ce service de manière responsable. Ne téléchargez pas de matériel protégé par des droits d\'auteur sans autorisation.',
        'footer_text': '© 2026 AekDownloader. Tous droits réservés.'
    },
    'es': {
        'lang_name': 'Español',
        'title': 'AekDownloader | Herramienta Universal',
        'nav_home': 'Inicio',
        'nav_contact': 'Contáctenos',
        'nav_privacy': 'Privacidad',
        'nav_terms': 'Términos de Uso',
        'hero_title': 'Descargador de Medios Universal',
        'hero_desc': 'Descarga tu contenido favorito de forma segura.',
        'placeholder': 'Pega tu enlace aquí...',
        'download': 'Descargar Ahora',
        'download_alert': 'Nota: La lógica de descarga ha sido eliminada.',
        'contact_name': 'Su Nombre',
        'contact_email': 'Su Correo',
        'contact_msg': 'Su Mensaje',
        'contact_send': 'Enviar Mensaje',
        'privacy_text': 'Priorizamos su privacidad. No almacenamos, rastreamos ni compartimos sus datos personales. Todo se procesa en tiempo real.',
        'terms_text': 'Utilice este servicio con responsabilidad. No descargue materiales protegidos por derechos de autor sin permiso.',
        'footer_text': '© 2026 AekDownloader. Todos los derechos reservados.'
    },
    'ru': {
        'lang_name': 'Русский',
        'title': 'AekDownloader | Универсальный инструмент',
        'nav_home': 'Главная',
        'nav_contact': 'Контакты',
        'nav_privacy': 'Конфиденциальность',
        'nav_terms': 'Условия',
        'hero_title': 'Универсальный загрузчик медиа',
        'hero_desc': 'Скачивайте любимый контент безопасно и быстро.',
        'placeholder': 'Вставьте ссылку здесь...',
        'download': 'Скачать',
        'download_alert': 'Примечание: Логика загрузки была удалена.',
        'contact_name': 'Ваше имя',
        'contact_email': 'Ваш Email',
        'contact_msg': 'Ваше сообщение',
        'contact_send': 'Отправить',
        'privacy_text': 'Мы не храним, не отслеживаем и не передаем ваши личные данные. Все операции выполняются в режиме реального времени.',
        'terms_text': 'Используйте этот сервис ответственно. Не скачивайте материалы, защищенные авторским правом.',
        'footer_text': '© 2026 AekDownloader. Все права защищены.'
    },
    'zh': {
        'lang_name': '中文',
        'title': 'AekDownloader | 通用工具',
        'nav_home': '首页',
        'nav_contact': '联系我们',
        'nav_privacy': '隐私政策',
        'nav_terms': '使用条款',
        'hero_title': '通用媒体下载器',
        'hero_desc': '安全、快速地下载您喜爱的内容。',
        'placeholder': '在此粘贴链接...',
        'download': '立即下载',
        'download_alert': '注意：下载后端逻辑已被移除。',
        'contact_name': '您的姓名',
        'contact_email': '您的邮箱',
        'contact_msg': '您的留言',
        'contact_send': '发送',
        'privacy_text': '我们重视您的隐私。我们不存储、跟踪或分享您的个人数据。所有处理均实时完成。',
        'terms_text': '请负责任地使用此服务。未经许可，请勿下载受版权保护的材料。',
        'footer_text': '© 2026 AekDownloader. 保留所有权利。'
    },
    'ja': {
        'lang_name': '日本語',
        'title': 'AekDownloader | ユニバーサルツール',
        'nav_home': 'ホーム',
        'nav_contact': 'お問い合わせ',
        'nav_privacy': 'プライバシー',
        'nav_terms': '利用規約',
        'hero_title': 'ユニバーサルメディアダウンローダー',
        'hero_desc': 'お気に入りのコンテンツを安全にダウンロード。',
        'placeholder': 'ここにリンクを貼り付けてください...',
        'download': 'ダウンロード',
        'download_alert': '注：ダウンロードロジックは削除されました。',
        'contact_name': 'お名前',
        'contact_email': 'メールアドレス',
        'contact_msg': 'メッセージ',
        'contact_send': '送信',
        'privacy_text': '当社はお客様のデータを保存、追跡、共有しません。すべての処理はリアルタイムで行われます。',
        'terms_text': 'このサービスは責任を持って使用してください。著作権で保護された素材をダウンロードしないでください。',
        'footer_text': '© 2026 AekDownloader. 無断複写・転載を禁じます。'
    }
}

# دالة ذكية لجلب لغة الجلسة الحالية
def get_t():
    lang = session.get('lang', 'en')
    if lang not in TRANSLATIONS:
        lang = 'en'
    return TRANSLATIONS[lang], lang

# ==========================================
# 🎨 القالب الأساسي (يحتوي على الهيدر والفوتر والستايل)
# ==========================================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ 'rtl' if lang == 'ar' else 'ltr' }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t['title'] }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #f8fafc;
            --text: #0f172a;
            --box-bg: #ffffff;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; }
        body { background: var(--bg); color: var(--text); display: flex; flex-direction: column; min-height: 100vh; }
        
        /* شريط التنقل العلوي */
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 15px 5%; background: var(--box-bg); box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .logo { font-size: 24px; font-weight: 800; color: #1e293b; text-decoration: none; }
        .logo span { color: var(--primary); }
        .nav-links { display: flex; gap: 25px; align-items: center; }
        .nav-links a { text-decoration: none; font-weight: 600; color: #475569; transition: 0.3s; }
        .nav-links a:hover { color: var(--primary); }
        
        /* القائمة المنسدلة للغات (لوجو احترافي) */
        .lang-menu { position: relative; display: inline-block; }
        .lang-btn { background: #f1f5f9; border: none; padding: 10px 15px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 14px; color: #1e293b; transition: 0.3s; }
        .lang-btn:hover { background: #e2e8f0; }
        .lang-dropdown { display: none; position: absolute; top: 110%; right: 0; background: #fff; min-width: 150px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden; z-index: 100; }
        [dir="rtl"] .lang-dropdown { right: auto; left: 0; } /* ضبط الاتجاه للعربية */
        .lang-menu:hover .lang-dropdown { display: block; }
        .lang-dropdown a { display: block; padding: 12px 20px; color: #334155; text-decoration: none; border-bottom: 1px solid #f1f5f9; transition: 0.3s; font-weight: 600; }
        .lang-dropdown a:hover { background: var(--primary); color: #fff; }
        
        /* المحتوى المتغير */
        .main-content { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 60px 20px; }
        
        /* تصميم الصفحات الداخلية (اتصل بنا، الخصوصية) */
        .page-box { background: var(--box-bg); padding: 40px; border-radius: 16px; width: 100%; max-width: 700px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); line-height: 1.8; }
        .page-box h2 { color: var(--primary); margin-bottom: 20px; font-size: 28px; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; }
        .page-box p { color: #475569; font-size: 16px; }
        
        /* تصميم النماذج (Forms) */
        .custom-form { display: flex; flex-direction: column; gap: 15px; }
        .custom-form input, .custom-form textarea { width: 100%; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; font-size: 15px; outline: none; background: #f8fafc; transition: 0.3s; }
        .custom-form input:focus, .custom-form textarea:focus { border-color: var(--primary); background: #fff; }
        .custom-form button { background: var(--primary); color: #fff; border: none; padding: 15px; font-size: 16px; font-weight: bold; border-radius: 10px; cursor: pointer; transition: 0.3s; }
        .custom-form button:hover { background: var(--primary-hover); }

        /* الفوتر */
        footer { background: #0f172a; color: #cbd5e1; text-align: center; padding: 40px 20px; font-size: 15px; margin-top: auto; }
        footer a { color: #cbd5e1; text-decoration: none; margin: 0 15px; font-weight: 600; transition: 0.3s; }
        footer a:hover { color: #fff; text-decoration: underline; }
        footer p { margin-top: 15px; color: #94a3b8; }
        
        /* التجاوب مع الهواتف */
        @media (max-width: 600px) {
            .nav-links { gap: 10px; font-size: 14px; }
            .lang-btn span { display: none; } /* إخفاء النص وترك الأيقونة في الجوال */
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">Aek<span>Downloader</span></a>
        
        <div class="nav-links">
            <a href="/">{{ t['nav_home'] }}</a>
            <a href="/contact">{{ t['nav_contact'] }}</a>
            
            <!-- لوجو اللغات المتطور -->
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

    <main class="main-content">
        {{ content|safe }}
    </main>

    <footer>
        <div>
            <a href="/privacy">{{ t['nav_privacy'] }}</a>
            <a href="/terms">{{ t['nav_terms'] }}</a>
        </div>
        <p>{{ t['footer_text'] }}</p>
    </footer>
</body>
</html>
"""

# ==========================================
# 📄 محتوى الصفحات الداخلية المستقلة
# ==========================================

# 1. الصفحة الرئيسية (البحث)
HOME_HTML = """
<div style="text-align: center; width: 100%; max-width: 800px; margin-top: 20px;">
    <h1 style="font-size: 42px; color: #1e293b; margin-bottom: 15px; font-weight: 800;">{{ t['hero_title'] }}</h1>
    <p style="color: #64748b; font-size: 18px; margin-bottom: 40px;">{{ t['hero_desc'] }}</p>
    
    <form style="display: flex; background: #fff; border-radius: 12px; padding: 10px; box-shadow: 0 15px 30px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; max-width: 650px; margin: 0 auto;" onsubmit="event.preventDefault(); alert('{{ t['download_alert'] }}');">
        <input type="text" placeholder="{{ t['placeholder'] }}" required style="flex: 1; border: none; padding: 15px; outline: none; font-size: 16px; background: transparent;">
        <button type="submit" style="background: #2563eb; color: #fff; border: none; padding: 10px 30px; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer;">{{ t['download'] }}</button>
    </form>
</div>
"""

# 2. صفحة اتصل بنا
CONTACT_HTML = """
<div class="page-box">
    <h2>{{ t['nav_contact'] }}</h2>
    <form class="custom-form" onsubmit="event.preventDefault(); alert('تم إرسال رسالتك بنجاح! / Message Sent!');">
        <input type="text" placeholder="{{ t['contact_name'] }}" required>
        <input type="email" placeholder="{{ t['contact_email'] }}" required>
        <textarea rows="6" placeholder="{{ t['contact_msg'] }}" required></textarea>
        <button type="submit">{{ t['contact_send'] }}</button>
    </form>
</div>
"""

# 3. صفحة سياسة الخصوصية
PRIVACY_HTML = """
<div class="page-box">
    <h2>{{ t['nav_privacy'] }}</h2>
    <p>{{ t['privacy_text'] }}</p>
</div>
"""

# 4. صفحة شروط الاستخدام
TERMS_HTML = """
<div class="page-box">
    <h2>{{ t['nav_terms'] }}</h2>
    <p>{{ t['terms_text'] }}</p>
</div>
"""

# ==========================================
# 🚦 مسارات الموقع (Routes)
# ==========================================

# مسار لتغيير اللغة وحفظها في الذاكرة
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

@app.route('/contact')
def contact():
    t, lang = get_t()
    content = render_template_string(CONTACT_HTML, t=t)
    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content)

@app.route('/privacy')
def privacy():
    t, lang = get_t()
    content = render_template_string(PRIVACY_HTML, t=t)
    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content)

@app.route('/terms')
def terms():
    t, lang = get_t()
    content = render_template_string(TERMS_HTML, t=t)
    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
