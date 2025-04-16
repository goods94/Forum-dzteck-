from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import time
import random
import logging
import binascii
from models import db, User, Thread, Reaction

logging.basicConfig(level=logging.DEBUG)

# Configuration
AVATAR_UPLOAD_DIR = 'uploads/avatars/'
DEFAULT_AVATAR = 'assets/images/default-avatar.png'
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_AVATAR_TYPES = ['image/jpeg', 'image/png', 'image/gif']

# Initialize Flask app
app = Flask(__name__, static_folder='.')
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.permanent_session_lifetime = 3600 * 24 * 7  # 1 week

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///forum.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Create avatar directory if it doesn't exist
os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

# Helper functions
def get_user_level(points):
    levels = [
        {'min_points': 0, 'name': 'عضو جديد', 'color': 'secondary', 'next_level_name': 'عضو مشارك', 'next_level_points': 10},
        {'min_points': 10, 'name': 'عضو مشارك', 'color': 'info', 'next_level_name': 'عضو نشيط', 'next_level_points': 50},
        {'min_points': 50, 'name': 'عضو نشيط', 'color': 'warning', 'next_level_name': 'محترف متقدم', 'next_level_points': 100},
        {'min_points': 100, 'name': 'محترف متقدم', 'color': 'danger', 'next_level_name': 'عضو محترف', 'next_level_points': 500},
        {'min_points': 500, 'name': 'عضو محترف', 'color': 'danger', 'next_level_name': 'قمة المنتدى', 'next_level_points': 1000}
    ]
    
    current_level = levels[0]
    for level in levels:
        if points >= level['min_points']:
            current_level = level
        else:
            break
    
    # If at max level
    if current_level == levels[-1]:
        current_level['next_level_name'] = 'أعلى مستوى'
        current_level['next_level_points'] = current_level['min_points']
        
    return current_level

def time_ago(timestamp):
    time_ago = time.time() - timestamp
    if time_ago < 60:
        return 'الآن'
    
    condition = {
        12 * 30 * 24 * 60 * 60: 'سنة',
        30 * 24 * 60 * 60: 'شهر',
        24 * 60 * 60: 'يوم',
        60 * 60: 'ساعة',
        60: 'دقيقة',
        1: 'ثانية'
    }
    
    for secs, str_time in condition.items():
        d = time_ago / secs
        if d >= 1:
            r = round(d)
            if r == 1:
                return f'منذ {str_time}'
            if r == 2:
                if str_time == 'سنة':
                    return 'منذ سنتين'
                elif str_time == 'شهر':
                    return 'منذ شهرين'
                elif str_time == 'يوم':
                    return 'منذ يومين'
                else:
                    return f'منذ {str_time}ين'
            if r >= 3 and r <= 10:
                if str_time == 'سنة':
                    return f'منذ {r} سنوات'
                elif str_time == 'شهر':
                    return f'منذ {r} أشهر'
                elif str_time == 'يوم':
                    return f'منذ {r} أيام'
                elif str_time == 'ساعة':
                    return f'منذ {r} ساعات'
                elif str_time == 'دقيقة':
                    return f'منذ {r} دقائق'
                else:
                    return f'منذ {r} {str_time}'
            return f'منذ {r} {str_time}'
    
    return 'الآن'

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = binascii.hexlify(os.urandom(32)).decode()
    return session['csrf_token']

# Initialize default data if not in session
def initialize_session_data():
    if 'threads' not in session:
        session['threads'] = [
            {'id': 1, 'title': 'أول موضوع في المنتدى', 'content': 'هذا هو أول موضوع تجريبي! مرحباً بالجميع في منتدى DzTeck. شاركونا آراءكم.', 'author': 'Admin', 'timestamp': time.time() - 86400},  # 1 day ago
            {'id': 2, 'title': 'اقتراحات لتطوير المنتدى', 'content': 'هل لديك اقتراح لجعل المنتدى أفضل؟ شاركه معنا هنا. نحن نستمع!', 'author': 'Moderator', 'timestamp': time.time() - 7200},  # 2 hours ago
            {'id': 3, 'title': 'نقاش حول أحدث التقنيات', 'content': 'ما رأيكم في آخر التطورات في عالم الذكاء الاصطناعي والحوسبة السحابية؟', 'author': 'TechGuru', 'timestamp': time.time() - 900},  # 15 minutes ago
        ]
    
    if 'reactions' not in session:
        session['reactions'] = {}
    
    if 'user_reactions' not in session:
        session['user_reactions'] = {}

