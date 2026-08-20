import os
import glob
from flask import Flask, render_template_string, request, session, redirect, url_for, send_file
import yt_dlp

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ==========================================
# 🌐 قاموس الترجمات (يشمل كل الأقسام الجديدة)
# ==========================================
TRANSLATIONS = {
    'en': {
        'lang_name': 'English',
        'title': 'AekDownloader | TikTok Downloader',
        'nav_home': 'Home',
        'nav_contact': 'Contact Us',
        'nav_privacy': 'Privacy Policy',
        'nav_terms': 'Terms of Use',
        'hero_title': 'Universal Media Downloader',
        'hero_desc': 'Download TikTok videos, stories, and audio quickly and safely.',
        'placeholder': 'Paste your link here...',
        'paste': 'Paste',
        'download': 'Download',
        'opt_video': 'Video (MP4)',
        'opt_audio': 'Audio (MP3)',
        'opt_story': 'Story',
        'opt_photo': 'Photos',
        'feat_title': 'Why Choose Us?',
        'f1_title': 'No Watermark',
        'f1_desc': 'Download videos in crystal clear HD without any logos.',
        'f2_title': 'Unlimited & Free',
        'f2_desc': 'Save as many videos as you want without any restrictions.',
        'f3_title': 'Multiple Formats',
        'f3_desc': 'Extract high-quality MP3 audio or download image slideshows.',
        'how_title': 'How to download?',
        'step1_t': '1. Copy the Link',
        'step1_d': 'Open the app, find the video, tap Share, and select "Copy Link".',
        'step2_t': '2. Paste it here',
        'step2_d': 'Come back to this page, paste the link in the input field above.',
        'step3_t': '3. Download',
        'step3_d': 'Choose your format (MP4/MP3) and click Download to save it.',
        'faq_title': 'Frequently Asked Questions',
        'q1': 'Are the downloaded files safe?',
        'a1': 'Absolutely. We do not require any software installation, and all files are processed directly from the official servers ensuring 100% safety.',
        'q2': 'Where are the files saved on my phone?',
        'a2': 'By default, all downloaded files (videos or audio) are saved in your device\'s "Downloads" folder or your gallery.',
        'q3': 'Can I download private videos?',
        'a3': 'No. Our tool respects user privacy. We can only process videos that are publicly available.',
        'contact_name': 'Full Name',
        'contact_email': 'Email Address',
        'contact_msg': 'Your Message',
        'contact_send': 'Send Message',
        'footer_text': '© 2026 AekDownloader. All rights reserved.'
    },
    'ar': {
        'lang_name': 'العربية',
        'title': 'AekDownloader | تحميل تيك توك',
        'nav_home': 'الرئيسية',
        'nav_contact': 'اتصل بنا',
        'nav_privacy': 'سياسة الخصوصية',
        'nav_terms': 'شروط الاستخدام',
        'hero_title': 'أداة التحميل الشاملة للوسائط',
        'hero_desc': 'قم بتحميل فيديوهات تيك توك، الستوريات، والصوتيات بأمان وسرعة.',
        'placeholder': 'ألصق الرابط هنا...',
        'paste': 'لصق 📋',
        'download': 'تحميل الآن',
        'opt_video': 'فيديو (MP4)',
        'opt_audio': 'صوت (MP3)',
        'opt_story': 'ستوري',
        'opt_photo': 'صور',
        'feat_title': 'لماذا تختار منصتنا؟',
        'f1_title': 'بدون علامة مائية',
        'f1_desc': 'احصل على الفيديوهات بجودة HD الأصلية خالية تماماً من أي شعار.',
        'f2_title': 'مجاني وغير محدود',
        'f2_desc': 'لا توجد قيود على عدد التحميلات اليومية، حمل ما تشاء مجاناً.',
        'f3_title': 'صيغ متعددة',
        'f3_desc': 'استخرج الصوتيات (MP3) بوضوح، أو حمل الصور كفيديو مدمج.',
        'how_title': 'كيفية التحميل؟',
        'step1_t': '1. انسخ الرابط',
        'step1_d': 'افتح التطبيق، ابحث عن المقطع، اضغط على سهم المشاركة ثم "نسخ الرابط".',
        'step2_t': '2. ألصق الرابط',
        'step2_d': 'عد إلى موقعنا، وقم بلصق الرابط في المربع المخصص بالأعلى.',
        'step3_t': '3. اضغط تحميل',
        'step3_d': 'اختر الصيغة المناسبة (فيديو أو صوت) واضغط على زر التحميل.',
        'faq_title': 'الأسئلة الشائعة (FAQ)',
        'q1': 'هل الملفات المحملة آمنة على هاتفي؟',
        'a1': 'بكل تأكيد. منصتنا لا تتطلب تثبيت أي برامج خارجية، ويتم جلب الملفات مباشرة من السيرفرات الرسمية بصيغتها الأصلية والآمنة 100%.',
        'q2': 'أين أجد الفيديوهات بعد تحميلها؟',
        'a2': 'بشكل افتراضي، يتم حفظ جميع المقاطع والصوتيات في مجلد "التنزيلات" (Downloads) في مدير الملفات بهاتفك، أو مباشرة في الاستوديو.',
        'q3': 'هل يمكنني تحميل مقطع من حساب "خاص" (Private)؟',
        'a3': 'للأسف لا. نظامنا يحترم خصوصية المستخدمين ولا يمكنه سحب البيانات إلا من الحسابات العامة (Public) المتاحة للجميع.',
        'contact_name': 'الاسم الكامل',
        'contact_email': 'البريد الإلكتروني',
        'contact_msg': 'رسالتك...',
        'contact_send': 'إرسال',
        'footer_text': '© 2026 AekDownloader. جميع الحقوق محفوظة.'
    }
}

