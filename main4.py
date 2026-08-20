import os
import requests
from flask import Flask, request, jsonify, render_template_string, Response

app = Flask(__name__)

# ==========================================
# 1. FRONTEND (UI & UX)
# ==========================================
# (نفس كود HTML و CSS و JS السابق بدون تغيير)
HTML_CODE = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AETECHUP - TikTok Downloader</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        /* ... الأكواد السابقة للستايل ... */
        :root { --bg-primary: #0f172a; --bg-surface: #1e293b; --bg-hero: linear-gradient(135deg, #4c1d95 0%, #5b21b6 100%); --text-primary: #f8fafc; --text-secondary: #cbd5e1; --border-color: #334155; --accent-purple: #8b5cf6; --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; transition: 0.25s; }
        body { background-color: var(--bg-primary); color: var(--text-primary); min-height: 100vh; }
        header { background-color: var(--bg-surface); border-bottom: 1px solid var(--border-color); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 800; color: var(--accent-purple); text-decoration: none; }
        .hero { background: var(--bg-hero); padding: 3.5rem 1rem; text-align: center; }
        .downloader-box { max-width: 750px; margin: 0 auto; background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(12px); padding: 8px; border-radius: 14px; display: flex; gap: 8px; }
        .input-wrapper { flex: 1; background: white; border-radius: 10px; display: flex; align-items: center; }
        .input-wrapper input { width: 100%; padding: 1rem; border: none; outline: none; border-radius: 10px; font-size: 1rem; color: #1e293b; }
        .btn-download { background: #6d28d9; color: white; border: none; padding: 1rem 2rem; border-radius: 10px; font-weight: 700; cursor: pointer; }
        .result-card { max-width: 750px; margin: 2rem auto 0; background: var(--bg-surface); border-radius: 16px; padding: 1.5rem; display: none; text-align: left; }
        .video-meta { display: flex; gap: 1.5rem; align-items: center; margin-bottom: 1.5rem; }
        .video-cover { width: 100px; height: 130px; border-radius: 10px; object-fit: cover; }
        .result-actions { display: flex; gap: 0.8rem; flex-wrap: wrap; }
        .btn-act { flex: 1; min-width: 180px; padding: 0.85rem; border-radius: 8px; text-align: center; text-decoration: none; font-weight: 700; color: white; }
        .btn-nowm { background: #10b981; } .btn-wm { background: #3b82f6; } .btn-mp3 { background: #f59e0b; }
        .loader { display: none; margin: 2rem auto; border: 4px solid rgba(255,255,255,0.2); border-top: 4px solid #ffffff; border-radius: 50%; width: 45px; height: 45px; animation: spin 0.8s linear infinite; }
        .error-banner { max-width: 750px; margin: 1.5rem auto 0; padding: 1rem; background: #ef444420; border: 1px solid #ef4444; color: #f87171; border-radius: 10px; display: none; text-align: center; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <header>
        <a href="#" class="logo">aetechup</a>
    </header>
    <section class="hero">
        <h1>TikTok Video Downloader</h1>
        <div class="downloader-box">
            <div class="input-wrapper">
                <input type="text" id="videoUrl" placeholder="Paste TikTok link here (vm.tiktok.com or www.tiktok.com)">
            </div>
            <button class="btn-download" id="downloadBtn">Download</button>
        </div>
        <div class="loader" id="loader"></div>
        <div class="error-banner" id="errorBanner"></div>
        <div class="result-card" id="resultCard">
            <div class="video-meta">
                <img src="" id="resCover" class="video-cover">
                <div class="video-info">
                    <span id="resAuthor" style="color:#8b5cf6; font-weight:bold;"></span>
                    <h4 id="resTitle"></h4>
                </div>
            </div>
            <div class="result-actions">
                <a href="#" class="btn-act btn-nowm" id="btnNoWm">No Watermark</a>
                <a href="#" class="btn-act btn-wm" id="btnWm">With Watermark</a>
                <a href="#" class="btn-act btn-mp3" id="btnMp3">Audio MP3</a>
            </div>
        </div>
    </section>

    <script>
        document.getElementById('downloadBtn').addEventListener('click', async () => {
            const urlInput = document.getElementById('videoUrl').value.trim();
            const loader = document.getElementById('loader');
            const resultCard = document.getElementById('resultCard');
            const errorBanner = document.getElementById('errorBanner');

            if (!urlInput) {
                errorBanner.innerText = "Please paste a valid link!";
                errorBanner.style.display = 'block'; return;
            }

            errorBanner.style.display = 'none'; resultCard.style.display = 'none'; loader.style.display = 'block';

            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: urlInput })
                });
                const data = await response.json();
                loader.style.display = 'none';

                if (data.status === 'success') {
                    document.getElementById('resCover').src = data.cover;
                    document.getElementById('resAuthor').innerText = '@' + data.author;
                    document.getElementById('resTitle').innerText = data.title;
                    
                    document.getElementById('btnNoWm').href = `/download_file?url=${encodeURIComponent(data.video_nowm)}&type=mp4`;
                    document.getElementById('btnWm').href = `/download_file?url=${encodeURIComponent(data.video_wm || data.video_nowm)}&type=mp4`;
                    document.getElementById('btnMp3').href = `/download_file?url=${encodeURIComponent(data.music)}&type=mp3`;
                    
                    resultCard.style.display = 'block';
                } else {
                    errorBanner.innerText = data.message;
                    errorBanner.style.display = 'block';
                }
            } catch(err) {
                loader.style.display = 'none';
                errorBanner.innerText = "Server error. Please retry.";
                errorBanner.style.display = 'block';
            }
        });
    </script>
</body>
</html>
"""

# ==========================================
# 2. BACKEND (Fixed Logic)
# ==========================================

def fetch_from_api(url):
    """
    نمرر الرابط مباشرة للـ API الخارجي دون استخدام requests.head من سيرفرنا
    لأن الـ API الخارجي قادر على معالجة روابط vm.tiktok.com بكفاءة.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url, headers=headers, timeout=12)
        if res.status_code == 200:
            json_data = res.json()
            if json_data.get('code') == 0:
                d = json_data.get('data', {})
                return {
                    'title': d.get('title', 'TikTok Video'),
                    'author': d.get('author', {}).get('unique_id', 'user'),
                    'cover': d.get('cover'),
                    'video_nowm': d.get('play'),
                    'video_wm': d.get('wmplay'),
                    'music': d.get('music')
                }
    except Exception as e:
        print("API Error:", e)
    return None

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.get_json() or {}
    raw_url = data.get('url', '').strip()

    if not raw_url:
        return jsonify({'status': 'error', 'message': 'Please provide a URL'}), 400

    # إرسال الرابط الخام مباشرة (سواء كان طويلاً أو قصيراً)
    result = fetch_from_api(raw_url)

    if result and result.get('video_nowm'):
        return jsonify({
            'status': 'success',
            **result
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to process this video. The link might be private, deleted, or invalid.'
        }), 400

@app.route('/download_file')
def download_file():
    file_url = request.args.get('url')
    file_type = request.args.get('type', 'mp4')

    if not file_url:
        return "Invalid File URL", 400

    try:
        # إجبار التنزيل المباشر
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = requests.get(file_url, headers=headers, stream=True, timeout=20)
        
        ext = "mp3" if file_type == "mp3" else "mp4"
        mime_type = "audio/mpeg" if file_type == "mp3" else "video/mp4"
        filename = f"aetechup_tiktok.{ext}"

        return Response(
            req.iter_content(chunk_size=1024 * 1024),
            content_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        return f"Download Failed: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
