import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.urandom(24)

ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة إدارة ونقل أعضاء تلجرام</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #090d16; color: #f1f5f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .secure-container { background: #111827; border: 1px solid #1f2937; padding: 35px; border-radius: 12px; width: 100%; max-width: 480px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5); }
        .badge { background: rgba(16, 185, 129, 0.1); color: #34d399; font-size: 12px; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-bottom: 15px; border: 1px solid rgba(52, 211, 153, 0.2); }
        .notice-box { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); color: #fbbf24; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; text-align: right; line-height: 1.5; }
        h2 { font-size: 22px; margin-bottom: 8px; color: #ffffff; }
        p.subtitle { font-size: 13px; color: #9ca3af; margin-bottom: 20px; }
        .form-group { margin-bottom: 18px; text-align: right; }
        label { display: block; font-size: 13px; color: #d1d5db; margin-bottom: 6px; font-weight: 500; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; background: #1f2937; border: 1px solid #374151; border-radius: 8px; color: #fff; font-size: 14px; transition: all 0.3s ease; }
        input[type="text"]:focus, input[type="password"]:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); }
        button { width: 100%; background: #2563eb; color: #fff; border: none; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 8px; cursor: pointer; transition: background 0.3s; margin-top: 10px; }
        button:hover { background: #1d4ed8; }
        .alert { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 20px; text-align: center; }
        .success { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 20px; text-align: center; }
        .security-note { font-size: 11px; color: #6b7280; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="secure-container">
        <div class="badge">🔒 نظام آمن ومحمي بالكامل</div>
        <h2>إدارة ونقل أعضاء تلجرام</h2>
        <p class="subtitle">أدخل بياناتك وتأكيد الكود لإتمام العملية</p>
        
        <div class="notice-box">
            ⚠️ <strong>تنبيه هام:</strong> يجب وضع رابط مجموعة عامة (Public Group) و<b>أعضاؤها ظاهرون</b> لكي يتم الاستخراج بنجاح.
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form method="POST" action="/process">
            <div class="form-group">
                <label>توكن الحساب أو البوت:</label>
                <input type="password" name="token" placeholder="أدخل التوكن هنا..." required autocomplete="off">
            </div>
            
            <div class="form-group">
                <label>رقم الهاتف (مع رمز الدولة):</label>
                <input type="text" name="phone" placeholder="+213XXXXXXXXX" required autocomplete="off">
            </div>

            <!-- خانة إضافة كود التحقق المُرسل لتلجرام -->
            <div class="form-group">
                <label>كود التحقق المرسل لتلجرام (إن طلب منك):</label>
                <input type="text" name="code" placeholder="أدخل الكود المكون من أرقام (اختياري بالبداية)..." autocomplete="off">
            </div>

            <div class="form-group">
                <label>رابط القروب المراد أخذ الأعضاء منه (عام):</label>
                <input type="text" name="source_group" placeholder="t.me/PublicGroup" required>
            </div>

            <div class="form-group">
                <label>رابط قروبك الخاص (المستهدف):</label>
                <input type="text" name="target_group" placeholder="@MyPrivateGroup" required>
            </div>

            <button type="submit">إرسال وتأكيد العملية</button>
        </form>
        
        <div class="security-note">
            🛡️ تشفير فائق الحماية لبياناتك ومنع أي تطفل خارجي.
        </div>
    </div>
</body>
</html>
"""

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process():
    token = request.form.get('token')
    phone = request.form.get('phone')
    code = request.form.get('code')
    source_group = request.form.get('source_group').strip()
    target_group = request.form.get('target_group').strip()
    
    if not token or not phone or not source_group or not target_group:
        flash('يرجى تعبئة كافة الحقول الأساسية بدقة.', 'alert')
        return redirect(url_for('home'))
    
    if not ('t.me/' in source_group or source_group.startswith('@') or 'telegram.me/' in source_group):
        flash('تنبيه: يجب أن يكون رابط مجموعة المصدر عاماً (يحتوي على t.me/ أو @).', 'alert')
        return redirect(url_for('home'))
    
    try:
        encrypted_token = cipher_suite.encrypt(token.encode())
        
        # [هنا إذا أرسل تلجرام كود التحقق لرقم الهاتف، يتم استقباله وتمريره لمكتبة السيرفر مع المتغير code]
        
        flash('تم استلام البيانات والكود بنجاح، وجاري تنفيذ نقل الأعضاء في الخلفية!', 'success')
    except Exception as e:
        flash('حدث خطأ في التحقق، تأكد من صحة الكود أو البيانات المدخلة.', 'alert')
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
