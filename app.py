# app.py
from flask import Flask, request, redirect, url_for, session, flash, jsonify
import os
from datetime import datetime
import pytz # تأكد من تثبيت pytz: pip install pytz
import json 

app = Flask(__name__)
# مفتاح سري قوي جداً. غير هذا المفتاح في تطبيقك الحقيقي
app.secret_key = 'your_super_secret_key_here_please_change_this_to_a_strong_one_for_security_v2' 

# =========================================================
# بيانات مؤقتة (عادةً ما تكون في قاعدة بيانات)
# =========================================================
# بيانات المستخدمين
USERS = {
    "1234": {"password": "12341234", "role": "admin"} # بيانات المدير
}

ACADEMY_NAME = "أكاديمية المعرفة" # اسم الأكاديمية

GLOBAL_ANNOUNCEMENTS = [
    {'id': 1, 'title': 'ورشة عمل جديدة: أساسيات بايثون للمبتدئين', 'description': 'انضموا إلينا في ورشة عمل تفاعلية لتعلم أساسيات لغة بايثون.', 'media_url': '', 'content_type': 'announcement'},
    {'id': 2, 'title': 'إعلان هام: تحديث محتوى الهاكر الأخلاقي', 'description': 'تم إضافة قسم جديد حول أدوات اختبار الاختراق المتقدمة.', 'media_url': '', 'content_type': 'announcement'},
    {'id': 3, 'title': 'فيديو جديد: مقدمة في الأمن السيبراني', 'description': 'شاهد الفيديو التعريفي الشامل حول أساسيات الأمن السيبراني.', 'media_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'content_type': 'video'}, # غيّر هذا الرابط لفيديو يوتيوب حقيقي ومناسب (embed URL)
    {'id': 4, 'title': 'صورة توضيحية لرحلة التعلم', 'description': 'خارطة طريق مبسطة لرحلتك في مجال الأمن السيبراني والبرمجة.', 'media_url': 'learn_roadmap.png', 'content_type': 'image'} # تأكد من وجود learn_roadmap.png في مجلد static
]

EDUCATIONAL_VIDEOS = [
    {'id': 1, 'title': 'مقدمة في Kali Linux', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ'}, # غيّر هذا الرابط
    {'id': 2, 'title': 'أساسيات البرمجة بلغة Python', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ'}, # غيّر هذا الرابط
]

STUDENT_QUERIES = [] # للاستفسارات

# نظام الدردشة البسيط (الرسائل)
CHAT_MESSAGES = []

# محرر الأكواد (محتوى الكود المشترك)
SHARED_CODE_CONTENT = {
    "python": "# اكتب كود بايثون هنا\n",
    "html": "\n",
    "css": "/* اكتب كود CSS هنا */\n",
    "javascript": "// اكتب كود JavaScript هنا\n"
}

# قائمة المستخدمين الذين سجلوا الدخول مؤخرًا (للمدير)
RECENT_LOGINS = []

# =========================================================
# دوال مساعدة لإنشاء HTML
# =========================================================

def get_current_time():
    """تُرجع الوقت الحالي في توقيت المغرب."""
    current_time_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    morocco_timezone = pytz.timezone('Africa/Casablanca')
    return current_time_utc.astimezone(morocco_timezone).strftime('%Y-%m-%d %H:%M:%S')

def get_flash_messages_html(flash_messages):
    """تُولد HTML لرسائل الفلاش."""
    flash_html = ""
    for category, message in flash_messages:
        flash_html += f"""
        <div class="flash-message flash-{category}">
            {message}
        </div>
        """
    return flash_html

def get_login_html(academy_app_name, flash_messages):
    return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - {academy_app_name}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background-color: #2c3e50;
            background-image: url('{url_for('static', filename='login_background.jpg')}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            backdrop-filter: blur(3px);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            direction: rtl;
        }}
        .login-container {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            text-align: center;
            width: 380px;
            max-width: 90%;
            animation: fadeIn 0.8s ease-out;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-50px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .logo-container {{
            width: 150px;
            height: 150px;
            margin: 0 auto 25px auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .logo {{
            max-width: 100%;
            max-height: 100%;
            height: auto;
            width: auto;
            border-radius: 50%;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }}
        h2 {{
            color: #3498db;
            margin-bottom: 30px;
            font-size: 28px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }}
        input {{
            width: calc(100% - 24px);
            padding: 12px;
            margin-bottom: 20px;
            border: 1px solid #c8d6e5;
            border-radius: 6px;
            font-size: 17px;
            transition: border-color 0.3s ease;
            direction: rtl;
        }}
        input:focus {{
            border-color: #28a745;
            outline: none;
            box-shadow: 0 0 5px rgba(40, 167, 69, 0.5);
        }}
        button {{
            width: 100%;
            padding: 14px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 19px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }}
        button:hover {{
            background-color: #218838;
            transform: translateY(-2px);
        }}
        button:active {{
            transform: translateY(0);
        }}
        .flash-message {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .flash-error {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo-container">
            <img src="{url_for('static', filename='academy_logo.png')}" alt="{academy_app_name}" class="logo">
        </div>
        <h2>تسجيل الدخول إلى {academy_app_name}</h2>
        {get_flash_messages_html(flash_messages)}
        <form method="post">
            <input type="text" name="username" placeholder="اسم المستخدم" required>
            <input type="password" name="password" placeholder="كلمة المرور" required>
            <button type="submit">تسجيل الدخول</button>
        </form>
    </div>
</body>
</html>
"""

def get_dashboard_html(academy_app_name, logged_in_username, user_role, display_role, page_heading_text, 
                       global_announcements, latest_activity, educational_videos, student_queries, 
                       chat_messages, shared_code_content, recent_logins, section_to_display, flash_messages):
    
    # رسالة ترحيبية خاصة للطالب
    welcome_message_html = ""
    if user_role == 'student':
        welcome_message_html = f"""
            <p style="font-size: 18px; line-height: 1.6;">
                مرحباً بك يا <span style="color: #28a745; font-weight: bold;">{logged_in_username}</span>!
                هذه <span style="font-weight: bold;">أكاديمية المعرفة</span> مع الأستاذ <span style="color: #3498db; font-weight: bold;">عبد الصمد</span>.
                استخدم الأزرار أعلاه لاستكشاف محتوى الأكاديمية والتواصل مع الإدارة.
            </p>
        """
    elif user_role == 'admin':
        welcome_message_html = """
            <p>مرحباً بك يا مدير الأكاديمية. من هنا يمكنك إدارة المحتوى، الإعلانات، والتعامل مع استفسارات الطلاب.</p>
        """


    # بناء الأقسام المختلفة بناءً على section_to_display
    section_content_html = ""
    if section_to_display == 'dashboard':
        latest_activity_html = ""
        if global_announcements: # نستخدم آخر إعلان كأحدث نشاط
            latest_activity_data = global_announcements[-1]
            media_html = ""
            if latest_activity_data.get('media_url'):
                if 'youtube.com/embed' in latest_activity_data['media_url'] or 'youtu.be/' in latest_activity_data['media_url']: # رابط يوتيوب embed
                    media_html = f"""
                        <div class="activity-video-container">
                            <iframe src="{latest_activity_data['media_url']}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                        </div>
                    """
                elif any(ext in latest_activity_data['media_url'].lower() for ext in ['.png', '.jpg', '.jpeg', '.gif']): # صورة
                    media_html = f"""
                        <img src="{url_for('static', filename=latest_activity_data['media_url'])}" alt="{latest_activity_data['title']}" class="activity-media">
                    """
            latest_activity_html = f"""
                <div style="background-color: #f8fcfd; border: 1px solid #e0eaf1; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.08);">
                    <h4 style="color: #3498db; margin-top: 0; font-size: 20px;">{latest_activity_data['title']}</h4>
                    <p style="font-size: 16px;">{latest_activity_data['description']}</p>
                    {media_html}
                </div>
            """
        else:
            latest_activity_html = """<p style="text-align: center; color: #888; font-style: italic;">لا توجد أنشطة جديدة لعرضها حالياً.</p>"""

        section_content_html = f"""
            <div class="section-content">
                <h3>أحدث الأنشطة والمبادرات</h3>
                <p>تعرف على أحدث الأنشطة والمبادرات الجديدة التي أطلقتها الأكاديمية.</p>
                {latest_activity_html}
            </div>
        """
    elif section_to_display == 'hacking_basics':
        section_content_html = """
            <div class="section-content">
                <h3>أساسيات الهاكر الأخلاقي</h3>
                <p>هنا ستجد مقدمة شاملة لمفاهيم الهاكر الأخلاقي، بما في ذلك أنواع الهجمات الشائعة، وكيفية حماية الأنظمة. هذا القسم يهدف إلى تزويدك بالمعرفة الأساسية التي تحتاجها لفهم عالم الأمن السيبراني.</p>
                <p>الموضوعات التي سيتم تغطيتها:</p>
                <ul>
                    <li>مقدمة في الأمن السيبراني</li>
                    <li>أنواع التهديدات السيبرانية</li>
                    <li>أساسيات الشبكات</li>
                    <li>أدوات الهاكر الأخلاقي</li>
                    <li>الحماية من البرمجيات الخبيثة</li>
                </ul>
            </div>
        """
    elif section_to_display == 'ethical_details':
        section_content_html = """
            <div class="section-content">
                <h3>تفاصيل الهاكر الأخلاقي المتقدمة</h3>
                <p>يغوص هذا القسم بعمق في التقنيات المتقدمة المستخدمة في الهاكر الأخلاقي، مثل اختبار الاختراق المتقدم، تحليل الثغرات، وهندسة الاختراق العكسية. هذا الجزء مخصص للطلاب الذين لديهم فهم جيد للأساسيات ويرغبون في التوسع.</p>
                <p>الموضوعات المتقدمة:</p>
                <ul>
                    <li>اختبار الاختراق (Penetration Testing)</li>
                    <li>هندسة عكسية للبرمجيات</li>
                    <li>تحليل الثغرات (Vulnerability Analysis)</li>
                    <li>أمن تطبيقات الويب</li>
                    <li>الاستجابة للحوادث الأمنية</li>
                </ul>
            </div>
        """
    elif section_to_display == 'programming_fundamentals':
        section_content_html = """
            <div class="section-content">
                <h3>أساسيات البرمجة</h3>
                <p>تعلم أساسيات البرمجة من خلال لغة بايثون، والتي تعتبر من أقوى وأسهل اللغات للتعلم. سيتضمن هذا القسم المفاهيم الأساسية مثل المتغيرات، الدوال، الحلقات، والهياكل البيانية. ستكون قادراً على بناء برامج بسيطة وفهم كيفية عمل الخوارزميات.</p>
                <p>ما ستتعلمه:</p>
                <ul>
                    <li>مقدمة في بايثون</li>
                    <li>أنواع البيانات والمتغيرات</li>
                    <li>الشروط والحلقات التكرارية</li>
                    <li>الدوال والموديلات</li>
                    <li>مقدمة في البرمجة الكائنية</li>
                </ul>
            </div>
        """
    elif section_to_display == 'announcements':
        announcements_list_html = ""
        if global_announcements:
            for announcement in reversed(global_announcements): # عرض الأحدث أولاً
                media_html = ""
                if announcement.get('media_url'):
                    if 'youtube.com/embed' in announcement['media_url'] or 'youtu.be/' in announcement['media_url']:
                        media_html = f"""
                            <div class="activity-video-container">
                                <iframe src="{announcement['media_url']}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                            </div>
                        """
                    elif any(ext in announcement['media_url'].lower() for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                        media_html = f"""
                            <img src="{url_for('static', filename=announcement['media_url'])}" alt="{announcement['title']}" class="activity-media">
                        """
                announcements_list_html += f"""
                    <div style="background-color: #f8fcfd; border: 1px solid #e0eaf1; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.08);">
                        <h4 style="color: #3498db; margin-top: 0; font-size: 20px;">{announcement['title']}</h4>
                        <p style="font-size: 16px;">{announcement['description']}</p>
                        {media_html}
                    </div>
                """
        else:
            announcements_list_html = """<p style="text-align: center; color: #888; font-style: italic;">لا توجد إعلانات لعرضها حالياً.</p>"""

        section_content_html = f"""
            <div class="section-content">
                <h3>إعلانات الأكاديمية</h3>
                {announcements_list_html}
            </div>
        """
    elif section_to_display == 'videos':
        videos_grid_html = ""
        if educational_videos:
            for video in educational_videos:
                videos_grid_html += f"""
                    <div class="video-item">
                        <h4>{video['title']}</h4>
                        <iframe src="{video['url']}" allowfullscreen></iframe>
                    </div>
                """
        else:
            videos_grid_html = """<p style="text-align: center; color: #888; font-style: italic; grid-column: 1 / -1;">لا توجد فيديوهات لعرضها حالياً.</p>"""

        section_content_html = f"""
            <div class="section-content">
                <h3>فيديوهات تعليمية</h3>
                <div class="video-grid">
                    {videos_grid_html}
                </div>
            </div>
        """
    elif section_to_display == 'contact_admin':
        section_content_html = f"""
            <div class="section-content">
                <h3>إرسال استفسار للمدير</h3>
                <div class="form-section">
                    <form method="post" action="{url_for('submit_query_to_admin')}">
                        <div class="form-group">
                            <label for="query_text">اكتب استفسارك هنا:</label>
                            <textarea id="query_text" name="query_text" required></textarea>
                        </div>
                        <button type="submit">إرسال الاستفسار</button>
                    </form>
                </div>
            </div>
        """
    elif user_role == 'admin' and section_to_display == 'admin_inbox':
        inbox_items_html = ""
        if student_queries:
            for query in reversed(student_queries):
                inbox_items_html += f"""
                    <div class="inbox-item">
                        <strong>من:</strong> {query['username']}
                        <span class="timestamp">{query['time']}</span>
                        <p>{query['query']}</p>
                    </div>
                """
        else:
            inbox_items_html = """<p style="text-align: center; color: #888; font-style: italic;">لا توجد استفسارات حالياً.</p>"""

        recent_logins_html = ""
        if recent_logins:
            for login_entry in reversed(recent_logins):
                recent_logins_html += f"""
                    <div class="inbox-item">
                        <strong>المستخدم:</strong> {login_entry['username']}
                        <span class="timestamp">{login_entry['time']}</span>
                    </div>
                """
        else:
            recent_logins_html = """<p style="text-align: center; color: #888; font-style: italic;">لا توجد عمليات تسجيل دخول حديثة.</p>"""


        section_content_html = f"""
            <div class="section-content">
                <h3>صندوق استفسارات الطلاب</h3>
                {inbox_items_html}
            </div>
            <div class="admin-controls" style="margin-top: 30px;">
                <h3>المستخدمون النشطون (تسجيلات الدخول الحديثة)</h3>
                <p>هذه قائمة بآخر المستخدمين الذين سجلوا الدخول إلى النظام.</p>
                {recent_logins_html}
            </div>
            <div class="admin-controls" style="margin-top: 30px;">
                <h3>إدارة المحتوى والإعلانات</h3>
                 <form method="post" action="{url_for('add_new_content')}">
                    <div class="form-group">
                        <label for="admin_content_title">عنوان المحتوى:</label>
                        <input type="text" id="admin_content_title" name="title" required>
                    </div>
                    <div class="form-group">
                        <label for="admin_content_description">الوصف:</label>
                        <textarea id="admin_content_description" name="description" required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="admin_content_media_url">رابط الوسائط (فيديو يوتيوب embed أو مسار صورة من static):</label>
                        <input type="text" id="admin_content_media_url" name="media_url">
                    </div>
                    <div class="form-group">
                        <label for="admin_content_type">نوع المحتوى:</label>
                        <select id="admin_content_type" name="type">
                            <option value="announcement">إعلان</option>
                            <option value="video">فيديو</option>
                            <option value="image">صورة</option>
                        </select>
                    </div>
                    <button type="submit">إضافة محتوى جديد</button>
                </form>
            </div>
        """
    elif section_to_display == 'chat':
        chat_messages_html = ""
        if chat_messages:
            for msg in chat_messages:
                # تحديد ما إذا كانت الرسالة مرسلة من المستخدم الحالي
                message_class = "sent-message" if msg['sender'] == logged_in_username else "received-message"
                chat_messages_html += f"""
                    <div class="chat-message {message_class}">
                        <div class="message-header">
                            <strong>{msg['sender']}</strong>
                            <span class="message-time">{msg['time']}</span>
                        </div>
                        <p>{msg['message']}</p>
                    </div>
                """
        else:
            chat_messages_html = """<p style="text-align: center; color: #888; font-style: italic;">لا توجد رسائل بعد. ابدأ المحادثة!</p>"""

        section_content_html = f"""
            <div class="section-content">
                <h3>التواصل مع الآخرين</h3>
                <div class="chat-container">
                    <div class="chat-messages" id="chat-messages-container">
                        {chat_messages_html}
                    </div>
                    <div class="chat-input-form">
                        <form method="post" action="{url_for('send_chat_message')}" onsubmit="return submitChatMessage()">
                            <textarea id="chat_message_text" name="message" placeholder="اكتب رسالتك هنا..." required onkeydown="if(event.keyCode==13 && !event.shiftKey) {{ this.form.submit(); return false; }}"></textarea>
                            <button type="submit">إرسال</button>
                        </form>
                    </div>
                </div>
                <script>
                    function scrollToBottom() {{
                        var chatContainer = document.getElementById('chat-messages-container');
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                    }}
                    document.addEventListener('DOMContentLoaded', scrollToBottom);

                    function submitChatMessage() {{
                        // هذا سيرسل الرسالة ويعيد توجيه الصفحة، مما يؤدي إلى تحديث الدردشة
                        return true; 
                    }}
                </script>
            </div>
        """
    elif section_to_display == 'code_editor':
        section_content_html = f"""
            <div class="section-content">
                <h3>منصة كتابة الأكواد</h3>
                <p>يمكنك كتابة الأكواد هنا. لا يتم تنفيذ الكود، بل هو مخصص للمشاركة والمراجعة.</p>
                
                <div class="code-editor-controls">
                    <label for="code_language">اختر لغة الكود:</label>
                    <select id="code_language" onchange="loadCodeContent()">
                        <option value="python">Python</option>
                        <option value="html">HTML</option>
                        <option value="css">CSS</option>
                        <option value="javascript">JavaScript</option>
                    </select>
                    <button onclick="saveCodeContent()">حفظ الكود</button>
                    <button onclick="copyCodeContent()">نسخ الكود</button>
                </div>

                <textarea id="code_editor_textarea" class="code-editor-area" rows="20">{shared_code_content.get('python', '')}</textarea>
            </div>
            
            <script>
                var currentLanguage = 'python';
                var codeContents = {json.dumps(shared_code_content)}; 

                function loadCodeContent() {{
                    currentLanguage = document.getElementById('code_language').value;
                    document.getElementById('code_editor_textarea').value = codeContents[currentLanguage];
                }}

                function saveCodeContent() {{
                    var code = document.getElementById('code_editor_textarea').value;
                    fetch('{url_for('save_shared_code')}', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{ language: currentLanguage, code: code }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        alert(data.message); 
                        codeContents[currentLanguage] = code; 
                    }})
                    .catch(error => console.error('Error:', error));
                }}

                function copyCodeContent() {{
                    var copyText = document.getElementById('code_editor_textarea');
                    copyText.select();
                    document.execCommand('copy');
                    alert('تم نسخ الكود!');
                }}

                document.addEventListener('DOMContentLoaded', loadCodeContent);
            </script>
        """
    else: 
        section_content_html = f"""
            <div class="section-content">
                <h3>مرحباً بك!</h3>
                {welcome_message_html}
            </div>
        """


    return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_heading_text} - {academy_app_name}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            background-color: #f4f7f6;
            direction: rtl;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            display: flex;
            align-items: center;
        }}
        .header h1 .logo {{
            height: 40px;
            margin-left: 10px;
            border-radius: 50%;
        }}
        .user-info {{
            font-size: 16px;
        }}
        .user-info a {{
            color: #3498db;
            text-decoration: none;
            margin-right: 15px;
            font-weight: bold;
            transition: color 0.3s ease;
        }}
        .user-info a:hover {{
            color: #e74c3c;
        }}
        .container {{
            padding: 20px 30px;
            max-width: 1200px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        .flash-message {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .flash-error {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .welcome-section {{
            background-color: #eaf6fe;
            border-left: 5px solid #3498db;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .welcome-section h2 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .welcome-section p {{
            color: #555;
            font-size: 18px;
            line-height: 1.6;
        }}
        .action-buttons-group {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
            margin-bottom: 40px;
        }}
        .action-buttons-group button {{
            background-color: #3498db;
            color: white;
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            min-height: 80px;
        }}
        .action-buttons-group button:hover {{
            background-color: #2980b9;
            transform: translateY(-3px);
        }}
        .action-buttons-group button:active {{
            transform: translateY(0);
        }}
        .action-buttons-group button i {{
            margin-left: 10px;
            font-size: 24px;
        }}
        .section-content {{
            background-color: #f8fcfd;
            border: 1px solid #e0eaf1;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        }}
        .section-content h3 {{
            color: #3498db;
            margin-bottom: 15px;
            font-size: 22px;
            border-bottom: 2px solid #e0eaf1;
            padding-bottom: 10px;
        }}
        .section-content p {{
            line-height: 1.8;
            color: #444;
        }}
        .video-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .video-item {{
            background-color: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .video-item h4 {{
            padding: 10px;
            margin: 0;
            background-color: #f0f0f0;
            color: #333;
            font-size: 18px;
            text-align: center;
        }}
        .video-item iframe {{
            width: 100%;
            height: 200px;
            border: none;
        }}
        .form-section {{
            padding: 20px;
            background-color: #eaf6fe;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .form-section label {{
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }}
        .form-section textarea {{
            width: calc(100% - 20px);
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            resize: vertical;
            min-height: 100px;
            font-size: 16px;
            direction: rtl;
        }}
        .form-section button {{
            background-color: #28a745;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 17px;
            margin-top: 15px;
            transition: background-color 0.3s ease;
        }}
        .form-section button:hover {{
            background-color: #218838;
        }}
        .inbox-item {{
            background-color: #f9f9f9;
            border: 1px solid #eee;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .inbox-item strong {{
            color: #3498db;
        }}
        .inbox-item .timestamp {{
            font-size: 0.9em;
            color: #888;
            margin-right: 10px;
        }}
        .inbox-item p {{
            margin-top: 10px;
            margin-bottom: 0;
        }}
        .admin-controls {{
            margin-top: 30px;
            background-color: #f0f8ff;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #d0e8f7;
        }}
        .admin-controls h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        .admin-controls .form-group {{
            margin-bottom: 15px;
        }}
        .admin-controls label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #444;
        }}
        .admin-controls input[type="text"],
        .admin-controls textarea,
        .admin-controls select {{
            width: calc(100% - 22px);
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
            direction: rtl;
        }}
        .admin-controls textarea {{
            min-height: 80px;
            resize: vertical;
        }}
        .admin-controls button {{
            background-color: #28a745;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 17px;
            margin-top: 15px;
            transition: background-color 0.3s ease;
        }}
        .admin-controls button:hover {{
            background-color: #218838;
        }}
        .activity-media {{
            width: 100%;
            height: auto;
            max-width: 100%;
            border-radius: 8px;
            margin-top: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .activity-video-container {{
            position: relative;
            width: 100%;
            height: 0;
            padding-bottom: 56.25%;
            margin-top: 15px;
            border-radius: 8px;
            overflow: hidden;
        }}
        .activity-video-container iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }}
        .fa {{ }}

        /* Chat Specific CSS */
        .chat-container {{
            display: flex;
            flex-direction: column;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background-color: #fdfdfd;
        }}
        .chat-messages {{
            flex-grow: 1;
            padding: 15px;
            overflow-y: auto;
            max-height: 500px; 
            display: flex;
            flex-direction: column;
        }}
        .chat-message {{
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            word-wrap: break-word;
        }}
        .sent-message {{
            align-self: flex-end;
            background-color: #dcf8c6; 
            color: #333;
        }}
        .received-message {{
            align-self: flex-start;
            background-color: #e0f2f7; 
            color: #333;
        }}
        .message-header {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }}
        .message-header strong {{
            color: #333;
        }}
        .message-time {{
            font-size: 0.75em;
            color: #999;
            margin-right: 10px;
        }}
        .chat-input-form {{
            border-top: 1px solid #eee;
            padding: 15px;
            background-color: #f0f0f0;
            display: flex;
        }}
        .chat-input-form textarea {{
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 20px;
            margin-left: 10px;
            resize: none;
            height: 40px; 
            line-height: 20px; 
            overflow: hidden;
            direction: rtl;
        }}
        .chat-input-form button {{
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }}
        .chat-input-form button:hover {{
            background-color: #218838;
        }}

        /* Code Editor Specific CSS */
        .code-editor-controls {{
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .code-editor-controls select,
        .code-editor-controls button {{
            padding: 8px 15px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .code-editor-controls select {{
            background-color: #f8f8f8;
        }}
        .code-editor-controls button {{
            background-color: #3498db;
            color: white;
            border-color: #3498db;
        }}
        .code-editor-controls button:hover {{
            background-color: #2980b9;
            border-color: #2980b9;
        }}
        .code-editor-area {{
            width: calc(100% - 20px);
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            background-color: #f5f5f5;
            color: #333;
            tab-size: 4;
            -moz-tab-size: 4;
            outline: none;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
            direction: ltr; 
            unicode-bidi: embed; 
        }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1>
            <img src="{url_for('static', filename='academy_logo.png')}" alt="شعار {academy_app_name}" class="logo">
            {academy_app_name}
        </h1>
        <div class="user-info">
            مرحباً بك، <strong>{logged_in_username}</strong> ({display_role})
            <a href="{url_for('logout')}">تسجيل الخروج</a>
        </div>
    </div>

    <div class="container">
        {get_flash_messages_html(flash_messages)}

        <div class="welcome-section">
            <h2>{page_heading_text}</h2>
            {welcome_message_html}
        </div>

        <div class="action-buttons-group">
            {'<button onclick="window.location.href=\'{}\''.format(url_for('show_hacking_basics')) + '">أساسيات الهاكر الأخلاقي <i class="fa fa-skull-crossbones"></i></button>' if user_role == 'student' else ''}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('show_ethical_details')) + '">تفاصيل الهاكر الأخلاقي <i class="fa fa-user-secret"></i></button>' if user_role == 'student' else ''}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('show_programming_fundamentals')) + '">أساسيات البرمجة <i class="fa fa-code"></i></button>' if user_role == 'student' else ''}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('show_announcements_view')) + '">إعلانات الأكاديمية <i class="fa fa-bullhorn"></i></button>' if user_role == 'student' else ''}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('student_videos_view')) + '">فيديوهات تعليمية <i class="fa fa-video"></i></button>' if user_role == 'student' else ''}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('submit_query_to_admin')) + '">إرسال استفسار للمدير <i class="fa fa-question-circle"></i></button>' if user_role == 'student' else ''}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('show_chat_view')) + '">التواصل (الدردشة) <i class="fa fa-comments"></i></button>'}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('show_code_editor_view')) + '">منصة الأكواد <i class="fa fa-terminal"></i></button>'}


            {'<button onclick="window.location.href=\'{}\''.format(url_for('admin_inbox_view')) + '">استعراض استفسارات الطلاب <i class="fa fa-inbox"></i></button>' if user_role == 'admin' else ''}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('show_announcements_view')) + '">إدارة الإعلانات <i class="fa fa-bullhorn"></i></button>' if user_role == 'admin' else ''}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('student_videos_view')) + '">إدارة الفيديوهات <i class="fa fa-video"></i></button>' if user_role == 'admin' else ''}
            {'<button onclick="window.location.href=\'{}\''.format(url_for('show_programming_fundamentals')) + '">إدارة محتوى البرمجة <i class="fa fa-code"></i></button>' if user_role == 'admin' else ''}
        </div>

        {section_content_html}

    </div>
</body>
</html>
"""


# =========================================================
# مسارات التطبيق (Routes)
# =========================================================

@app.route('/')
def home():
    if 'current_user_name' in session:
        return redirect(url_for('dashboard_view'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'current_user_name' in session:
        return redirect(url_for('dashboard_view'))

    # استخلاص رسائل الفلاش لعرضها مرة واحدة فقط
    flashed_messages = list(session.pop('_flashed_messages', []))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = USERS.get(username)

        # التحقق من دخول المدير
        if user_data and user_data['password'] == password and user_data['role'] == 'admin':
            session['current_user_name'] = username
            session['current_user_role'] = user_data['role']
            RECENT_LOGINS.append({'username': username, 'time': get_current_time()})
            flash('تم تسجيل الدخول بنجاح كمدير!', 'success')
            return redirect(url_for('dashboard_view'))
        
        # التحقق من دخول الطالب (أي اسم مستخدم وكلمة مرور "aaa")
        elif password == 'aaa': 
            session['current_user_name'] = username 
            session['current_user_role'] = 'student'
            RECENT_LOGINS.append({'username': username, 'time': get_current_time()})
            flash(f'مرحباً بك يا {username}!', 'success')
            return redirect(url_for('dashboard_view'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'error')
            # بعد الفلاش، نُعيد استخلاص الرسائل إذا كانت هناك رسالة جديدة
            flashed_messages = list(session.pop('_flashed_messages', []))

    return get_login_html(academy_app_name=ACADEMY_NAME, flash_messages=flashed_messages)

@app.route('/dashboard')
def dashboard_view():
    if 'current_user_name' not in session:
        flash('الرجاء تسجيل الدخول أولاً للوصول إلى لوحة التحكم.', 'error')
        return redirect(url_for('login_page'))

    display_role_text = {
        'admin': 'مدير الأكاديمية',
        'student': 'طالب'
    }.get(session.get('current_user_role'), 'مستخدم')

    page_heading_text = "لوحة تحكم المدير" if session.get('current_user_role') == 'admin' else "صفحة الطالب الرئيسية"

    latest_activity = GLOBAL_ANNOUNCEMENTS[-1] if GLOBAL_ANNOUNCEMENTS else None
    
    flashed_messages = list(session.pop('_flashed_messages', []))

    return get_dashboard_html(academy_app_name=ACADEMY_NAME,
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role=display_role_text,
                           page_heading_text=page_heading_text,
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=latest_activity, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES,
                           shared_code_content=SHARED_CODE_CONTENT,
                           recent_logins=RECENT_LOGINS,
                           section_to_display="dashboard",
                           flash_messages=flashed_messages)


@app.route('/logout')
def logout():
    session.pop('current_user_name', None)
    session.pop('current_user_role', None)
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('login_page'))

# =========================================================
# صفحات إضافية (جميعها ستُعرض الآن ضمن dashboard كأقسام)
# =========================================================

@app.route('/show_hacking_basics')
def show_hacking_basics():
    if 'current_user_name' not in session: return redirect(url_for('login_page'))
    flashed_messages = list(session.pop('_flashed_messages', []))
    return get_dashboard_html(academy_app_name=ACADEMY_NAME, 
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role="", 
                           page_heading_text="أساسيات الهاكر الأخلاقي",
                           section_to_display="hacking_basics",
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=None, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES,
                           shared_code_content=SHARED_CODE_CONTENT,
                           recent_logins=RECENT_LOGINS,
                           flash_messages=flashed_messages)

@app.route('/show_ethical_details')
def show_ethical_details():
    if 'current_user_name' not in session: return redirect(url_for('login_page'))
    flashed_messages = list(session.pop('_flashed_messages', []))
    return get_dashboard_html(academy_app_name=ACADEMY_NAME, 
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role="",
                           page_heading_text="تفاصيل الهاكر الأخلاقي",
                           section_to_display="ethical_details",
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=None, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES,
                           shared_code_content=SHARED_CODE_CONTENT,
                           recent_logins=RECENT_LOGINS,
                           flash_messages=flashed_messages)

@app.route('/show_programming_fundamentals')
def show_programming_fundamentals():
    if 'current_user_name' not in session: return redirect(url_for('login_page'))
    flashed_messages = list(session.pop('_flashed_messages', []))
    return get_dashboard_html(academy_app_name=ACADEMY_NAME, 
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role="",
                           page_heading_text="أساسيات البرمجة",
                           section_to_display="programming_fundamentals",
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=None, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES,
                           shared_code_content=SHARED_CODE_CONTENT,
                           recent_logins=RECENT_LOGINS,
                           flash_messages=flashed_messages)

@app.route('/show_announcements_view')
def show_announcements_view():
    if 'current_user_name' not in session: return redirect(url_for('login_page'))
    flashed_messages = list(session.pop('_flashed_messages', []))
    return get_dashboard_html(academy_app_name=ACADEMY_NAME, 
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role="",
                           page_heading_text="إعلانات الأكاديمية",
                           section_to_display="announcements",
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=None, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES,
                           shared_code_content=SHARED_CODE_CONTENT,
                           recent_logins=RECENT_LOGINS,
                           flash_messages=flashed_messages)

@app.route('/student_videos_view')
def student_videos_view():
    if 'current_user_name' not in session: return redirect(url_for('login_page'))
    flashed_messages = list(session.pop('_flashed_messages', []))
    return get_dashboard_html(academy_app_name=ACADEMY_NAME, 
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role="",
                           page_heading_text="فيديوهات تعليمية",
                           section_to_display="videos",
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=None, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES,
                           shared_code_content=SHARED_CODE_CONTENT,
                           recent_logins=RECENT_LOGINS,
                           flash_messages=flashed_messages)

@app.route('/submit_query_to_admin', methods=['GET', 'POST'])
def submit_query_to_admin():
    if 'current_user_name' not in session: return redirect(url_for('login_page'))
    
    flashed_messages = list(session.pop('_flashed_messages', []))

    if request.method == 'POST':
        query_text = request.form['query_text']
        query_time = get_current_time() 

        STUDENT_QUERIES.append({
            'username': session['current_user_name'],
            'query': query_text,
            'time': query_time
        })
        flash('تم إرسال استفسارك بنجاح إلى الإدارة!', 'success')
        return redirect(url_for('dashboard_view'))
    
    return get_dashboard_html(academy_app_name=ACADEMY_NAME, 
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role="",
                           page_heading_text="إرسال استفسار للمدير",
                           section_to_display="contact_admin",
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=None, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES,
                           shared_code_content=SHARED_CODE_CONTENT,
                           recent_logins=RECENT_LOGINS,
                           flash_messages=flashed_messages)

@app.route('/admin_inbox_view') 
def admin_inbox_view():
    if 'current_user_name' not in session or session['current_user_role'] != 'admin':
        flash('غير مصرح لك بالوصول لهذه الصفحة.', 'error')
        return redirect(url_for('login_page'))
    
    flashed_messages = list(session.pop('_flashed_messages', []))
    
    return get_dashboard_html(academy_app_name=ACADEMY_NAME, 
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role="",
                           page_heading_text="صندوق استفسارات الطلاب & سجل الدخول",
                           section_to_display="admin_inbox",
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=None, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES,
                           shared_code_content=SHARED_CODE_CONTENT,
                           recent_logins=RECENT_LOGINS, 
                           flash_messages=flashed_messages)


@app.route('/add_new_content', methods=['POST'])
def add_new_content():
    if 'current_user_name' not in session or session['current_user_role'] != 'admin':
        flash('غير مصرح لك بإضافة محتوى.', 'error')
        return redirect(url_for('login_page'))
    
    title = request.form['title']
    description = request.form['description']
    media_url = request.form['media_url']
    content_type = request.form['type'] 

    # استخدام ID فريد لكل إعلان/محتوى
    next_id = max([a['id'] for a in GLOBAL_ANNOUNCEMENTS]) + 1 if GLOBAL_ANNOUNCEMENTS else 1

    if content_type == 'announcement' or content_type == 'image': 
        GLOBAL_ANNOUNCEMENTS.append({'id': next_id, 'title': title, 'description': description, 'media_url': media_url, 'content_type': content_type})
    elif content_type == 'video':
        # استخدام نفس الـ ID للإعلان العام أو الـ ID الخاص بالفيديو
        next_video_id = max([v['id'] for v in EDUCATIONAL_VIDEOS]) + 1 if EDUCATIONAL_VIDEOS else 1
        EDUCATIONAL_VIDEOS.append({'id': next_video_id, 'title': title, 'url': media_url})
        # يمكن أيضاً إضافة الفيديو كإعلان عام ليظهر في لوحة التحكم الرئيسية
        GLOBAL_ANNOUNCEMENTS.append({'id': next_id, 'title': title, 'description': description, 'media_url': media_url, 'content_type': content_type})
    
    flash('تم إضافة المحتوى بنجاح!', 'success')
    return redirect(url_for('admin_inbox_view')) 


# =========================================================
# مسارات جديدة للدردشة ومحرر الأكواد
# =========================================================

@app.route('/chat_view')
def show_chat_view():
    if 'current_user_name' not in session:
        flash('الرجاء تسجيل الدخول أولاً للوصول إلى الدردشة.', 'error')
        return redirect(url_for('login_page'))
    
    flashed_messages = list(session.pop('_flashed_messages', []))
    
    display_role_text = {
        'admin': 'مدير الأكاديمية',
        'student': 'طالب'
    }.get(session.get('current_user_role'), 'مستخدم')

    return get_dashboard_html(academy_app_name=ACADEMY_NAME,
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role=display_role_text,
                           page_heading_text="التواصل المباشر",
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=None, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES, 
                           shared_code_content=SHARED_CODE_CONTENT,
                           recent_logins=RECENT_LOGINS,
                           section_to_display="chat",
                           flash_messages=flashed_messages)

@app.route('/send_chat_message', methods=['POST'])
def send_chat_message():
    if 'current_user_name' not in session:
        flash('الرجاء تسجيل الدخول لإرسال الرسائل.', 'error')
        return redirect(url_for('login_page'))
    
    message_text = request.form['message']
    if message_text.strip(): 
        CHAT_MESSAGES.append({
            'sender': session['current_user_name'],
            'message': message_text.strip(),
            'time': get_current_time()
        })
        flash('تم إرسال رسالتك!', 'success')
    else:
        flash('الرسالة لا يمكن أن تكون فارغة.', 'error')
    
    return redirect(url_for('show_chat_view'))


@app.route('/code_editor_view')
def show_code_editor_view():
    if 'current_user_name' not in session:
        flash('الرجاء تسجيل الدخول أولاً للوصول إلى محرر الأكواد.', 'error')
        return redirect(url_for('login_page'))
    
    flashed_messages = list(session.pop('_flashed_messages', []))
    
    display_role_text = {
        'admin': 'مدير الأكاديمية',
        'student': 'طالب'
    }.get(session.get('current_user_role'), 'مستخدم')

    return get_dashboard_html(academy_app_name=ACADEMY_NAME,
                           logged_in_username=session['current_user_name'],
                           user_role=session['current_user_role'],
                           display_role=display_role_text,
                           page_heading_text="منصة كتابة الأكواد",
                           global_announcements=GLOBAL_ANNOUNCEMENTS, 
                           latest_activity=None, 
                           educational_videos=EDUCATIONAL_VIDEOS,
                           student_queries=STUDENT_QUERIES,
                           chat_messages=CHAT_MESSAGES,
                           shared_code_content=SHARED_CODE_CONTENT, 
                           recent_logins=RECENT_LOGINS,
                           section_to_display="code_editor",
                           flash_messages=flashed_messages)


@app.route('/save_shared_code', methods=['POST'])
def save_shared_code():
    if 'current_user_name' not in session:
        return jsonify({'status': 'error', 'message': 'غير مصرح لك بحفظ الكود.'}), 401
    
    data = request.json
    language = data.get('language')
    code = data.get('code')

    if language in SHARED_CODE_CONTENT:
        SHARED_CODE_CONTENT[language] = code
        return jsonify({'status': 'success', 'message': f'تم حفظ كود {language} بنجاح!'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'لغة الكود غير مدعومة.'}), 400

# =========================================================
# تشغيل التطبيق
# =========================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')