# Route for static files (CSS, JS, images)
@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('assets', path)

# Route for avatar uploads
@app.route('/uploads/avatars/<path:path>')
def serve_avatars(path):
    return send_from_directory('uploads/avatars', path)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        csrf_token = request.form.get('csrf_token', '')
        
        if not username:
            login_error = "الرجاء إدخال اسم المستخدم."
        elif csrf_token != session.get('csrf_token'):
            login_error = "خطأ في التحقق من CSRF!"
        else:
            session['username'] = username
            session['points'] = session.get('points', 0)
            session['avatar'] = session.get('avatar')
            initialize_session_data()
            session.modified = True
            return redirect(url_for('index'))
    
    return render_template('login.html', login_error=login_error, csrf_token=generate_csrf_token())

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Avatar upload handler
@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'avatar' not in request.files:
        flash('لم يتم اختيار أي ملف.', 'danger')
        return redirect(url_for('index'))
    
    csrf_token = request.form.get('csrf_token', '')
    if csrf_token != session.get('csrf_token'):
        flash('خطأ في التحقق من CSRF!', 'danger')
        return redirect(url_for('index'))
    
    avatar_file = request.files['avatar']
    
    # Check if file is empty
    if avatar_file.filename == '':
        flash('لم يتم اختيار أي ملف.', 'danger')
        return redirect(url_for('index'))
    
    # Check file type
    if avatar_file.content_type not in ALLOWED_AVATAR_TYPES:
        flash('نوع الملف غير مسموح به. الأنواع المسموح بها: JPG, PNG, GIF.', 'danger')
        return redirect(url_for('index'))
    
    # Check file size
    if request.content_length > MAX_AVATAR_SIZE:
        flash(f'حجم الملف كبير جداً. الحد الأقصى: {MAX_AVATAR_SIZE / 1024 / 1024} MB.', 'danger')
        return redirect(url_for('index'))
    
    # Delete old avatar if exists
    old_avatar = session.get('avatar')
    if old_avatar and os.path.exists(os.path.join(AVATAR_UPLOAD_DIR, old_avatar)):
        try:
            os.unlink(os.path.join(AVATAR_UPLOAD_DIR, old_avatar))
        except:
            pass
    
    # Save new avatar
    filename = secure_filename(avatar_file.filename)
    safe_username = ''.join(c if c.isalnum() else '_' for c in session['username'])
    new_filename = f"{safe_username}_{int(time.time())}.{filename.rsplit('.', 1)[1].lower()}"
    avatar_file.save(os.path.join(AVATAR_UPLOAD_DIR, new_filename))
    
    # Update session
    session['avatar'] = new_filename
    session['points'] = session.get('points', 0) + 2
    session.modified = True
    
    flash('تم تحديث الصورة الرمزية بنجاح!', 'success')
    return redirect(url_for('index'))

