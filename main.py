import os
import time
import asyncio
from threading import Thread
from flask import Flask, render_template_string, request, redirect, url_for, flash
from cryptography.fernet import Fernet
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest

app = Flask(__name__)
app.secret_key = os.urandom(24)

ENCRYPTION_KEY = Fernet.generate_key() if 'ENCRYPTION_KEY' not in os.environ else os.environ.get('ENCRYPTION_KEY').encode()
cipher_suite = Fernet(ENCRYPTION_KEY if isinstance(ENCRYPTION_KEY, bytes) else ENCRYPTION_KEY.encode())

# قواعد بيانات مؤقتة
USER_TIMESTAMPS = {}
ADDED_MEMBERS_DATABASE = {}

COOLDOWN_PERIOD = 86400  # 24 ساعة
MAX_MEMBERS_LIMIT = 100  # الحد الأقصى 100 عضو

# [================= دالة العمليات الخلفية (Telethon) =================]
def background_telegram_task(api_id, api_hash, phone, code, two_fa, source_group, target_group):
    """
    هذه الدالة تعمل في الخلفية دون أن توقف الموقع. 
    تتصل بتيليجرام، تسجل الدخول، وتسحب الأعضاء وتضيفهم.
    """
    # إنشاء بيئة عمل غير متزامنة (Asyncio Loop) خاصة بهذا الخيط
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # تسمية ملف الجلسة برقم الهاتف للحفاظ على تسجيل الدخول
    session_name = f"session_{phone.replace('+', '')}"
    client = TelegramClient(session_name, int(api_id), api_hash, loop=loop)

    async def run_logic():
        await client.connect()
        
        # 1. نظام المصادقة وتسجيل الدخول
        if not await client.is_user_authorized():
            if not code:
                # إذا لم يضع المستخدم الكود، نأمر تيليجرام بإرسال الكود لهاتفه
                try:
                    await client.send_code_request(phone)
                    print(f"تم إرسال كود التحقق إلى الرقم {phone}. يرجى إدخاله في الموقع.")
                except Exception as e:
                    print(f"خطأ في إرسال الكود: {e}")
                await client.disconnect()
                return
            else:
                # إذا أدخل الكود، نقوم بتسجيل الدخول
                try:
                    await client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    if two_fa:
                        await client.sign_in(password=two_fa)
                    else:
                        print("هذا الحساب محمي بكلمة مرور 2FA. الرجاء إدخالها.")
                        await client.disconnect()
                        return
                except Exception as e:
                    print(f"خطأ في تسجيل الدخول: {e}")
                    await client.disconnect()
                    return

        # 2. نظام السحب والإضافة
        try:
            source_entity = await client.get_entity(source_group)
            target_entity = await client.get_entity(target_group)
            
            # جلب آخر 100 عضو من المجموعة المصدر
            participants = await client.get_participants(source_entity, limit=100)
            
            # استدعاء سجل الأعضاء المضافين سابقاً لهذا الرقم
            already_added = ADDED_MEMBERS_DATABASE.get(phone, set())
            
            added_count = 0
            for user in participants:
                if added_count >= MAX_MEMBERS_LIMIT:
                    break
                
                # تخطي البوتات، الحسابات المحذوفة، ومن تمت إضافته سابقاً
                if user.bot or user.deleted or user.id in already_added:
                    continue
                
                try:
                    # أمر الإضافة الفعلي
                    await client(InviteToChannelRequest(target_entity, [user]))
                    already_added.add(user.id)
                    ADDED_MEMBERS_DATABASE[phone] = already_added
                    added_count += 1
                    
                    print(f"تمت إضافة العضو بنجاح: {user.username or user.id}")
                    
                    # ⚠️ فاصل زمني هام جداً (15 ثانية) بين كل عضو لتجنب الحظر
                    await asyncio.sleep(15) 
                    
                except PeerFloodError:
                    print("تنبيه أمان: تم تفعيل حظر Flood من تيليجرام! تم إيقاف العملية لحماية حسابك.")
                    break
                except UserPrivacyRestrictedError:
                    print(f"تخطي: العضو {user.id} يمنع إضافته للمجموعات بسبب الخصوصية.")
                except Exception as e:
                    print(f"خطأ في إضافة العضو {user.id}: {e}")
                    
        except Exception as e:
            print(f"خطأ في عملية النقل الرئيسية: {e}")
        finally:
            await client.disconnect()

    # تشغيل الدالة
    loop.run_until_complete(run_logic())
    loop.close()
