import os
import time
import asyncio
from threading import Thread
from flask import Flask, render_template_string, request, flash, session, redirect, url_for, jsonify
from cryptography.fernet import Fernet
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError, PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_actechup_2026')

USER_TIMESTAMPS = {}
ADDED_MEMBERS_DATABASE = {}
LIVE_LOGS = {} 

COOLDOWN_PERIOD = 86400  # 24 ساعة
MAX_MEMBERS_LIMIT = 100  
# تم إزالة التأخير الزمني كلياً للعمل بأقصى سرعة ممكنة (0 ثانية)

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# [============== دوال المصادقة ==============]
async def step1_send_code(api_id, api_hash, phone):
    session_name = f"session_{phone.replace('+', '')}"
    client = TelegramClient(session_name, int(api_id), api_hash)
    await client.connect()
    try:
        if not await client.is_user_authorized():
            result = await client.send_code_request(phone)
            return {"status": "CODE_SENT", "hash": result.phone_code_hash}
        return {"status": "ALREADY_AUTH"}
    except Exception as e:
        return {"status": f"ERROR: {str(e)}"}
    finally:
        await client.disconnect()

async def step2_verify_code(api_id, api_hash, phone, code, phone_code_hash, two_fa):
    session_name = f"session_{phone.replace('+', '')}"
    client = TelegramClient(session_name, int(api_id), api_hash)
    await client.connect()
    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        return "SUCCESS"
    except SessionPasswordNeededError:
        if two_fa:
            try:
                await client.sign_in(password=two_fa)
                return "SUCCESS"
            except Exception:
                return "ERROR: كلمة المرور السحابية خاطئة."
        return "2FA_NEEDED"
    except PhoneCodeInvalidError:
        return "INVALID_CODE"
    except PhoneCodeExpiredError:
        return "EXPIRED_CODE"
    except Exception as e:
        return f"ERROR: {str(e)}"
    finally:
        await client.disconnect()

# [============== دالة العمل في الخلفية (بسرعة جنونية) ==============]
def background_telegram_task(api_id, api_hash, phone, source_group, target_group):
    LIVE_LOGS[phone] = ['🚀 جاري الاتصال الآمن بسيرفرات تيليجرام...']
    
    async def run_logic():
        session_name = f"session_{phone.replace('+', '')}"
        client = TelegramClient(session_name, int(api_id), api_hash)
        await client.connect()
        try:
            LIVE_LOGS[phone].append('✅ تم الاتصال. جاري سحب الأعضاء وبدء الإضافة الجنونية الحظية...')
            source_entity = await client.get_entity(source_group)
            target_entity = await client.get_entity(target_group)
            
            participants = await client.get_participants(source_entity, limit=100)
            already_added = ADDED_MEMBERS_DATABASE.get(phone, set())
            
            added_count = 0
            for user in participants:
                if added_count >= MAX_MEMBERS_LIMIT:
                    LIVE_LOGS[phone].append('🛑 اكتملت المهمة: تم الوصول للحد الأقصى (100 عضو).')
                    break
                
                if user.bot or user.deleted or user.id in already_added:
                    continue
                
                name = user.username if user.username else user.first_name
                try:
                    await client(InviteToChannelRequest(target_entity, [user]))
                    already_added.add(user.id)
                    ADDED_MEMBERS_DATABASE[phone] = already_added
                    added_count += 1
                    
                    LIVE_LOGS[phone].append(f'<span style="color:#0f0;">⚡ تمت الإضافة الفورية: @{name}</span>')
                    
                    # ⚠️ تم إزالة الـ (Sleep) ليقوم النظام بالإضافة في أجزاء من الثانية
                    
                except PeerFloodError:
                    LIVE_LOGS[phone].append('<span style="color:#f00;">⚠️ ضربة أمنية: تيليجرام حظر الحساب بسبب السرعة الجنونية (Flood).</span>')
                    break
                except UserPrivacyRestrictedError:
                    LIVE_LOGS[phone].append(f'<span style="color:#aa0;">⏭️ تخطي الخصوصية: @{name}</span>')
                except Exception:
                    pass 
                    
            LIVE_LOGS[phone].append('🎉 توقفت العملية هنا. تحقق من مجموعتك.')
        except Exception as e:
            LIVE_LOGS[phone].append(f'<span style="color:#f00;">❌ حدث خطأ: {str(e)}</span>')
        finally:
            await client.disconnect()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_logic())
    loop.close()

