import os
import glob
from flask import Flask, render_template_string, request, send_file
import yt_dlp

app = Flask(__name__)

# قالب HTML متطور بتصميم عصري ووضع ليلي/نهاري
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AekDownloader - تيك توك</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --text-color: #f8fafc;
            --box-bg: #1e293b;
            --primary: #38bdf8;
            --primary-hover: #0ea5e9;
            --border: #334155;
        }
        [data-theme="light"] {
            --bg-color: #f1f5f9;
            --text-color: #0f172a;
            --box-bg: #ffffff;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --border: #e2e8f0;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; transition: background 0.3s, color 0.3s; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg-color); color: var(--text-color); display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 20px; }
        
        /* الهيدر وزر الوضع الليلي */
        .header { width: 100%; max-width: 600px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; margin-top: 20px; }
        .logo { font-size: 28px; font-weight: bold; }
        .logo span { color: var(--primary); }
        .theme-toggle { background: transparent; border: 2px solid var(--primary); color: var(--text-color); padding: 8px 15px; border-radius: 20px; cursor: pointer; font-weight: bold; }
        
        /* صندوق التحميل */
        .container { background: var(--box-bg); padding: 40px 30px; border-radius: 16px; width: 100%; max-width: 600px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 1px solid var(--border); text-align: center; }
        h2 { margin-bottom: 25px; font-size: 22px; }
        input[type="text"] { width: 100%; padding: 15px; border-radius: 10px; border: 1px solid var(--border); background: var(--bg-color); color: var(--text-color); margin-bottom: 20px; font-size: 16px; outline: none; }
        input[type="text"]:focus { border-color: var(--primary); }
        
        /* خيارات التحميل */
        .options { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; margin-bottom: 25px; }
        .radio-label { display: flex; align-items: center; gap: 5px; cursor: pointer; font-size: 15px; }
        .radio-label input[type="radio"] { accent-color: var(--primary); transform: scale(1.2); }
        
        button[type="submit"] { width: 100%; background: var(--primary); color: #fff; border: none; padding: 15px; font-size: 18px; font-weight: bold; border-radius: 10px; cursor: pointer; }
        button[type="submit"]:hover { background: var(--primary-hover); transform: translateY(-2px); }
        
        /* معلومات الموقع */
        .about-section { margin-top: 40px; background: var(--box-bg); padding: 25px; border-radius: 16px; width: 100%; max-width: 600px; border: 1px solid var(--border); line-height: 1.6; }
        .about-section h3 { color: var(--primary); margin-bottom: 10px; }
        
        .message { margin-top: 15px; padding: 10px; border-radius: 8px; }
        .error { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
        .info { color: #8b5cf6; font-size: 14px; margin-top: 10px; display: block; }
    </style>
</head>
<body>

    <div class="header">
        <div class="logo">Aek<span>Downloader</span></div>
        <button class="theme-toggle" onclick="toggleTheme()">☀️ نهاري</button>
    </div>

    <div class="container">
        <h2>تحميل من تيك توك بدون علامات مائية</h2>
        <form method="POST" action="/download">
            <input type="text" name="url" placeholder="ألصق رابط الفيديو، الستوري، أو الصور هنا..." required autocomplete="off">
            
            <div class="options">
                <label class="radio-label">
                    <input type="radio" name="format_type" value="video" checked> فيديو (MP4)
                </label>
                <label class="radio-label">
                    <input type="radio" name="format_type" value="mp3"> صوت فقط (MP3)
                </label>
                <label class="radio-label">
                    <input type="radio" name="format_type" value="story"> ستوري
                </label>
                <label class="radio-label">
                    <input type="radio" name="format_type" value="photo"> صور (تُحفظ كفيديو)
                </label>
            </div>

            <button type="submit" onclick="this.innerHTML='جاري التحميل... ⏳';">بدء التحميل</button>
        </form>
        
        {% if error %}
            <div class="message error">{{ error }}</div>
        {% endif %}
    </div>

    <div class="about-section">
        <h3>معلومات عن المنصة ℹ️</h3>
        <p>مرحباً بك في منصة <strong>Aek Tech</strong> لتحميل الوسائط. تم تصميم هذه الأداة لتكون الأسرع والأكثر أماناً لتحميل محتوى تيك توك.</p>
        <ul style="margin-top: 10px; padding-right: 20px; color: #64748b;">
            <li>✨ تحميل الفيديوهات بجودة أصلية بدون علامة مائية.</li>
            <li>🎵 استخراج الصوت (MP3) من أي مقطع بسهولة.</li>
            <li>📸 دعم تحميل الستوريات وصور السلايد شو (كمقاطع فيديو).</li>
            <li>🔒 أمان تام: لا نحتفظ بأي ملفات أو بيانات خاصة بك على سيرفراتنا.</li>
        </ul>
    </div>

    <script>
        // سكربت حفظ وتغيير الوضع الليلي/النهاري
        const themeToggleBtn = document.querySelector('.theme-toggle');
        const currentTheme = localStorage.getItem('theme') || 'dark';
        
        if (currentTheme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
            themeToggleBtn.innerHTML = '🌙 ليلي';
        }

        function toggleTheme() {
            let theme = document.documentElement.getAttribute('data-theme');
            if (theme === 'light') {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'dark');
                themeToggleBtn.innerHTML = '☀️ نهاري';
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                themeToggleBtn.innerHTML = '🌙 ليلي';
            }
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
    
    # تنظيف السيرفر من الملفات القديمة قبل بدء تحميل جديد
    for file in glob.glob("downloaded_media*"):
        try:
            os.remove(file)
        except:
            pass

    # الإعدادات الأساسية
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        if format_type == 'mp3':
            # إعدادات سحب الصوت فقط (تتطلب وجود FFmpeg على السيرفر)
            ydl_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': 'downloaded_media', 
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
            expected_ext = '.mp3'
        else:
            # إعدادات الفيديو والستوري والصور (يتم التعامل معها كفيديو)
            ydl_opts.update({
                'format': 'best',
                'outtmpl': 'downloaded_media.%(ext)s',
            })
            expected_ext = '.mp4' # تيك توك غالباً ما يكون mp4

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # البحث عن الملف الذي تم تحميله وإرساله
        downloaded_files = glob.glob("downloaded_media*")
        if downloaded_files:
            final_file = downloaded_files[0]
            # تحديد اسم الملف عند الحفظ لدى المستخدم
            dl_name = f"Aek_TikTok_{format_type}{os.path.splitext(final_file)[1]}"
            return send_file(final_file, as_attachment=True, download_name=dl_name)
        else:
            raise Exception("لم يتم العثور على الملف بعد التحميل.")
            
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error="❌ عذراً، تأكد من صحة الرابط أو أن الحساب ليس خاصاً (Private).")

if __name__ == '__main__':
    # تحديد البورت بشكل ديناميكي ليتوافق مع منصات الاستضافة مثل Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