# (لتبسيط الكود وحمايته من التقطيع، تم إضافة اللغتين الأساسيتين فقط هنا، يمكنك إضافة الباقي بسهولة بنسخ نفس الهيكل)

def get_t():
    lang = session.get('lang', 'ar') # جعلنا العربية هي الافتراضية
    if lang not in TRANSLATIONS:
        lang = 'ar'
    return TRANSLATIONS[lang], lang

# ==========================================
# 🎨 القالب الأساسي (BASE)
# ==========================================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ 'rtl' if lang == 'ar' else 'ltr' }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t['title'] }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1e40af;
            --bg: #f8fafc;
            --text: #0f172a;
            --box-bg: #ffffff;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; }
        body { background: var(--bg); color: var(--text); display: flex; flex-direction: column; min-height: 100vh; overflow-x: hidden; }
        
        /* Navbar */
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 15px 5%; background: var(--box-bg); box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: relative; z-index: 10; }
        .logo { font-size: 24px; font-weight: 900; color: #1e293b; text-decoration: none; letter-spacing: -0.5px; }
        .logo span { color: var(--primary); }
        .nav-links { display: flex; gap: 25px; align-items: center; }
        .nav-links a { text-decoration: none; font-weight: 600; color: #475569; transition: 0.3s; }
        .nav-links a:hover { color: var(--primary); }
        
        /* Language Dropdown */
        .lang-menu { position: relative; display: inline-block; }
        .lang-btn { background: #f1f5f9; border: none; padding: 8px 15px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; color: #1e293b; }
        .lang-dropdown { display: none; position: absolute; top: 110%; right: 0; background: #fff; min-width: 120px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-radius: 12px; overflow: hidden; }
        [dir="rtl"] .lang-dropdown { right: auto; left: 0; }
        .lang-menu:hover .lang-dropdown { display: block; }
        .lang-dropdown a { display: block; padding: 10px 15px; color: #334155; text-decoration: none; border-bottom: 1px solid #f8fafc; font-weight: 600; }
        .lang-dropdown a:hover { background: var(--primary); color: #fff; }

        /* Main Content */
        .main-content { flex: 1; display: flex; flex-direction: column; align-items: center; }
        
        /* Error Alert */
        .alert-error { background: #fee2e2; color: #dc2626; padding: 15px; text-align: center; font-weight: bold; width: 100%; border-bottom: 1px solid #f87171; }
        
        /* Footer */
        footer { background: #0f172a; color: #cbd5e1; text-align: center; padding: 40px 20px; margin-top: auto; }
        footer a { color: #cbd5e1; text-decoration: none; margin: 0 15px; font-weight: 600; }
        footer a:hover { color: #fff; }
        footer p { margin-top: 20px; color: #64748b; font-size: 14px; }

        @media (max-width: 768px) {
            .nav-links { gap: 12px; font-size: 14px; }
            .lang-btn span { display: none; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">Aek<span>Downloader</span></a>
        
        <div class="nav-links">
            <a href="/">{{ t['nav_home'] }}</a>
            <a href="/contact">{{ t['nav_contact'] }}</a>
            
            <div class="lang-menu">
                <button class="lang-btn">🌐 <span>{{ t['lang_name'] }}</span></button>
                <div class="lang-dropdown">
                    <a href="/set_lang/en">English</a>
                    <a href="/set_lang/ar">العربية</a>
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
        <div>
            <a href="/privacy">{{ t['nav_privacy'] }}</a>
            <a href="/terms">{{ t['nav_terms'] }}</a>
        </div>
        <p>{{ t['footer_text'] }}</p>
    </footer>

    <script>
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
            btn.style.opacity = '0.8';
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
# 📄 محتوى الصفحة الرئيسية (مع الشرح والأسئلة الشائعة)
# ==========================================
HOME_HTML = """
<style>
    .hero { text-align: center; padding: 60px 20px 40px; width: 100%; }
    .hero h1 { font-size: 38px; color: #1e293b; font-weight: 900; margin-bottom: 15px; }
    .hero p { color: #64748b; font-size: 18px; margin-bottom: 40px; }
    
    .search-container { max-width: 700px; margin: 0 auto; background: #fff; padding: 10px; border-radius: 16px; box-shadow: 0 20px 40px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; display: flex; gap: 8px; flex-wrap: wrap; }
    .search-container input { flex: 1; min-width: 250px; border: none; padding: 15px 20px; font-size: 16px; outline: none; background: #f8fafc; border-radius: 10px; }
    .btn-paste { background: transparent; color: #475569; border: 2px solid #e2e8f0; padding: 0 15px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.3s; }
    .btn-paste:hover { background: #f1f5f9; }
    .btn-dl { background: var(--primary); color: #fff; border: none; padding: 15px 30px; font-size: 16px; font-weight: bold; border-radius: 10px; cursor: pointer; transition: 0.3s; }
    .btn-dl:hover { background: var(--primary-hover); }

    /* خيارات التحميل أسفل الصندوق */
    .options-row { display: flex; justify-content: center; gap: 20px; margin-top: 25px; flex-wrap: wrap; }
    .opt-radio { display: flex; align-items: center; gap: 5px; cursor: pointer; font-weight: 600; color: #475569; padding: 8px 15px; border-radius: 20px; background: #fff; border: 1px solid #e2e8f0; transition: 0.3s; }
    .opt-radio:hover { border-color: var(--primary); background: #eff6ff; color: var(--primary); }
    .opt-radio input { accent-color: var(--primary); transform: scale(1.1); }

    /* الأقسام الإضافية */
    .section-wrap { width: 100%; padding: 60px 20px; display: flex; flex-direction: column; align-items: center; }
    .bg-light { background: #fff; }
    .sec-title { font-size: 32px; color: #1e293b; margin-bottom: 40px; font-weight: 800; text-align: center; }

    /* المميزات */
    .features-grid { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; max-width: 1000px; }
    .f-card { background: #f8fafc; padding: 30px; border-radius: 16px; width: 300px; text-align: center; border: 1px solid #e2e8f0; transition: 0.3s; }
    .f-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-color: var(--primary); }
    .f-card h3 { color: var(--primary); margin-bottom: 15px; font-size: 20px; }
    .f-card p { color: #64748b; font-size: 15px; line-height: 1.6; }

    /* الشرح */
    .how-box { background: #1e3a8a; color: #fff; padding: 40px; border-radius: 24px; max-width: 800px; width: 100%; box-shadow: 0 20px 40px rgba(30,58,138,0.2); }
    .step { position: relative; padding: 0 40px; margin-bottom: 30px; }
    [dir="ltr"] .step { padding: 0 0 0 40px; }
    .step::before { content: "✓"; position: absolute; right: 0; top: 0; color: #38bdf8; font-size: 24px; font-weight: bold; }
    [dir="ltr"] .step::before { right: auto; left: 0; }
    .step h4 { font-size: 18px; margin-bottom: 5px; color: #fff; }
    .step p { color: #94a3b8; font-size: 15px; }

    /* الأسئلة الشائعة */
    .faq-container { max-width: 800px; width: 100%; }
    details { background: #f8fafc; margin-bottom: 15px; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }
    summary { padding: 20px; font-weight: 700; cursor: pointer; color: #1e293b; font-size: 16px; list-style: none; display: flex; justify-content: space-between; align-items: center; }
    summary::-webkit-details-marker { display: none; }
    summary::after { content: "+"; color: var(--primary); font-size: 20px; }
    details[open] summary::after { content: "-"; }
    details p { padding: 0 20px 20px 20px; color: #475569; line-height: 1.7; font-size: 15px; }
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
            <label class="opt-radio">
                <input type="radio" name="format_type" value="video" checked> {{ t['opt_video'] }}
            </label>
            <label class="opt-radio">
                <input type="radio" name="format_type" value="mp3"> {{ t['opt_audio'] }}
            </label>
            <label class="opt-radio">
                <input type="radio" name="format_type" value="story"> {{ t['opt_story'] }}
            </label>
            <label class="opt-radio">
                <input type="radio" name="format_type" value="photo"> {{ t['opt_photo'] }}
            </label>
        </div>
    </form>
</div>

<!-- قسم المميزات -->
<div class="section-wrap bg-light">
    <h2 class="sec-title">{{ t['feat_title'] }}</h2>
    <div class="features-grid">
        <div class="f-card">
            <h3>{{ t['f1_title'] }}</h3>
            <p>{{ t['f1_desc'] }}</p>
        </div>
        <div class="f-card">
            <h3>{{ t['f2_title'] }}</h3>
            <p>{{ t['f2_desc'] }}</p>
        </div>
        <div class="f-card">
            <h3>{{ t['f3_title'] }}</h3>
            <p>{{ t['f3_desc'] }}</p>
        </div>
    </div>
</div>

<!-- قسم كيفية التحميل -->
<div class="section-wrap">
    <h2 class="sec-title">{{ t['how_title'] }}</h2>
    <div class="how-box">
        <div class="step">
            <h4>{{ t['step1_t'] }}</h4>
            <p>{{ t['step1_d'] }}</p>
        </div>
        <div class="step">
            <h4>{{ t['step2_t'] }}</h4>
            <p>{{ t['step2_d'] }}</p>
        </div>
        <div class="step">
            <h4>{{ t['step3_t'] }}</h4>
            <p>{{ t['step3_d'] }}</p>
        </div>
    </div>
</div>

<!-- قسم الأسئلة الشائعة -->
<div class="section-wrap bg-light">
    <h2 class="sec-title">{{ t['faq_title'] }}</h2>
    <div class="faq-container">
        <details>
            <summary>{{ t['q1'] }}</summary>
            <p>{{ t['a1'] }}</p>
        </details>
        <details>
            <summary>{{ t['q2'] }}</summary>
            <p>{{ t['a2'] }}</p>
        </details>
        <details>
            <summary>{{ t['q3'] }}</summary>
            <p>{{ t['a3'] }}</p>
        </details>
    </div>
</div>
"""

# ==========================================
# 🚦 مسارات الموقع (Routes) + منطق التحميل
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

@app.route('/contact')
def contact():
    t, lang = get_t()
    content = f"""
    <div style="max-width: 600px; margin: 40px auto; background: #fff; padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.05);">
        <h2 style="color: #1e293b; margin-bottom: 20px;">{t['nav_contact']}</h2>
        <form style="display: flex; flex-direction: column; gap: 15px;">
            <input type="text" placeholder="{t['contact_name']}" style="padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; background: #f8fafc;" required>
            <input type="email" placeholder="{t['contact_email']}" style="padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; background: #f8fafc;" required>
            <textarea rows="5" placeholder="{t['contact_msg']}" style="padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; background: #f8fafc;" required></textarea>
            <button type="button" onclick="alert('Sent!')" style="background: #2563eb; color: #fff; border: none; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer;">{t['contact_send']}</button>
        </form>
    </div>
    """
    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content)

@app.route('/privacy')
def privacy():
    t, lang = get_t()
    content = f'<div style="max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.8; color: #475569;"><h2>{t["nav_privacy"]}</h2><p>نحن نحترم خصوصيتك بالكامل. جميع عمليات التحميل تتم بشكل لحظي ولا نقوم بتخزين أي بيانات شخصية أو مقاطع تم تنزيلها على سيرفراتنا.</p></div>'
    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content)

@app.route('/terms')
def terms():
    t, lang = get_t()
    content = f'<div style="max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.8; color: #475569;"><h2>{t["nav_terms"]}</h2><p>باستخدامك لهذه المنصة، فإنك توافق على استخدامها للأغراض الشخصية فقط وعدم انتهاك حقوق الطبع والنشر الخاصة بصناع المحتوى.</p></div>'
    return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content)

# منطق التحميل الفعلي (yt-dlp)
@app.route('/download', methods=['POST'])
def download_video():
    t, lang = get_t()
    url = request.form.get('url')
    format_type = request.form.get('format_type', 'video')
    
    # تنظيف السيرفر من الملفات القديمة
    for file in glob.glob("downloaded_media*"):
        try:
            os.remove(file)
        except:
            pass

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        if format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': 'downloaded_media', 
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'best',
                'outtmpl': 'downloaded_media.%(ext)s',
            })

        # بدء التحميل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        downloaded_files = glob.glob("downloaded_media*")
        if downloaded_files:
            final_file = downloaded_files[0]
            ext = os.path.splitext(final_file)[1]
            dl_name = f"AekDownloader_{format_type}{ext}"
            return send_file(final_file, as_attachment=True, download_name=dl_name)
        else:
            raise Exception("File not found")
            
    except Exception as e:
        content = render_template_string(HOME_HTML, t=t)
        error_msg = "❌ عذراً، تأكد من صحة الرابط أو أن المقطع متاح للعامة." if lang == 'ar' else "❌ Error: Please check the link or ensure the video is public."
        return render_template_string(BASE_TEMPLATE, t=t, lang=lang, content=content, error=error_msg)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