# Handle thread reactions
@app.route('/react', methods=['POST'])
def react():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    csrf_token = request.form.get('csrf_token', '')
    if csrf_token != session.get('csrf_token'):
        flash('خطأ في التحقق من CSRF!', 'danger')
        return redirect(url_for('index'))
    
    thread_id = int(request.form.get('thread_id', 0))
    emoji = request.form.get('emoji', '')
    username = session['username']
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    valid_emojis = ['like', 'love', 'laugh', 'sad', 'angry']
    
    if emoji in valid_emojis:
        # Get the reactions dict
        reactions = session.get('reactions', {})
        user_reactions = session.get('user_reactions', {})
        
        # Convert for easier manipulation
        reactions = dict(reactions)
        user_reactions = dict(user_reactions)
        
        # Initialize if needed
        if str(thread_id) not in reactions:
            reactions[str(thread_id)] = {emoji: 0 for emoji in valid_emojis}
        
        if str(thread_id) not in user_reactions:
            user_reactions[str(thread_id)] = {}
        
        current_user_reaction = user_reactions[str(thread_id)].get(username)
        points_awarded = 0
        
        if current_user_reaction == emoji:
            # Remove reaction
            reactions[str(thread_id)][emoji] = max(0, reactions[str(thread_id)][emoji] - 1)
            user_reactions[str(thread_id)].pop(username, None)
            user_has_reacted = False
            current_reaction = None
        else:
            # Add or change reaction
            if current_user_reaction:
                # Decrement old reaction
                reactions[str(thread_id)][current_user_reaction] = max(0, reactions[str(thread_id)][current_user_reaction] - 1)
            else:
                # New reaction
                points_awarded = 1
            
            # Increment new reaction
            reactions[str(thread_id)][emoji] = reactions[str(thread_id)].get(emoji, 0) + 1
            user_reactions[str(thread_id)][username] = emoji
            user_has_reacted = True
            current_reaction = emoji
        
        # Update session
        session['reactions'] = reactions
        session['user_reactions'] = user_reactions
        session['points'] = session.get('points', 0) + points_awarded
        session.modified = True
        
        # If it's an AJAX request, return JSON response
        if is_ajax:
            return jsonify({
                'success': True,
                'thread_id': thread_id,
                'emoji': emoji,
                'reaction_counts': reactions[str(thread_id)],
                'user_reacted': user_has_reacted,
                'current_reaction': current_reaction
            })
        
        # For non-AJAX requests, redirect as before
        return redirect(url_for('index', _anchor=f'thread-{thread_id}'))
    
    # Error response for invalid emoji
    if is_ajax:
        return jsonify({'success': False, 'error': 'Invalid emoji'}), 400
        
    return redirect(url_for('index'))

# New thread route
@app.route('/new_thread', methods=['POST'])
def new_thread():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    csrf_token = request.form.get('csrf_token', '')
    if csrf_token != session.get('csrf_token'):
        flash('خطأ في التحقق من CSRF!', 'danger')
        return redirect(url_for('index'))
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    
    if not title or not content:
        flash('يرجى ملء جميع الحقول المطلوبة.', 'danger')
        return redirect(url_for('index'))
    
    # Get current threads
    threads = session.get('threads', [])
    threads = list(threads)  # Make a copy for manipulation
    
    # Generate next ID
    next_id = 1
    if threads:
        next_id = max(thread['id'] for thread in threads) + 1
    
    # Create new thread
    new_thread = {
        'id': next_id,
        'title': title,
        'content': content,
        'author': session['username'],
        'timestamp': time.time()
    }
    
    # Add to beginning of list
    threads.insert(0, new_thread)
    
    # Update session
    session['threads'] = threads
    session['points'] = session.get('points', 0) + 5
    session.modified = True
    
    flash('تم إنشاء الموضوع بنجاح!', 'success')
    return redirect(url_for('index', _anchor=f'thread-{next_id}'))

# Main route
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    initialize_session_data()
    
    view_mode = request.args.get('view', 'list')
    thread_id = request.args.get('id')
    thread_to_view = None
    
    if view_mode == 'thread' and thread_id:
        thread_id = int(thread_id)
        for thread in session['threads']:
            if thread['id'] == thread_id:
                thread_to_view = thread
                break
        
        if not thread_to_view:
            view_mode = 'list'
    
    user_level = get_user_level(session.get('points', 0))
    
    return render_template('index.html', 
                          username=session['username'],
                          avatar=session.get('avatar'),
                          points=session.get('points', 0),
                          user_level=user_level,
                          threads=session['threads'],
                          reactions=session.get('reactions', {}),
                          user_reactions=session.get('user_reactions', {}),
                          view_mode=view_mode,
                          thread_to_view=thread_to_view,
                          csrf_token=generate_csrf_token(),
                          DEFAULT_AVATAR=DEFAULT_AVATAR,
                          time_ago=time_ago)

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    initialize_session_data()
    
    user_level = get_user_level(session.get('points', 0))
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         avatar=session.get('avatar'),
                         points=session.get('points', 0),
                         user_level=user_level,
                         threads=session['threads'],
                         reactions=session.get('reactions', {}),
                         user_reactions=session.get('user_reactions', {}),
                         csrf_token=generate_csrf_token(),
                         DEFAULT_AVATAR=DEFAULT_AVATAR,
                         time_ago=time_ago)

# For direct access of PHP files
@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)