# تأكد من إضافة FloodWaitError إلى الاستيرادات في أعلى الملف
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError, PeerFloodError, UserPrivacyRestrictedError, FloodWaitError

def background_telegram_task(api_id, api_hash, phone, source_group, target_group):
    LIVE_LOGS[phone] = ['🚀 جاري الاتصال الآمن بسيرفرات تيليجرام...']
    BATCH_SIZE = 5  # تقليل الدفعة إلى 5 لتجنب فشل المجموعة بالكامل بسبب شخص واحد
    
    async def run_logic():
        session_name = f"session_{phone.replace('+', '')}"
        client = TelegramClient(session_name, int(api_id), api_hash)
        await client.connect()
        try:
            LIVE_LOGS[phone].append('✅ تم الاتصال. جاري فلترة الأعضاء وتجهيز الدفعات (5 أعضاء لكل دفعة)...')
            source_entity = await client.get_entity(source_group)
            target_entity = await client.get_entity(target_group)
            
            participants = await client.get_participants(source_entity, limit=200)
            already_added = ADDED_MEMBERS_DATABASE.get(phone, set())
            
            valid_users = []
            for user in participants:
                if not user.bot and not user.deleted and user.id not in already_added:
                    valid_users.append(user)
                if len(valid_users) >= MAX_MEMBERS_LIMIT:
                    break

            if not valid_users:
                LIVE_LOGS[phone].append('⚠️ لم يتم العثور على أعضاء جدد.')
                return

            for i in range(0, len(valid_users), BATCH_SIZE):
                chunk = valid_users[i:i + BATCH_SIZE]
                
                try:
                    LIVE_LOGS[phone].append(f'🔥 جاري إرسال دفعة تحتوي على {len(chunk)} أعضاء...')
                    
                    await client(InviteToChannelRequest(target_entity, chunk))
                    
                    for u in chunk:
                        already_added.add(u.id)
                    ADDED_MEMBERS_DATABASE[phone] = already_added
                    
                    LIVE_LOGS[phone].append(f'<span style="color:#0f0;">⚡ تمت إضافة {len(chunk)} أعضاء بنجاح!</span>')
                    
                    # استراحة قصيرة جداً (3 ثوانٍ) لعدم استفزاز السيرفر
                    await asyncio.sleep(3)
                    
                except FloodWaitError as e:
                    # المستشعر الذكي: قراءة الوقت الذي يطلبه تيليجرام والانتظار بصمت
                    LIVE_LOGS[phone].append(f'<span style="color:#aa0;">⏳ طلب تيليجرام الانتظار الإجباري لمدة {e.seconds} ثانية. النظام يتوقف مؤقتاً...</span>')
                    await asyncio.sleep(e.seconds)
                    LIVE_LOGS[phone].append('<span style="color:#0f0;">🔄 انتهى وقت الانتظار، النظام يعود للعمل!</span>')
                    
                except PeerFloodError:
                    LIVE_LOGS[phone].append('<span style="color:#f00;">⚠️ حظر صارم: تيليجرام أوقف الحساب مؤقتاً بالكامل.</span>')
                    break
                except Exception as e:
                    LIVE_LOGS[phone].append(f'<span style="color:#f00;">⚠️ خطأ في إضافة الدفعة (غالباً بسبب إعدادات الخصوصية لأحد الأعضاء). جاري التخطي...</span>')
                    
            LIVE_LOGS[phone].append('🎉 توقفت العملية هنا. تحقق من مجموعتك.')
        except Exception as e:
            LIVE_LOGS[phone].append(f'<span style="color:#f00;">❌ حدث خطأ جذري: {str(e)}</span>')
        finally:
            await client.disconnect()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_logic())
    loop.close()
