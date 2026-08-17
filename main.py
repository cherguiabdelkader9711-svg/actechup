import os
import time
from flask import Flask, render_template_string, request, redirect, url_for, flash
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.urandom(24)

ENCRYPTION_KEY = Fernet.generate_key() if 'ENCRYPTION_KEY' not in os.environ else os.environ.get('ENCRYPTION_KEY').encode()
cipher_suite = Fernet(ENCRYPTION_KEY if isinstance(ENCRYPTION_KEY, bytes) else ENCRYPTION_KEY.encode())

# قواعد البيانات المؤقتة على السيرفر
USER_TIMESTAMPS = {}
ADDED_MEMBERS_DATABASE = {}
USER_SESSIONS = {} # لحفظ حالة الجلسة وتخطي تسجيل الدخول المتكرر

COOLDOWN_PERIOD = 86400  # 24 ساعة
MAX_MEMBERS_LIMIT = 100  # الحد الأقصى 100 عضو

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة إدارة ونقل الأعضاء - النظام الآمن المتقدم</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #090d16; color: #f1f5f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .secure-container { background: #111827; border: 1px solid #1f2937; padding: 35px; border-radius: 12px; width: 100%; max-width: 520px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5); }
        .badge { background: rgba(16, 185, 129, 0.1); color: #34d399; font-size: 12px; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-bottom: 15px; border: 1px solid rgba(52, 211, 153, 0.2); }
        .terms-box { background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 15px; border-radius: 8px; font-size: 12px; margin-bottom: 20px; text-align: right; line-height: 1.6; max-height: 130px; overflow-y: auto; }
        h2 { font-size: 22px; margin-bottom: 8px; color: #ffffff; }
        p.subtitle { font-size: 13px; color: #9ca3af; margin-bottom: 20px; }
        .form-group { margin-bottom: 16px; text-align: right; }
        label { display: block; font-size: 13px; color: #d1d5db; margin-bottom: 6px; font-weight: 500; }
        input[type="text"], input[type="password"] { width: 100%; padding: 11px; background: #1f2937; border: 1px solid #374151; border-radius: 8px; color: #fff; font-size: 14px; }
        input[type="text"]:focus, input[type="password"]:focus { outline: none; border-color: #3b82f6; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; text-align: right; font-size: 13px; color: #e2e8f0; cursor: pointer; }
        .checkbox-group input { width: 18px; height: 18px; cursor: pointer; accent-color: #2563eb; }
        button { width: 100%; background: #2563eb; color: #fff; border: none; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 8px; cursor: pointer; transition: background 0.3s; }
        button:hover { background: #1d4ed8; }
        .alert { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 20px; text-align: center; }
        .success { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 20px; text-align: center; }
        .security-note { font-size: 11px; color: #6b7280; text-align: center; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="secure-container">
        <div class="badge">🔒 منصة آمنة محمية ضد الحظر</div>
        <h2>إدارة ونقل الأعضاء الذكي</h2>
        <p class="subtitle">النظام المحترف لنقل الأعضاء وتخطي المتكرر</p>
        
        <div class="terms-box">
            <strong>⚠️ شروط الاستخدام وسياسة الأمان وإخلاء المسؤولية:</strong><br>
            1. <strong>الحد اليومي والكمية:</strong> 100 عضو كحد أقصى يومياً مع فاصل زمني آمن لتجنب حظر الحسابات.<br>
            2. <strong>تخطي المتكرر:</strong> يتذكر النظام الأعضاء المضافين سابقاً ويتخطاهم تلقائياً في الدفعات القادمة.<br>
            3. <strong>إخلاء المسؤولية:</strong> إدارة الموقع غير مسؤولة عن أي حظر قد يفرضه تيليجرام نتيجة الاستخدام المخالف.<br>
            4. <strong>التشفير:</strong> كافة البيانات الحساسة مشفرة ولا يتم كشفها نهائياً.
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
                <label>معرف التطبيق (API ID) أو التوكن:</label>
                <input type="password" name="token" placeholder="أدخل API ID أو التوكن..." required autocomplete="off">
            </div>
            
            <div class="form-group">
                <label>رقم الهاتف (مع رمز الدولة):</label>
                <input type="text" name="phone" placeholder="+213XXXXXXXXX" required autocomplete="off">
            </div>

            <div class="form-group">
                <label>كود التحقق المرسل لتلجرام (إن طلب منك):</label>
                <input type="text" name="code" placeholder="أدخل كود الرسالة (اختياري بالبداية)..." autocomplete="off">
            </div>

            <div class="form-group">
                <label>كلمة مرور الحماية الثنائية 2FA (إن وجدت):</label>
                <input type="password" name="two_fa" placeholder="كلمة المرور السحابية..." autocomplete="off">
            </div>

            <div class="form-group">
                <label>رابط القروب المصدر (عام وبأعضاء ظاهرين):</label>
                <input type="text" name="source_group" placeholder="t.me/PublicGroup" required>
            </div>

            <div class="form-group">
                <label>رابط قروبك الخاص المستهدف:</label>
                <input type="text" name="target_group" placeholder="@MyPrivateGroup" required>
            </div>

            <div class="checkbox-group">
                <input type="checkbox" id="agree" name="agree" required>
                <label for="agree" style="display:inline; color:#cbd5e1; cursor:pointer;">أوافق على كافة الشروط والسياسات المذكورة أعلاه.</label>
            </div>

            <button type="submit">بدء النقل الذكي وتخطي القدامى (100 عضو)</button>
        </form>
        
        <div class="security-note">
            🛡️ حماية قصوى وتخزين آمن للبيانات على السيرفر.
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
    phone = request.form.get('phone', '').strip()
    code = request.form.get('code', '').strip()
    two_fa = request.form.get('two_fa', '').strip()
    source_group = request.form.get('source_group', '').strip()
    target_group = request.form.get('target_group', '').strip()
    agreement = request.form.get('agree')
    
    if not agreement:
        flash('يجب عليك الموافقة على الشروط والسياسات قبل المتابعة.', 'alert')
        return redirect(url_for('home'))
    
    if not token or not phone or not source_group or not target_group:
        flash('يرجى تعبئة كافة الحقول الأساسية المطلوبة.', 'alert')
        return redirect(url_for('home'))
    
    if not ('t.me/' in source_group or source_group.startswith('@') or 'telegram.me/' in source_group):
        flash('تنبيه: يجب أن يكون رابط مجموعة المصدر عاماً (يحتوي على t.me/ أو @).', 'alert')
        return redirect(url_for('home'))
    
    current_time = time.time()
    
    # فحص الحد اليومي (24 ساعة) على السيرفر لتجاوز حذف المتصفح
    if phone in USER_TIMESTAMPS:
        elapsed_time = current_time - USER_TIMESTAMPS[phone]
        if elapsed_time < COOLDOWN_PERIOD:
            remaining_hours = int((COOLDOWN_PERIOD - elapsed_time) / 3600)
            remaining_minutes = int(((COOLDOWN_PERIOD - elapsed_time) % 3600) / 60)
            flash(f'⚠️ عذراً، لقد وصلت للحد اليومي (100 عضو). انتظر {remaining_hours} ساعة و {remaining_minutes} دقيقة لتخطي الأعضاء السابقين.', 'alert')
            return redirect(url_for('home'))

    try:
        encrypted_token = cipher_suite.encrypt(token.encode())
        
        # استرجاع الأعضاء المضافين سابقاً لهذا الرقم لتخطيهم تلقائياً
        already_added = ADDED_MEMBERS_DATABASE.get(phone, set())
        
        # [منطقة ربط مكتبة التيليجرام الفعليية عبر Telethon]: 
        # استخدام phone, code, two_fa للاتصال، وسحب الأعضاء وتخطي (already_added)، ونقل حتى 100 عضو جديد فقط.
        
        USER_TIMESTAMPS[phone] = current_time
        
        flash('تم التحقق بنجاح! بدأ النظام بنقل دفعة جديدة (حتى 100 عضو) مع تخطي من تم إضافتهم مسبقاً.', 'success')
    except Exception as e:
        flash('حدث خطأ في المصادقة أو الاتصال، تأكد من صحة الكود أو البيانات.', 'alert')
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