# [============== واجهات الموقع ==============]

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة إدارة ونقل الأعضاء</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #090d16; color: #f1f5f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .container { background: #111827; border: 1px solid #1f2937; padding: 35px; border-radius: 12px; width: 100%; max-width: 500px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .badge { background: rgba(239, 68, 68, 0.1); color: #f87171; padding: 5px 10px; border-radius: 20px; font-size: 12px; display: inline-block; margin-bottom: 15px; border: 1px solid rgba(239, 68, 68, 0.2); }
        h2 { font-size: 22px; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; text-align: right; }
        label { display: block; font-size: 13px; color: #d1d5db; margin-bottom: 5px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 11px; background: #1f2937; border: 1px solid #374151; border-radius: 8px; color: #fff; font-size: 14px; }
        button { width: 100%; background: #2563eb; color: #fff; border: none; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 10px; transition: 0.3s; }
        button:hover { background: #1d4ed8; }
        .alert { background: rgba(239, 68, 68, 0.1); color: #f87171; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">🚀 وضع السرعة القصوى (بدون تأخير)</div>
        <h2>إعدادات النقل</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST" action="/submit_main">
            <div class="form-group"><label>API ID:</label><input type="text" name="api_id" required autocomplete="off"></div>
            <div class="form-group"><label>API Hash:</label><input type="password" name="api_hash" required autocomplete="off"></div>
            <div class="form-group"><label>رقم الهاتف:</label><input type="text" name="phone" placeholder="+213..." required autocomplete="off"></div>
            <div class="form-group"><label>رابط القروب المصدر:</label><input type="text" name="source_group" required autocomplete="off"></div>
            <div class="form-group"><label>رابط قروبك المستهدف:</label><input type="text" name="target_group" required autocomplete="off"></div>
            <button type="submit">بدء الهجوم السريع 🚀</button>
        </form>
    </div>
</body>
</html>
"""

# واجهة المؤقت المباشر (عند محاولة إضافة معلومات قبل 24 ساعة)
COOLDOWN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>توقف النظام - قيد الانتظار</title>
    <style>
        body { background-color: #090d16; color: #f1f5f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: 'Segoe UI'; margin: 0; }
        .container { background: #111827; padding: 40px; border-radius: 12px; width: 100%; max-width: 450px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #1f2937; }
        .icon { font-size: 50px; margin-bottom: 15px; }
        h2 { color: #f87171; margin-bottom: 10px; }
        p { color: #9ca3af; font-size: 14px; margin-bottom: 25px; line-height: 1.6; }
        .timer-box { font-size: 35px; font-weight: bold; color: #3b82f6; background: #1f2937; padding: 20px; border-radius: 10px; letter-spacing: 2px; border: 1px solid #374151; margin-bottom: 20px; }
        .btn-home { display: inline-block; background: #374151; color: #fff; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-size: 14px; transition: 0.3s; }
        .btn-home:hover { background: #4b5563; }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">⏳</div>
        <h2>تم بلوغ الحد المسموح</h2>
        <p>لقد قمت بإجراء عملية إضافة مؤخراً بهذا الرقم. لحماية حسابك من الحظر الدائم، يفرض النظام استراحة إجبارية لمدة 24 ساعة.</p>
        
        <div class="timer-box" id="countdown">00:00:00</div>
        
        <a href="/" class="btn-home">العودة للرئيسية</a>
    </div>

    <script>
        let timeLeft = {{ remaining_seconds }};
        
        function updateTimer() {
            if (timeLeft <= 0) {
                document.getElementById('countdown').innerHTML = "00:00:00";
                document.getElementById('countdown').style.color = "#10b981";
                document.querySelector('p').innerHTML = "لقد انتهى وقت الانتظار! يمكنك بدء عملية جديدة الآن.";
                return;
            }
            
            let hours = Math.floor(timeLeft / 3600);
            let minutes = Math.floor((timeLeft % 3600) / 60);
            let seconds = Math.floor(timeLeft % 60);
            
            hours = hours < 10 ? "0" + hours : hours;
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;
            
            document.getElementById('countdown').innerHTML = hours + ":" + minutes + ":" + seconds;
            timeLeft--;
        }
        
        setInterval(updateTimer, 1000);
        updateTimer();
    </script>
</body>
</html>
"""

CODE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تأكيد الكود</title>
    <style>
        body { background-color: #090d16; color: #f1f5f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: 'Segoe UI'; }
        .container { background: #111827; padding: 35px; border-radius: 12px; width: 100%; max-width: 400px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #1f2937; }
        .icon { font-size: 40px; margin-bottom: 10px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; background: #1f2937; border: 1px solid #374151; border-radius: 8px; color: #fff; text-align: center; font-size: 16px; letter-spacing: 2px; }
        button { width: 100%; background: #10b981; color: #fff; border: none; padding: 12px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; }
        button:hover { background: #059669; }
        .alert { color: #f87171; font-size: 13px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">💬</div>
        <h2>أدخل كود تيليجرام</h2>
        <p style="color:#9ca3af; font-size:13px; margin-bottom:20px;">تم إرسال كود التأكيد إلى حسابك، الرجاء إدخاله للمتابعة.</p>
        {% with messages = get_flashed_messages() %}
            {% if messages %}<div class="alert">{{ messages[0] }}</div>{% endif %}
        {% endwith %}
        <form method="POST" action="/submit_code">
            <input type="text" name="code" placeholder="الكود هنا..." required autofocus autocomplete="off">
            <input type="password" name="two_fa" placeholder="كلمة المرور 2FA (إن وجدت)">
            <button type="submit">أكمل بدء النقل ✅</button>
        </form>
    </div>
</body>
</html>
"""

LIVE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>البث المباشر للإضافة (السرعة القصوى)</title>
    <style>
        body { background-color: #090d16; color: #f1f5f9; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; font-family: 'Segoe UI', sans-serif; }
        h2 { color: #3b82f6; margin-bottom: 10px; }
        p { color: #9ca3af; font-size: 14px; margin-bottom: 20px; text-align: center; }
        .terminal-box {
            background-color: #050505;
            color: #10b981;
            font-family: 'Courier New', Courier, monospace;
            width: 100%;
            max-width: 600px;
            height: 400px;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #333;
            box-shadow: inset 0 0 15px #000, 0 0 20px rgba(59, 130, 246, 0.2);
            overflow-y: auto;
            text-align: right;
            line-height: 1.8;
            font-size: 14px;
        }
        .log-entry { border-bottom: 1px dashed #111; margin-bottom: 5px; padding-bottom: 5px; }
        .btn-home { margin-top: 20px; background: #374151; color: #fff; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
    <h2>⚡ البث المباشر (وضع السرعة الجنونية) ⚡</h2>
    <p>يتم الآن رمي الطلبات بأقصى سرعة ممكنة للسيرفر.</p>
    
    <div class="terminal-box" id="terminal">
        <div class="log-entry">🔄 جاري تهيئة النظام...</div>
    </div>

    <a href="/" class="btn-home">العودة للرئيسية</a>

    <script>
        setInterval(function() {
            fetch('/api/logs')
            .then(response => response.json())
            .then(data => {
                if (data.logs) {
                    let terminal = document.getElementById('terminal');
                    let htmlContent = '';
                    data.logs.forEach(function(log) {
                        htmlContent += '<div class="log-entry">' + log + '</div>';
                    });
                    terminal.innerHTML = htmlContent;
                    terminal.scrollTop = terminal.scrollHeight;
                }
            });
        }, 500); // تحديث سريع جداً كل نصف ثانية لمواكبة السرعة
    </script>
</body>
</html>
"""

# [============== مسارات الموقع ==============]

@app.route('/')
def home():
    return render_template_string(MAIN_TEMPLATE)

@app.route('/submit_main', methods=['POST'])
def submit_main():
    session['api_id'] = request.form['api_id'].strip()
    session['api_hash'] = request.form['api_hash'].strip()
    session['phone'] = request.form['phone'].strip()
    session['source_group'] = request.form['source_group'].strip()
    session['target_group'] = request.form['target_group'].strip()
    
    phone = session['phone']
    
    # [تعديل هام]: التحقق من المؤقت قبل إرسال كود تيليجرام
    if phone in USER_TIMESTAMPS:
        elapsed_time = time.time() - USER_TIMESTAMPS[phone]
        if elapsed_time < COOLDOWN_PERIOD:
            remaining = COOLDOWN_PERIOD - elapsed_time
            # تحويله فوراً لصفحة المؤقت
            return render_template_string(COOLDOWN_TEMPLATE, remaining_seconds=int(remaining))

    result = run_async(step1_send_code(session['api_id'], session['api_hash'], phone))
    
    if result["status"] == "CODE_SENT":
        session['phone_code_hash'] = result["hash"]
        return render_template_string(CODE_TEMPLATE)
    elif result["status"] == "ALREADY_AUTH":
        # تفعيل المؤقت فوراً بمجرد بدء العملية
        USER_TIMESTAMPS[phone] = time.time()
        Thread(target=background_telegram_task, args=(session['api_id'], session['api_hash'], phone, session['source_group'], session['target_group'])).start()
        return redirect(url_for('live_progress'))
    else:
        flash(result["status"])
        return redirect(url_for('home'))

@app.route('/submit_code', methods=['POST'])
def submit_code():
    code = request.form['code'].strip()
    two_fa = request.form.get('two_fa', '').strip()
    
    api_id = session.get('api_id')
    api_hash = session.get('api_hash')
    phone = session.get('phone')
    source = session.get('source_group')
    target = session.get('target_group')
    phone_code_hash = session.get('phone_code_hash') 
    
    status = run_async(step2_verify_code(api_id, api_hash, phone, code, phone_code_hash, two_fa))
    
    if status == "SUCCESS":
        # تفعيل المؤقت وبدء النقل
        USER_TIMESTAMPS[phone] = time.time()
        Thread(target=background_telegram_task, args=(api_id, api_hash, phone, source, target)).start()
        return redirect(url_for('live_progress'))
    elif status == "2FA_NEEDED":
        flash('⚠️ الحساب محمي. أدخل الكود مجدداً مع كلمة المرور السحابية.')
        return render_template_string(CODE_TEMPLATE)
    elif status == "INVALID_CODE":
        flash('❌ الكود غير صحيح، يرجى المحاولة مجدداً.')
        return render_template_string(CODE_TEMPLATE)
    elif status == "EXPIRED_CODE":
        flash('❌ انتهت صلاحية الكود. يرجى العودة للرئيسية والبدء من جديد.')
        return render_template_string(CODE_TEMPLATE)
    else:
        flash(f'❌ خطأ: {status}')
        return render_template_string(CODE_TEMPLATE)

@app.route('/live')
def live_progress():
    return render_template_string(LIVE_TEMPLATE)

@app.route('/api/logs')
def api_logs():
    phone = session.get('phone')
    if phone and phone in LIVE_LOGS:
        return jsonify({'logs': LIVE_LOGS[phone]})
    return jsonify({'logs': ['جاري انتظار بدء العملية...']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
