from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from functools import wraps
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)

# Генерация безопасного секретного ключа
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# Настройки для продакшена
app.config['SESSION_COOKIE_SECURE'] = True  # Только HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Защита от XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Защита от CSRF

# Путь к файлу для сохранения данных
DATA_FILE = os.environ.get('DATA_FILE') or 'consilium_data.json'

# Аутентификация из переменных окружения
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH') or generate_password_hash('consilium2024')

# Email настройки
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.yandex.ru')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'consilium-events@yandex.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', 'consilium-events@yandex.com')

# Функция для загрузки данных из файла
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'events': SAMPLE_EVENTS,
        'stats': COMMUNITY_STATS,
        'testimonials': TESTIMONIALS
    }

# Функция для сохранения данных в файл
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# Функция отправки email
def send_email(subject, body):
    """Функция отправки email через SMTP с поддержкой SSL"""
    try:
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        
        # Добавляем текст письма
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Определяем тип подключения по порту
        if SMTP_PORT == 465:
            # SSL подключение
            import ssl
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # TLS подключение
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
        
        print(f"Email успешно отправлен на {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
        raise

# Декоратор для проверки авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Исходные данные (будут использоваться при первом запуске)
SAMPLE_EVENTS = [
    {
        'id': 1,
        'post_text': 'Чувствую непреодолимое желание обратиться к вам за помощью. Как научиться принимать себя таким, какой я есть?',
        'author': 'Анна К.',
        'likes': 1247,
        'event_date': datetime.now() + timedelta(days=3),
        'status': 'upcoming',
        'participants': 89,
        'category': 'self-acceptance',
        'tags': ['принятие себя', 'самопознание', 'внутренний рост'],
        'location': 'Москва, пространство "Точка"',
        'online_link': 'consilium://room/self-acceptance-talk'
    },
    {
        'id': 2,
        'post_text': 'Внутренний рост начинается с принятия своих теней. Кто готов поделиться опытом трансформации?',
        'author': 'Михаил Д.',
        'likes': 892,
        'event_date': datetime.now() + timedelta(days=7),
        'status': 'upcoming',
        'participants': 56,
        'category': 'transformation',
        'tags': ['трансформация', 'тени', 'юнгианская психология'],
        'location': 'Санкт-Петербург, центр "Пробуждение"',
        'online_link': 'consilium://room/shadow-work'
    },
    {
        'id': 3,
        'post_text': 'Медитация изменила мою жизнь. Но как сохранить состояние присутствия в повседневной суете?',
        'author': 'Елена С.',
        'likes': 2103,
        'event_date': datetime.now() - timedelta(days=2),
        'status': 'past',
        'participants': 142,
        'category': 'meditation',
        'tags': ['медитация', 'осознанность', 'практики присутствия'],
        'location': 'Онлайн',
        'recording_url': '/recordings/meditation-presence'
    },
    {
        'id': 4,
        'post_text': 'Успокоение приходит, когда перестаешь бороться с собой. Делюсь практиками, которые помогли мне.',
        'author': 'Дмитрий П.',
        'likes': 1567,
        'event_date': datetime.now() + timedelta(days=10),
        'status': 'upcoming',
        'participants': 34,
        'category': 'calming',
        'tags': ['успокоение', 'практики', 'внутренний покой'],
        'location': 'Екатеринбург, студия "Гармония"',
        'online_link': 'consilium://room/calming-practices'
    },
    {
        'id': 5,
        'post_text': 'Вдохновение - это не случайность, а результат внутренней работы. Как вы находите свой источник?',
        'author': 'София Р.',
        'likes': 923,
        'event_date': datetime.now() - timedelta(days=5),
        'status': 'past',
        'participants': 78,
        'category': 'inspiration',
        'tags': ['вдохновение', 'творчество', 'внутренний источник'],
        'location': 'Новосибирск, арт-пространство "Поток"',
        'recording_url': '/recordings/inspiration-source'
    }
]

COMMUNITY_STATS = {
    'total_users': 14127,
    'active_posts': 3847,
    'events_held': 89,
    'cities': 12
}

TESTIMONIALS = [
    {
        'id': 1,
        'author': 'Мария Петрова',
        'text': 'Consilium помог мне найти единомышленников и понять, что я не одинока в своих поисках.',
        'rating': 5,
        'event': 'Принятие себя'
    },
    {
        'id': 2,
        'author': 'Александр Иванов',
        'text': 'Каждый ивент - это глубокое погружение в себя и возможность услышать истории других.',
        'rating': 5,
        'event': 'Работа с тенью'
    },
    {
        'id': 3,
        'author': 'Елена Смирнова',
        'text': 'Благодаря обсуждениям я научилась медитировать и обрела внутренний покой.',
        'rating': 5,
        'event': 'Практики присутствия'
    }
]

# Загружаем данные при запуске
data = load_data()

@app.route('/')
def index():
    data = load_data()
    events = data.get('events', SAMPLE_EVENTS)
    
    # Преобразуем строки обратно в datetime объекты
    for event in events:
        if isinstance(event['event_date'], str):
            event['event_date'] = datetime.fromisoformat(event['event_date'])
    
    upcoming_events = [e for e in events if e['status'] == 'upcoming']
    past_events = [e for e in events if e['status'] == 'past']
    
    return render_template('index.html', 
                         upcoming_events=upcoming_events,
                         past_events=past_events,
                         stats=data.get('stats', COMMUNITY_STATS),
                         testimonials=data.get('testimonials', TESTIMONIALS))

@app.route('/events')
def events_page():
    data = load_data()
    events = data.get('events', SAMPLE_EVENTS)
    
    # Преобразуем строки обратно в datetime объекты
    for event in events:
        if isinstance(event['event_date'], str):
            event['event_date'] = datetime.fromisoformat(event['event_date'])
    
    category = request.args.get('category', 'all')
    if category != 'all':
        filtered_events = [e for e in events if e['category'] == category]
    else:
        filtered_events = events
    
    return render_template('events.html', 
                         events=filtered_events, 
                         current_category=category)

@app.route('/about')
def about():
    data = load_data()
    return render_template('about.html', stats=data.get('stats', COMMUNITY_STATS))

@app.route('/community')
def community():
    data = load_data()
    return render_template('community.html', 
                         testimonials=data.get('testimonials', TESTIMONIALS),
                         stats=data.get('stats', COMMUNITY_STATS))

@app.route('/api/events')
def get_events():
    data = load_data()
    return jsonify(data.get('events', SAMPLE_EVENTS))

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    data = load_data()
    events = data.get('events', SAMPLE_EVENTS)
    
    # Преобразуем строки обратно в datetime объекты
    for event in events:
        if isinstance(event['event_date'], str):
            event['event_date'] = datetime.fromisoformat(event['event_date'])
    
    event = next((e for e in events if e['id'] == event_id), None)
    if event:
        similar_events = [e for e in events 
                         if e['id'] != event_id and e['category'] == event['category']][:2]
        return render_template('event_detail.html', 
                             event=event, 
                             similar_events=similar_events)
    return "Ивент не найден", 404

# API для регистрации на ивент
@app.route('/api/register', methods=['POST'])
def register_for_event():
    try:
        data = request.json
        
        # Формируем текст письма
        email_subject = f"Новая регистрация на ивент: {data.get('event_title', 'Неизвестный ивент')}"
        
        email_body = f"""
Новая регистрация на офлайн встречу!

Информация об участнике:
- Имя: {data.get('name')}
- Email: {data.get('email')}
- Телефон: {data.get('phone')}
- О себе: {data.get('about', 'Не указано')}

Информация об ивенте:
- Название: {data.get('event_title')}
- Дата и время: {data.get('event_date')}
- Автор поста: {data.get('event_author')}

---
Это письмо отправлено автоматически с сайта consilium-events.ru
"""

        # Отправка email
        if SMTP_PASSWORD:  # Только если настроен пароль
            send_email(email_subject, email_body)
        else:
            # Если email не настроен, сохраняем в файл
            with open('registrations.log', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(email_body)
            print("Email не настроен. Регистрация сохранена в registrations.log")
        
        return jsonify({"success": True, "message": "Регистрация успешно отправлена"})
    
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Административные маршруты
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            flash('Вы успешно вошли в панель администратора', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    flash('Вы вышли из панели администратора', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    data = load_data()
    events = data.get('events', SAMPLE_EVENTS)
    
    # Преобразуем строки обратно в datetime объекты
    for event in events:
        if isinstance(event['event_date'], str):
            event['event_date'] = datetime.fromisoformat(event['event_date'])
    
    return render_template('admin/dashboard.html', 
                         events=events,
                         stats=data.get('stats', COMMUNITY_STATS),
                         testimonials=data.get('testimonials', TESTIMONIALS))

@app.route('/admin/events')
@login_required
def admin_events():
    data = load_data()
    events = data.get('events', SAMPLE_EVENTS)
    
    # Преобразуем строки обратно в datetime объекты
    for event in events:
        if isinstance(event['event_date'], str):
            event['event_date'] = datetime.fromisoformat(event['event_date'])
    
    return render_template('admin/events.html', events=events)

@app.route('/admin/events/new', methods=['GET', 'POST'])
@login_required
def admin_event_new():
    if request.method == 'POST':
        data = load_data()
        events = data.get('events', [])
        
        # Генерируем новый ID
        new_id = max([e['id'] for e in events], default=0) + 1
        
        # Преобразуем дату
        event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%dT%H:%M')
        
        # Создаем новый ивент
        new_event = {
            'id': new_id,
            'post_text': request.form['post_text'],
            'author': request.form['author'],
            'likes': int(request.form['likes']),
            'event_date': event_date,
            'status': 'upcoming',
            'participants': int(request.form['participants']),
            'category': request.form['category'],
            'tags': [tag.strip() for tag in request.form['tags'].split(',')],
            'location': request.form['location'],
            'online_link': request.form['online_link']
        }
        
        events.append(new_event)
        data['events'] = events
        save_data(data)
        
        flash('Ивент успешно создан!', 'success')
        return redirect(url_for('admin_events'))
    
    return render_template('admin/event_form.html', event=None)

@app.route('/admin/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_event_edit(event_id):
    data = load_data()
    events = data.get('events', [])
    
    # Преобразуем строки обратно в datetime объекты
    for event in events:
        if isinstance(event['event_date'], str):
            event['event_date'] = datetime.fromisoformat(event['event_date'])
    
    event = next((e for e in events if e['id'] == event_id), None)
    
    if not event:
        flash('Ивент не найден', 'error')
        return redirect(url_for('admin_events'))
    
    if request.method == 'POST':
        # Обновляем ивент
        event['post_text'] = request.form['post_text']
        event['author'] = request.form['author']
        event['likes'] = int(request.form['likes'])
        event['event_date'] = datetime.strptime(request.form['event_date'], '%Y-%m-%dT%H:%M')
        event['participants'] = int(request.form['participants'])
        event['category'] = request.form['category']
        event['tags'] = [tag.strip() for tag in request.form['tags'].split(',')]
        event['location'] = request.form['location']
        event['online_link'] = request.form['online_link']
        
        data['events'] = events
        save_data(data)
        
        flash('Ивент успешно обновлен!', 'success')
        return redirect(url_for('admin_events'))
    
    return render_template('admin/event_form.html', event=event)

@app.route('/admin/events/<int:event_id>/complete', methods=['POST'])
@login_required
def admin_event_complete(event_id):
    data = load_data()
    events = data.get('events', [])
    
    event = next((e for e in events if e['id'] == event_id), None)
    if event:
        event['status'] = 'past'
        data['events'] = events
        save_data(data)
        flash('Ивент отмечен как завершенный', 'success')
    
    return redirect(url_for('admin_events'))

@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
@login_required
def admin_event_delete(event_id):
    data = load_data()
    events = data.get('events', [])
    
    events = [e for e in events if e['id'] != event_id]
    data['events'] = events
    save_data(data)
    
    flash('Ивент успешно удален', 'success')
    return redirect(url_for('admin_events'))

@app.route('/admin/stats', methods=['GET', 'POST'])
@login_required
def admin_stats():
    data = load_data()
    
    if request.method == 'POST':
        stats = {
            'total_users': int(request.form['total_users']),
            'active_posts': int(request.form['active_posts']),
            'events_held': int(request.form['events_held']),
            'cities': int(request.form['cities'])
        }
        data['stats'] = stats
        save_data(data)
        flash('Статистика успешно обновлена!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/stats.html', stats=data.get('stats', COMMUNITY_STATS))

@app.route('/admin/testimonials')
@login_required
def admin_testimonials():
    data = load_data()
    return render_template('admin/testimonials.html', 
                         testimonials=data.get('testimonials', TESTIMONIALS))

@app.route('/admin/testimonials/new', methods=['GET', 'POST'])
@login_required
def admin_testimonial_new():
    if request.method == 'POST':
        data = load_data()
        testimonials = data.get('testimonials', [])
        
        # Генерируем новый ID
        new_id = max([t.get('id', 0) for t in testimonials], default=0) + 1
        
        new_testimonial = {
            'id': new_id,
            'author': request.form['author'],
            'text': request.form['text'],
            'rating': int(request.form['rating']),
            'event': request.form['event']
        }
        
        testimonials.append(new_testimonial)
        data['testimonials'] = testimonials
        save_data(data)
        
        flash('Отзыв успешно добавлен!', 'success')
        return redirect(url_for('admin_testimonials'))
    
    return render_template('admin/testimonial_form.html', testimonial=None)

@app.route('/admin/testimonials/<int:testimonial_id>/delete', methods=['POST'])
@login_required
def admin_testimonial_delete(testimonial_id):
    data = load_data()
    testimonials = data.get('testimonials', [])
    
    testimonials = [t for t in testimonials if t.get('id', 0) != testimonial_id]
    data['testimonials'] = testimonials
    save_data(data)
    
    flash('Отзыв успешно удален', 'success')
    return redirect(url_for('admin_testimonials'))

if __name__ == '__main__':
    # В продакшене используйте WSGI сервер, а не встроенный сервер Flask
    app.run(debug=False, host='0.0.0.0', port=5000)