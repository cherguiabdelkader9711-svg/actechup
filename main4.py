import os
import glob
from flask import Flask, render_template_string, request, send_file
import yt_dlp

app = Flask(__name__)

# واجهة مستخدم احترافية مطابقة لهيكل SSSTik مع تصميم عصري وألوان خاصة
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحميل فيديو تيك توك بدون علامة مائية | AekDownloader</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background-color: #f8fafc; color: #0f172a; overflow-x: hidden; }
        a { text-decoration: none; color: inherit; }
        
        /* 1. النافذة العلوية (Navbar) */
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 15px 5%; background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .logo { font-size: 24px; font-weight: 800; color: #1e293b; display: flex; align-items: center; gap: 8px; }
        .logo span { color: #2563eb; }
        .nav-links { display: flex; gap: 20px; font-weight: 600; color: #475569; }
        .nav-links a:hover { color: #2563eb; }
        .install-btn { background: #2563eb; color: #fff; padding: 8px 20px; border-radius: 8px; font-weight: 600; transition: transform 0.3s, background 0.3s; }
        .install-btn:hover { background: #1d4ed8; transform: translateY(-2px); }

        /* 2. القسم الرئيسي (Hero Section) مع تأثيرات الماوس */
        .hero {
            background: linear-gradient(135deg, #1e3a8a, #0ea5e9);
            padding: 80px 20px;
            text-align: center;
            color: #fff;
            position: relative;
            overflow: hidden;
        }
        .hero h1 { font-size: 40px; font-weight: 800; margin-bottom: 30px; z-index: 2; position: relative; }
        
        /* شريط البحث الاحترافي */
        .search-box {
            max-width: 700px;
            margin: 0 auto;
            background: #fff;
            border-radius: 12px;
            display: flex;
            padding: 8px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            position: relative;
            z-index: 2;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .search-box:hover { transform: translateY(-3px); box-shadow: 0 20px 40px rgba(0,0,0,0.3); }
        .search-box input { flex: 1; border: none; padding: 15px 20px; font-size: 16px; outline: none; border-radius: 10px; background: transparent; color: #333; }
        .paste-btn { background: #f1f5f9; color: #475569; border: none; padding: 10px 20px; margin: 5px; border-radius: 8px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 5px; transition: 0.3s; }
        .paste-btn:hover { background: #e2e8f0; color: #0f172a; }
        .download-btn { background: #2563eb; color: #fff; border: none; padding: 15px 30px; font-size: 18px; font-weight: bold; border-radius: 10px; cursor: pointer; transition: 0.3s; }
        .download-btn:hover { background: #1e40af; }

        /* خيارات التحميل (راديو) */
        .format-options { margin-top: 25px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; position: relative; z-index: 2; }
        .radio-label { background: rgba(255,255,255,0.1); padding: 8px 15px; border-radius: 20px; cursor: pointer; font-size: 14px; font-weight: 600; backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.2); transition: 0.3s; }
        .radio-label:hover { background: rgba(255,255,255,0.2); }
        .radio-label input { accent-color: #0ea5e9; margin-left: 5px; }

        /* 3. المميزات الثلاث السريعة */
        .top-features { display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; padding: 60px 20px; background: #fff; text-align: center; }
        .feature-item h3 { font-size: 20px; color: #1e293b; margin-bottom: 10px; }
        .feature-item p { color: #64748b; font-size: 15px; max-width: 250px; }

        /* 4. قسم "كيفية التحميل" (صندوق الخطوات) */
        .how-to-section { padding: 40px 20px; text-align: center; background: #f8fafc; }
        .how-to-section h2 { font-size: 28px; color: #1e3a8a; margin-bottom: 30px; }
        .steps-box { max-width: 800px; margin: 0 auto; background: #1e3a8a; color: #fff; text-align: right; padding: 40px; border-radius: 24px; box-shadow: 0 20px 40px rgba(30,58,138,0.2); transition: transform 0.3s; }
        .steps-box:hover { transform: translateY(-5px); }
        .steps-box h3 { font-size: 24px; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; }
        .step { margin-bottom: 25px; position: relative; padding-right: 40px; }
        .step::before { content: attr(data-step); position: absolute; right: 0; top: -5px; font-size: 40px; font-weight: 900; color: rgba(255,255,255,0.1); line-height: 1; }
        .step h4 { font-size: 18px; margin-bottom: 8px; color: #38bdf8; }
        .step p { font-size: 15px; color: #cbd5e1; line-height: 1.6; }

        /* 5. شبكة المميزات (Grid) */
        .grid-features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; max-width: 1000px; margin: 60px auto; padding: 0 20px; text-align: center; }
        .grid-card { padding: 30px; background: #fff; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; transition: transform 0.3s, box-shadow 0.3s; }
        .grid-card:hover { transform: translateY(-10px); box-shadow: 0 15px 30px rgba(0,0,0,0.08); }
        .grid-card .icon { font-size: 40px; margin-bottom: 15px; }
        .grid-card p { color: #64748b; font-size: 15px; line-height: 1.6; }

        /* 6. قسم الأسئلة الشائعة (FAQ) */
        .faq-section { max-width: 800px; margin: 0 auto 80px auto; padding: 0 20px; }
        .faq-section h2 { text-align: center; font-size: 28px; color: #1e3a8a; margin-bottom: 40px; }
        details { background: #fff; margin-bottom: 15px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); overflow: hidden; border: 1px solid #e2e8f0; }
        summary { padding: 20px; font-weight: 600; cursor: pointer; color: #1e293b; font-size: 16px; outline: none; transition: background 0.3s; }
        summary:hover { background: #f8fafc; }
        details p { padding: 0 20px 20px 20px; color: #64748b; line-height: 1.7; font-size: 15px; }

        /* 7. الفوتر (الأسفل) */
        footer { background: #0f172a; color: #cbd5e1; text-align: center; padding: 40px 20px; font-size: 14px; }
        footer .footer-links { display: flex; justify-content: center; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
        footer .footer-links a:hover { color: #fff; text-decoration: underline; }
        footer p { margin-top: 10px; color: #94a3b8; }

        /* رسائل الخطأ */
        .alert { background: #fee2e2; color: #ef4444; text-align: center; padding: 15px; font-weight: 600; }

        /* التجاوب مع شاشات الهاتف */
        @media (max-width: 768px) {
            .nav-links { display: none; }
            .hero h1 { font-size: 28px; }
            .search-box { flex-direction: column; padding: 15px; gap: 10px; }
            .paste-btn, .download-btn { width: 100%; padding: 15px; }
            .top-features { flex-direction: column; gap: 30px; }
        }
    </style>
</head>
<body>

    <!-- التنبيهات -->
    {% if error %}
    <div class="alert">⚠️ {{ error }}</div>
    {% endif %}

    <!-- 1. النافذة العلوية -->
    <nav class="navbar">
        <div class="logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Aek<span>Downloader</span>
        </div>
        <div class="nav-links">
            <a href="#">تحميل الفيديوهات</a>
            <a href="#">تحميل ستوريات</a>
            <a href="#">تحميل MP3</a>
        </div>
        <a href="#" class="install-btn">تثبيت التطبيق</a>
    </nav>

    <!-- 2. القسم الرئيسي -->
    <section class="hero">
        <h1>أداة تحميل فيديوهات تيك توك</h1>
        
        <form method="POST" action="/download" id="downloadForm" onsubmit="handleDownloadState()">
            <div class="search-box">
                <input type="text" name="url" id="urlInput" placeholder="ألصق رابط الفيديو هنا..." required autocomplete="off">
                <button type="button" class="paste-btn" onclick="pasteFromClipboard()">
                    📋 لصق
                </button>
                <button type="submit" class="download-btn" id="dlBtn">تحميل</button>
            </div>

            <div class="format-options">
                <label class="radio-label">
                    <input type="radio" name="format_type" value="video" checked> فيديو (بدون علامة)
                </label>
                <label class="radio-label">
                    <input type="radio" name="format_type" value="mp3"> موسيقى (MP3)
                </label>
                <label class="radio-label">
                    <input type="radio" name="format_type" value="story"> ستوري / صور
                </label>
            </div>
        </form>
    </section>

    <!-- 3. المميزات السريعة -->
    <section class="top-features">
        <div class="feature-item">
            <h3>غير محدود</h3>
            <p>احفظ فيديوهات تيك توك بالعدد الذي تريده وبدون أي قيود يومية.</p>
        </div>
        <div class="feature-item">
            <h3>بدون علامة مائية!</h3>
            <p>حمل الفيديوهات بصيغة MP4 خالية تماماً من شعار تيك توك المزعج.</p>
        </div>
        <div class="feature-item">
            <h3>MP4 و MP3</h3>
            <p>احفظ الملفات بجودة عالية HD، أو قم بتحويلها إلى مقاطع صوتية MP3.</p>
        </div>
    </section>

    <!-- 4. صندوق الشرح -->
    <section class="how-to-section">
        <h2>كيفية التحميل من تيك توك؟</h2>
        <div class="steps-box">
            <h3>طريقة تحميل فيديو بدون علامة مائية:</h3>
            
            <div class="step" data-step="1">
                <h4>ابحث عن فيديو</h4>
                <p>افتح تطبيق تيك توك على هاتفك. تصفح للوصول إلى الفيديو الذي ترغب في حفظه. قم بتشغيل الفيديو للتأكد منه.</p>
            </div>
            
            <div class="step" data-step="2">
                <h4>انسخ الرابط</h4>
                <p>اضغط على زر "المشاركة" الموجود في الجانب الأيمن من الشاشة. اختر "نسخ الرابط" من القائمة.</p>
            </div>
            
            <div class="step" data-step="3">
                <h4>احفظ الفيديو</h4>
                <p>عد إلى موقعنا، الصق الرابط المنسوخ في شريط البحث بالأعلى، واضغط على زر "تحميل" لبدء الحفظ.</p>
            </div>
        </div>
    </section>

    <!-- 5. شبكة المميزات -->
    <section class="grid-features">
        <div class="grid-card">
            <div class="icon">🔗</div>
            <p>أداة التحميل لدينا هي الحل الأمثل لحفظ الفيديوهات لإعادة تحريرها ونشرها!</p>
        </div>
        <div class="grid-card">
            <div class="icon">🆓</div>
            <p>حمل الفيديوهات مجاناً بالكامل وبكميات غير محدودة.</p>
        </div>
        <div class="grid-card">
            <div class="icon">👤</div>
            <p>لا يتطلب تسجيل الدخول أو إدخال اسم مستخدم. فقط الصق الرابط.</p>
        </div>
        <div class="grid-card">
            <div class="icon">⚡</div>
            <p>سرعة تحميل فائقة وبأعلى جودة متوفرة (HD).</p>
        </div>
        <div class="grid-card">
            <div class="icon">🎵</div>
            <p>يدعم تنزيل الفيديوهات والصور (كمقاطع)، بالإضافة إلى استخراج الصوتيات.</p>
        </div>
        <div class="grid-card">
            <div class="icon">💻</div>
            <p>يعمل بكفاءة على جميع المتصفحات وأنظمة التشغيل (أندرويد، آيفون، حاسوب).</p>
        </div>
    </section>

    <!-- 6. الأسئلة الشائعة -->
    <section class="faq-section">
        <h2>الأسئلة الشائعة (FAQ)</h2>
        <details>
            <summary>هل يجب علي الدفع لاستخدام الخدمة؟</summary>
            <p>لا، هذه الخدمة مجانية تماماً وستبقى كذلك. يمكنك تحميل أي عدد تريده من الفيديوهات بدون أي رسوم.</p>
        </details>
        <details>
            <summary>أين يتم حفظ الفيديوهات بعد تحميلها؟</summary>
            <p>بشكل افتراضي، يتم حفظ الملفات في مجلد "التنزيلات" (Downloads) على جهازك، سواء كنت تستخدم هاتفاً أو حاسوباً.</p>
        </details>
        <details>
            <summary>هل يمكنني تحميل فيديوهات من حسابات خاصة؟</summary>
            <p>للأسف لا. نظامنا يعتمد على الوصول العام للفيديوهات. إذا كان الحساب خاصاً، لا يمكننا استخراج الفيديو منه.</p>
        </details>
        <details>
            <summary>هل أحتاج إلى تثبيت تطبيق أو إضافة؟</summary>
            <p>لا تحتاج لتثبيت أي شيء. كل ما تحتاجه هو متصفح الويب الخاص بك ورابط الفيديو لتعمل الأداة بنجاح.</p>
        </details>
    </section>

    <!-- 7. الفوتر -->
    <footer>
        <div class="footer-links">
            <a href="#">اتصل بنا</a>
            <a href="#">سياسة الخصوصية</a>
            <a href="#">شروط الاستخدام</a>
            <a href="#">تحميل من انستقرام</a>
        </div>
        <p>نحن غير تابعين لشركة TikTok أو ByteDance.</p>
        <p>تم الإنشاء بواسطة فريق AekDownloader - خبراء تحميل الفيديوهات.</p>
        <p>Copyright © 2024-2026</p>
    </footer>

    <!-- سكربتات التفاعل (اللصق + حالة الزر) -->
    <script>
        // دالة اللصق من الحافظة
        async function pasteFromClipboard() {
            try {
                const text = await navigator.clipboard.readText();
                document.getElementById('urlInput').value = text;
            } catch (err) {
                alert('يرجى السماح للمتصفح بالوصول إلى الحافظة، أو قم باللصق يدوياً.');
            }
        }

        // دالة تغيير حالة الزر وعودته لطبيعته بعد بدء التحميل
        function handleDownloadState() {
            const btn = document.getElementById('dlBtn');
            const input = document.getElementById('urlInput');
            
            // تغيير شكل الزر
            btn.innerHTML = 'جاري المعالجة... ⏳';
            btn.style.backgroundColor = '#64748b'; // لون رمادي مؤقت
            btn.style.pointerEvents = 'none'; // منع النقر المتكرر
            
            // إعادة الزر لشكله الطبيعي وتفريغ الخانة بعد 7 ثوانٍ
            // (7 ثوانٍ وقت كافٍ ليبدأ التحميل الفعلي في المتصفح)
            setTimeout(() => {
                btn.innerHTML = 'تحميل مجدداً';
                btn.style.backgroundColor = '#2563eb';
                btn.style.pointerEvents = 'auto';
                input.value = ''; // تفريغ الخانة لتحميل فيديو جديد
            }, 7000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download_video():
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        downloaded_files = glob.glob("downloaded_media*")
        if downloaded_files:
            final_file = downloaded_files[0]
            dl_name = f"AekDownloader_{format_type}{os.path.splitext(final_file)[1]}"
            return send_file(final_file, as_attachment=True, download_name=dl_name)
        else:
            raise Exception("لم يتم العثور على الملف.")
            
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error="❌ عذراً، تأكد من صحة الرابط أو أن الفيديو غير متاح للعامة.")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
