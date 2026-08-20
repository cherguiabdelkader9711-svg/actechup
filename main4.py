import os
from flask import Flask, render_template_string, request, send_file
import yt_dlp

app = Flask(__name__)

# قالب HTML بسيط لتصميم واجهة الموقع
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تحميل فيديو تيك توك</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f172a; color: #fff; text-align: center; padding: 50px; }
        .container { background: #1e293b; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        input[type="text"] { width: 300px; padding: 10px; border-radius: 5px; border: none; margin-bottom: 10px; }
        button { background: #38bdf8; color: #0f172a; border: none; padding: 10px 20px; font-weight: bold; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0ea5e9; }
        .error { color: #f87171; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>تحميل فيديوهات تيك توك بدون علامة مائية</h2>
        <form method="POST" action="/download">
            <input type="text" name="url" placeholder="ألصق رابط تيك توك هنا..." required><br>
            <button type="submit">تحميل الفيديو</button>
        </form>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    output_filename = 'tiktok_video.mp4'
    
    # إعدادات التحميل باستخدام yt-dlp
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_filename,
        'quiet': True,
    }
    
    try:
        # مسح الملف القديم إن وجد
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        # إرسال الملف مباشرة لجهاز المستخدم لتحميله
        return send_file(output_filename, as_attachment=True)
    
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error="حدث خطأ أثناء تحميل الفيديو، تأكد من صحة الرابط.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
