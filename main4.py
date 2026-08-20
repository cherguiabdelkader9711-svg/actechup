import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ==========================================
# 1. FRONTEND (UI & UX المحسّن)
# ==========================================
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
        :root {
            --bg-primary: #0f172a; --bg-surface: #1e293b;
            --bg-hero: linear-gradient(135deg, #4c1d95 0%, #5b21b6 100%);
            --text-primary: #f8fafc; --text-secondary: #cbd5e1;
            --border-color: #334155; --accent-purple: #8b5cf6;
            --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }
        [data-theme="light"] {
            --bg-primary: #f8f9fa; --bg-surface: #ffffff;
            --bg-hero: linear-gradient(135deg, #7000ff 0%, #a100ff 100%);
            --text-primary: #1f2937; --text-secondary: #4b5563;
            --border-color: #e5e7eb; --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; transition: 0.25s; }
        body { background-color: var(--bg-primary); color: var(--text-primary); direction: ltr; min-height: 100vh; }
        [dir="rtl"] { direction: rtl; }
        header { background-color: var(--bg-surface); border-bottom: 1px solid var(--border-color); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
        .logo { font-size: 1.5rem; font-weight: 800; color: var(--accent-purple); text-decoration: none; display: flex; align-items: center; gap: 0.5rem; }
        .nav-controls { display: flex; align-items: center; gap: 1rem; }
        .lang-select, .theme-toggle { background: var(--bg-primary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; font-weight: 500; }
        .hero { background: var(--bg-hero); padding: 3.5rem 1rem; text-align: center; color: white; }
        .hero h1 { font-size: 2.2rem; margin-bottom: 1.5rem; font-weight: 800; }
        .downloader-box { max-width: 750px; margin: 0 auto; background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(12px); padding: 8px; border-radius: 14px; display: flex; gap: 8px; border: 1px solid rgba(255, 255, 255, 0.2); }
        .input-wrapper { flex: 1; background: white; border-radius: 10px; display: flex; align-items: center; }
        .input-wrapper input { width: 100%; padding: 1rem; border: none; outline: none; border-radius: 10px; font-size: 1rem; color: #1e293b; }
        .btn-paste { background: #f1f5f9; color: #475569; border: none; padding: 0.6rem 1rem; margin-right: 0.5rem; border-radius: 8px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 0.4rem; }
        .btn-download { background: #6d28d9; color: white; border: none; padding: 1rem 2rem; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 1rem; }
        .btn-download:hover { background: #5b21b6; }
        
        /* Card Display Area */
        .result-card { max-width: 750px; margin: 2rem auto 0; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; display: none; box-shadow: var(--shadow); text-align: left; }
        [dir="rtl"] .result-card { text-align: right; }
        .video-meta { display: flex; gap: 1.5rem; align-items: center; margin-bottom: 1.5rem; }
        .video-cover { width: 100px; height: 130px; border-radius: 10px; object-fit: cover; border: 1px solid var(--border-color); }
        .video-info h4 { font-size: 1.1rem; margin-bottom: 0.5rem; line-height: 1.4; }
        .video-author { color: var(--accent-purple); font-weight: 600; font-size: 0.9rem; }
        .result-actions { display: flex; gap: 0.8rem; flex-wrap: wrap; }
        .btn-act { flex: 1; min-width: 180px; padding: 0.85rem; border-radius: 8px; text-align: center; text-decoration: none; font-weight: 700; color: white; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
        .btn-nowm { background: #10b981; } .btn-nowm:hover { background: #059669; }
        .btn-wm { background: #3b82f6; } .btn-wm:hover { background: #2563eb; }
        .btn-mp3 { background: #f59e0b; } .btn-mp3:hover { background: #d97706; }
        
        /* Loader & Error Alerts */
        .loader { display: none; margin: 2rem auto; border: 4px solid rgba(255,255,255,0.2); border-top: 4px solid #ffffff; border-radius: 50%; width: 45px; height: 45px; animation: spin 0.8s linear infinite; }
        .error-banner { max-width: 750px; margin: 1.5rem auto 0; padding: 1rem; background: #ef444420; border: 1px solid #ef4444; color: #f87171; border-radius: 10px; display: none; text-align: center; font-weight: 600; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        /* Grid Section */
        .features { max-width: 1000px; margin: 4rem auto; padding: 0 1rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; }
        .feature-card { background: var(--bg-surface); padding: 2rem; border-radius: 14px; border: 1px solid var(--border-color); text-align: center; }
        .feature-card i { font-size: 2.2rem; color: var(--accent-purple); margin-bottom: 1rem; }
        footer { background-color: #090d16; color: #64748b; padding: 2.5rem 1rem; text-align: center; margin-top: 5rem; font-size: 0.9rem; }
    </style>
</head>
<body>
    <header>
        <a href="#" class="logo"><i class="fa-solid fa-bolt"></i> aetechup</a>
        <div class="nav-controls">
            <button class="theme-toggle" id="themeBtn"><i class="fa-solid fa-sun"></i></button>
            <select class="lang-select" id="langSelect">
                <option value="en">English</option>
                <option value="ar">العربية</option>
                <option value="fr">Français</option>
            </select>
        </div>
    </header>

    <section class="hero">
        <h1 id="heroTitle">TikTok Video Downloader</h1>
        <div class="downloader-box">
            <div class="input-wrapper">
                <input type="text" id="videoUrl" placeholder="Paste TikTok video link here...">
                <button class="btn-paste" id="pasteBtn"><i class="fa-regular fa-clipboard"></i> <span>Paste</span></button>
            </div>
            <button class="btn-download" id="downloadBtn">Download</button>
        </div>

        <div class="loader" id="loader"></div>
        <div class="error-banner" id="errorBanner"></div>

        <div class="result-card" id="resultCard">
            <div class="video-meta">
                <img src="" id="resCover" class="video-cover" alt="Cover">
                <div class="video-info">
                    <span class="video-author" id="resAuthor">@author</span>
                    <h4 id="resTitle">TikTok Video Description</h4>
                </div>
            </div>
            <div class="result-actions">
                <a href="#" class="btn-act btn-nowm" id="btnNoWm" target="_blank" download><i class="fa-solid fa-download"></i> No Watermark</a>
                <a href="#" class="btn-act btn-wm" id="btnWm" target="_blank" download><i class="fa-solid fa-film"></i> With Watermark</a>
                <a href="#" class="btn-act btn-mp3" id="btnMp3" target="_blank" download><i class="fa-solid fa-music"></i> Audio MP3</a>
            </div>
        </div>
    </section>

    <section class="features">
        <div class="feature-card"><i class="fa-solid fa-bolt"></i><h3>Ultra Fast</h3><p>Instant processing with multi-node API routing.</p></div>
        <div class="feature-card"><i class="fa-solid fa-shield-halved"></i><h3>No Watermark</h3><p>Clean HD video downloads without logos or branding.</p></div>
        <div class="feature-card"><i class="fa-solid fa-mobile-screen"></i><h3>All Devices</h3><p>Works smoothly on iOS, Android, PC, and tablets.</p></div>
    </section>

    <footer>
        <p>aetechup &copy; 2018-2026. All rights reserved.</p>
    </footer>

    <script>
        // Theme Switcher
        document.getElementById('themeBtn').addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
            document.getElementById('themeBtn').innerHTML = target === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
        });

        // Paste Link
        document.getElementById('pasteBtn').addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                document.getElementById('videoUrl').value = text;
            } catch(e) { alert("Clipboard permission required."); }
        });

        // Process Download Request
        document.getElementById('downloadBtn').addEventListener('click', async () => {
            const urlInput = document.getElementById('videoUrl').value.trim();
            const loader = document.getElementById('loader');
            const resultCard = document.getElementById('resultCard');
            const errorBanner = document.getElementById('errorBanner');

            if (!urlInput) {
                errorBanner.innerText = "Please paste a valid TikTok link first!";
                errorBanner.style.display = 'block';
                return;
            }

            errorBanner.style.display = 'none';
            resultCard.style.display = 'none';
            loader.style.display = 'block';

            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: urlInput })
                });

                const data = await response.json();
                loader.style.display = 'none';

                if (data.status === 'success') {
                    document.getElementById('resCover').src = data.cover || 'https://via.placeholder.com/100x130';
                    document.getElementById('resAuthor').innerText = '@' + (data.author || 'tiktok_user');
                    document.getElementById('resTitle').innerText = data.title || 'TikTok Video';
                    
                    document.getElementById('btnNoWm').href = data.video_nowm;
                    document.getElementById('btnWm').href = data.video_wm || data.video_nowm;
                    document.getElementById('btnMp3').href = data.music;
                    
                    resultCard.style.display = 'block';
                } else {
                    errorBanner.innerText = data.message || "Unable to download video. Check link or try again.";
                    errorBanner.style.display = 'block';
                }
            } catch(err) {
                loader.style.display = 'none';
                errorBanner.innerText = "Server connection timeout. Please retry.";
                errorBanner.style.display = 'block';
            }
        });
    </script>
</body>
</html>
"""

# ==========================================
# 2. BACKEND (Multi-API System with Fallback)
# ==========================================

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

def resolve_url(url):
    """فك الروابط المختصرة vm.tiktok.com إلى الرابط الأصلي"""
    try:
        if "tiktok.com" in url:
            res = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=5)
            return res.url
    except Exception:
        pass
    return url

def fetch_from_tikwm(url):
    """المحرك الأول: TikWM API"""
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url, headers=HEADERS, timeout=8)
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
    except Exception:
        pass
    return None

def fetch_from_lovetik(url):
    """المحرك الثاني (احتياطي): LoveTik API"""
    try:
        api_url = "https://lovetik.com/api/ajax/search"
        payload = {'query': url}
        res = requests.post(api_url, data=payload, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            json_data = res.json()
            if json_data.get('status') == 'ok':
                links = json_data.get('links', [])
                nowm = links[0].get('a') if len(links) > 0 else None
                wm = links[1].get('a') if len(links) > 1 else nowm
                mp3 = json_data.get('links', [])[-1].get('a')
                return {
                    'title': json_data.get('desc', 'TikTok Video'),
                    'author': json_data.get('author', 'user'),
                    'cover': json_data.get('cover'),
                    'video_nowm': nowm,
                    'video_wm': wm,
                    'music': mp3
                }
    except Exception:
        pass
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

    # 1. فك الرابط إذا كان قصيراً
    clean_url = resolve_url(raw_url)

    # 2. المحاولة في السيرفر الأول TikWM
    result = fetch_from_tikwm(clean_url)

    # 3. إذا فشل السيرفر الأول، الانتقال تلقائياً للسيرفر الاحتياطي LoveTik
    if not result:
        result = fetch_from_lovetik(clean_url)

    # 4. النتيجة النهائية
    if result and result.get('video_nowm'):
        return jsonify({
            'status': 'success',
            'title': result['title'],
            'author': result['author'],
            'cover': result['cover'],
            'video_nowm': result['video_nowm'],
            'video_wm': result['video_wm'],
            'music': result['music']
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to process this video. The video might be private or blocked.'
        }), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