# [====================================================================]


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة إدارة ونقل الأعضاء - النظام الآمن</title>
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
            <strong>⚠️ شروط الاستخدام وسياسة الأمان:</strong><br>
            1. الحد اليومي: 100 عضو كحد أقصى يومياً.<br>
            2. تخطي المتكرر: يتذكر النظام الأعضاء المضافين سابقاً ويتخطاهم تلقائياً.<br>
            3. الحماية والتشفير: يتم إرسال طلبات الإضافة بفاصل 15 ثانية لتجنب حظر حسابك.
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
                <label>معرف التطبيق (API ID):</label>
                <input type="text" name="api_id" placeholder="مثال: 30239790" required autocomplete="off">
            </div>

            <div class="form-group">
                <label>مفتاح التطبيق (API Hash):</label>
                <input type="password" name="api_hash" placeholder="أدخل API Hash هنا..." required autocomplete="off">
            </div>
            
            <div class="form-group">
                <label>رقم الهاتف (مع رمز الدولة):</label>
                <input type="text" name="phone" placeholder="+213XXXXXXXXX" required autocomplete="off">
            </div>

            <div class="form-group">
                <label>كود التحقق المرسل لتلجرام (إن طلب منك):</label>
                <input type="text" name="code" placeholder="أدخل كود الرسالة..." autocomplete="off">
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
                <label for="agree" style="display:inline; color:#cbd5e1; cursor:pointer;">أوافق على كافة الشروط والسياسات.</label>
            </div>

            <button type="submit">بدء النقل الذكي وتخطي القدامى (100 عضو)</button>
        </form>
    </div>
</body>
</html>
"""

PROGRESS_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جاري نقل الأعضاء بنجاح...</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #090d16; color: #f1f5f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .progress-container { background: #111827; border: 1px solid #1f2937; padding: 40px; border-radius: 14px; width: 100%; max-width: 500px; text-align: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6); }
        .spinner { width: 50px; height: 50px; border: 4px solid rgba(59, 130, 246, 0.2); border-top: 4px solid #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        h2 { font-size: 22px; color: #ffffff; margin-bottom: 10px; }
        p { color: #9ca3af; font-size: 14px; margin-bottom: 20px; }
        .live-box { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399; padding: 15px; border-radius: 8px; font-size: 14px; margin-bottom: 20px; text-align: right; line-height: 1.6; }
        .back-btn { display: inline-block; background: #374151; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-size: 14px; transition: background 0.3s; }
        .back-btn:hover { background: #4b5563; }
    </style>
</head>
<body>
    <div class="progress-container">
        <div class="spinner"></div>
        <h2>جاري استخراج ونقل الأعضاء...</h2>
        <p>يتم الآن نقل الأعضاء واحداً تلو الآخر في الخلفية مع فاصل زمني (15 ثانية) لحماية حسابك.</p>
        
        <div class="live-box" id="status-box">
            🔄 <b>حالة العملية المباشرة:</b><br>
            - جاري الاتصال بحساب تيليجرام...<br>
            - يتم نقل الأعضاء الجدد إلى <b>{{ target_group }}</b>...
        </div>

        <a href="/" class="back-btn">العودة للرئيسية</a>
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
    api_id = request.form.get('api_id', '').strip()
    api_hash = request.form.get('api_hash', '').strip()
    phone = request.form.get('phone', '').strip()
    code = request.form.get('code', '').strip()
    two_fa = request.form.get('two_fa', '').strip()
    source_group = request.form.get('source_group', '').strip()
    target_group = request.form.get('target_group', '').strip()
    agreement = request.form.get('agree')
    
    if not agreement:
        flash('يجب عليك الموافقة على الشروط والسياسات قبل المتابعة.', 'alert')
        return redirect(url_for('home'))
    
    if not api_id or not api_hash or not phone or not source_group or not target_group:
        flash('يرجى تعبئة كافة الحقول الأساسية المطلوبة.', 'alert')
        return redirect(url_for('home'))
    
    current_time = time.time()
    
    # فحص الحد اليومي إذا تم الإرسال بوجود كود التحقق
    if phone in USER_TIMESTAMPS and code:
        elapsed_time = current_time - USER_TIMESTAMPS[phone]
        if elapsed_time < COOLDOWN_PERIOD:
            remaining_hours = int((COOLDOWN_PERIOD - elapsed_time) / 3600)
            remaining_minutes = int(((COOLDOWN_PERIOD - elapsed_time) % 3600) / 60)
            flash(f'⚠️ عذراً، لقد وصلت للحد اليومي (100 عضو). انتظر {remaining_hours} ساعة.', 'alert')
            return redirect(url_for('home'))

    if code:
        # إذا تم إدخال الكود، نبدأ العملية ونحسب الحد اليومي
        USER_TIMESTAMPS[phone] = current_time
    
    # 🚀 تشغيل عملية تيليجرام الفعلية في مسار خلفي مستقل 🚀
    thread = Thread(target=background_telegram_task, args=(api_id, api_hash, phone, code, two_fa, source_group, target_group))
    thread.start()
    
    if not code:
        flash('✅ تم الاتصال بحسابك بنجاح. لقد أرسل لك تيليجرام كود التحقق لتسجيل الدخول، يرجى إدخاله الآن في الخانة المخصصة ثم اضغط بدء مرة أخرى.', 'success')
        return redirect(url_for('home'))
    
    return render_template_string(PROGRESS_TEMPLATE, target_group=target_group)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
