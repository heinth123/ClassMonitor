import os
import requests
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hz_platform_super_secret_2026")

# ----------------- DATABASE CONFIGURATION -----------------
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///hz_platform.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ----------------- DATABASE MODELS -----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    display_name = db.Column(db.String(150), default="")
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, default="Building the future on the Hz Network!")
    is_admin = db.Column(db.Boolean, default=False)

class SurveyIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    # Create Admin account automatically if it doesn't exist
    admin_user = User.query.filter_by(username="heinth123").first()
    if not admin_user:
        hashed_pw = generate_password_hash("Ssu@$1588hhs0=@@!!hsjk", method='pbkdf2:sha256')
        admin = User(username="heinth123", display_name="Hein Thant (Admin)", password=hashed_pw, is_admin=True)
        db.session.add(admin)
        db.session.commit()

# ----------------- HTML TEMPLATES & LAYOUT -----------------
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hz Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-[#131314] text-[#e3e3e3] min-h-screen flex flex-col font-sans">
    
    <!-- TOP NAVIGATION BAR -->
    {% if current_user.is_authenticated %}
    <nav class="bg-[#1e1f20] border-b border-[#333537] px-6 py-3 flex items-center justify-between sticky top-0 z-50">
        <div class="flex items-center gap-6">
            <a href="/" class="text-xl font-extrabold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">Hz Platform ⚡</a>
            <div class="hidden md:flex items-center gap-2">
                <a href="/" class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-[#2d2e30] hover:text-white transition">Home</a>
                <a href="/terms" class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-[#2d2e30] hover:text-white transition">Terms of Service</a>
                <a href="/privacy" class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-[#2d2e30] hover:text-white transition">Privacy Policy</a>
                <a href="/friends" class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-[#2d2e30] hover:text-white transition">Friends</a>
                <a href="/find-friends" class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-[#2d2e30] hover:text-white transition">Find Friends</a>
                <a href="/profile" class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-[#2d2e30] hover:text-white transition">Profile</a>
            </div>
        </div>
        <div class="flex items-center gap-3">
            <span class="text-xs bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full border border-blue-500/20 font-semibold">
                {{ current_user.display_name if current_user.display_name else current_user.username }}
            </span>
            <a href="/logout" class="text-gray-400 hover:text-red-400 p-2 transition" title="Log Out"><i class="fa-solid fa-arrow-right-from-bracket"></i></a>
        </div>
    </nav>
    {% endif %}

    <!-- MAIN CONTENT BLOCK -->
    <div class="flex-1 flex flex-col">
        {% block content %}{% endblock %}
    </div>

</body>
</html>
"""

AUTH_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    <div class="m-auto bg-[#1e1f20] p-8 rounded-2xl shadow-2xl w-full max-w-md border border-[#333537] my-auto">
        <div class="text-center mb-6">
            <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">Hz Platform</h1>
            <p class="text-sm text-gray-400 mt-1">Welcome! Log in or sign up to enter.</p>
        </div>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="bg-blue-500/20 border border-blue-500 text-blue-300 p-3 rounded-lg mb-4 text-sm text-center">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}

        <!-- Google Login Button Simulation / Integration -->
        <a href="/google-login" class="w-full bg-white hover:bg-gray-100 text-gray-900 font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-3 transition mb-4 shadow-sm">
            <i class="fa-brands fa-google text-red-500"></i> Continue with Google
        </a>

        <div class="flex items-center my-4">
            <div class="flex-1 border-t border-[#333537]"></div>
            <span class="px-3 text-xs text-gray-500 uppercase">or username</span>
            <div class="flex-1 border-t border-[#333537]"></div>
        </div>

        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-xs uppercase font-bold text-gray-400 mb-1">Username</label>
                <input type="text" name="username" required class="w-full bg-[#131314] border border-[#444] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500 text-sm">
            </div>
            <div>
                <label class="block text-xs uppercase font-bold text-gray-400 mb-1">Password</label>
                <input type="password" name="password" required class="w-full bg-[#131314] border border-[#444] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500 text-sm">
            </div>
            <div class="flex gap-2 pt-2">
                <button type="submit" name="action" value="login" class="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 rounded-lg transition text-sm">Log In</button>
                <button type="submit" name="action" value="register" class="flex-1 bg-[#2d2e30] hover:bg-[#3c3d40] text-white font-semibold py-2.5 rounded-lg transition text-sm border border-[#444]">Sign Up</button>
            </div>
        </form>
    </div>
""")

HOME_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    <div class="flex flex-1">
        <!-- ADMIN SIDEBAR (Visible only to admin heinth123) -->
        {% if current_user.is_admin %}
        <div class="w-72 bg-[#191a1b] border-r border-[#333537] p-6 hidden lg:block overflow-y-auto">
            <div class="flex items-center gap-2 mb-6">
                <span class="w-3 h-3 rounded-full bg-red-500 animate-pulse"></span>
                <h3 class="font-bold text-white text-sm uppercase tracking-wider">Admin Control Panel</h3>
            </div>
            <div class="text-xs font-semibold text-gray-400 uppercase mb-3">Survey Responses (App Ideas)</div>
            <div class="space-y-3">
                {% if surveys %}
                    {% for s in surveys %}
                        <div class="bg-[#131314] border border-[#333537] p-3 rounded-xl text-xs space-y-1">
                            <div class="font-bold text-blue-400">👤 {{ s.user_name }}</div>
                            <p class="text-gray-300 leading-relaxed">{{ s.description }}</p>
                        </div>
                    {% endfor %}
                {% else %}
                    <p class="text-xs text-gray-500 italic">No app ideas submitted yet.</p>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <!-- MAIN DASHBOARD CONTENT -->
        <div class="flex-1 p-8 max-w-5xl mx-auto space-y-12">
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="bg-blue-500/20 border border-blue-500 text-blue-300 p-3 rounded-xl text-sm text-center">{{ messages[0] }}</div>
                {% endif %}
            {% endwith %}

            <!-- FROM HZ SECTION -->
            <section class="space-y-4">
                <div class="flex items-center justify-between">
                    <h2 class="text-2xl font-extrabold text-white flex items-center gap-2">🔥 From Hz Network</h2>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Minecraft Community App Card -->
                    <a href="https://minecraft-portal.onrender.com/" target="_blank" class="bg-[#1e1f20] hover:bg-[#252628] border border-[#333537] p-6 rounded-2xl transition group flex flex-col justify-between shadow-lg">
                        <div>
                            <div class="text-3xl mb-3">⛏️</div>
                            <h3 class="text-lg font-bold text-white group-hover:text-blue-400 transition">Minecraft Myanmar Community</h3>
                            <p class="text-sm text-gray-400 mt-2">Explore servers, custom builds, and chat with other players in the Myanmar gaming community.</p>
                        </div>
                        <div class="mt-6 flex items-center text-xs font-bold text-blue-400 gap-1">
                            Launch App <i class="fa-solid fa-arrow-up-right-from-square"></i>
                        </div>
                    </a>

                    <!-- HeinGPT App Card -->
                    <a href="https://heingpt-bot-web.onrender.com/" target="_blank" class="bg-[#1e1f20] hover:bg-[#252628] border border-[#333537] p-6 rounded-2xl transition group flex flex-col justify-between shadow-lg">
                        <div>
                            <div class="text-3xl mb-3">⚡</div>
                            <h3 class="text-lg font-bold text-white group-hover:text-blue-400 transition">HeinGPT</h3>
                            <p class="text-sm text-gray-400 mt-2">Your lightning-fast personal AI workspace powered by Groq and custom memory systems.</p>
                        </div>
                        <div class="mt-6 flex items-center text-xs font-bold text-purple-400 gap-1">
                            Launch App <i class="fa-solid fa-arrow-up-right-from-square"></i>
                        </div>
                    </a>
                </div>
            </section>

            <!-- ABOUT US SECTION -->
            <section class="bg-[#1e1f20] border border-[#333537] p-8 rounded-2xl shadow-xl space-y-4">
                <h3 class="text-xl font-bold text-white">About Us</h3>
                <p class="text-sm text-gray-300 leading-relaxed">
                    Welcome to the <strong>Hz Network</strong>—a central digital ecosystem built by developers and creators for gamers, coders, and explorers. Our mission is to connect high-performance web applications, interactive gaming communities, and cutting-edge AI tools under one seamless platform. Whether you are building redstone contraptions in Minecraft, coding live applications, or testing new ideas, the Hz Network is your home base for innovation and community.
                </p>
            </section>

            <!-- SURVEY SECTION -->
            <section class="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 p-8 rounded-2xl shadow-xl space-y-4">
                <h3 class="text-xl font-bold text-white">💡 Pitch Your Next App Idea</h3>
                <p class="text-sm text-gray-300">Have an idea for the next big application on the Hz Network? Let us know what you want us to build!</p>
                <form action="/submit-survey" method="POST" class="space-y-4 pt-2">
                    <div>
                        <label class="block text-xs uppercase font-bold text-gray-400 mb-1">Your Name</label>
                        <input type="text" name="user_name" required value="{{ current_user.display_name if current_user.display_name else current_user.username }}" class="w-full bg-[#131314] border border-[#333537] rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500">
                    </div>
                    <div>
                        <label class="block text-xs uppercase font-bold text-gray-400 mb-1">Description / How it Works</label>
                        <textarea name="description" rows="3" required placeholder="Explain what the app does and how users interact with it..." class="w-full bg-[#131314] border border-[#333537] rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"></textarea>
                    </div>
                    <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-2.5 rounded-lg text-sm transition">Submit Idea</button>
                </form>
            </section>

        </div>
    </div>
""")

TERMS_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    <div class="max-w-4xl mx-auto p-8 space-y-6">
        <h1 class="text-3xl font-extrabold text-white">Terms of Service</h1>
        <p class="text-xs text-gray-500">Last updated: 2026</p>
        <div class="bg-[#1e1f20] border border-[#333537] p-8 rounded-2xl space-y-4 text-sm text-gray-300 leading-relaxed">
            <h2 class="text-lg font-bold text-white">1. Acceptance of Terms</h2>
            <p>By accessing and using the Hz Platform, you agree to comply with and be bound by these Terms of Service. If you do not agree, please do not use our platform or connected apps.</p>
            
            <h2 class="text-lg font-bold text-white">2. User Conduct</h2>
            <p>Users agree to maintain a respectful and positive environment. Harassment, spamming survey forms, attempting unauthorized access to admin accounts, or distributing harmful scripts is strictly prohibited.</p>

            <h2 class="text-lg font-bold text-white">3. Intellectual Property</h2>
            <p>All platform design, branding, and connected community applications (including HeinGPT and Minecraft Myanmar Portal) belong to the Hz Network creators.</p>
        </div>
    </div>
""")

PRIVACY_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    <div class="max-w-4xl mx-auto p-8 space-y-6">
        <h1 class="text-3xl font-extrabold text-white">Privacy Policy</h1>
        <p class="text-xs text-gray-500">Last updated: 2026</p>
        <div class="bg-[#1e1f20] border border-[#333537] p-8 rounded-2xl space-y-4 text-sm text-gray-300 leading-relaxed">
            <h2 class="text-lg font-bold text-white">1. Information We Collect</h2>
            <p>When you register or sign in via Google/credentials, we store your username, display name, and survey submissions to provide your personalized experience.</p>
            
            <h2 class="text-lg font-bold text-white">2. Data Security</h2>
            <p>We use encrypted password hashing and secure session management to protect your account data. Your information is never sold or shared with third parties.</p>

            <h2 class="text-lg font-bold text-white">3. Contact Us</h2>
            <p>If you have questions regarding your privacy or data on the Hz Platform, reach out through our community channels.</p>
        </div>
    </div>
""")

FRIENDS_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    <div class="max-w-4xl mx-auto p-8 space-y-6">
        <h1 class="text-3xl font-extrabold text-white">My Friends</h1>
        <div class="bg-[#1e1f20] border border-[#333537] p-6 rounded-2xl space-y-4">
            {% if friends %}
                <div class="space-y-3">
                    {% for f in friends %}
                        <div class="flex items-center justify-between p-3 bg-[#131314] rounded-xl border border-[#333537]">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center font-bold text-white uppercase">{{ f.username[0] }}</div>
                                <div>
                                    <div class="font-bold text-white text-sm">{{ f.display_name if f.display_name else f.username }}</div>
                                    <div class="text-xs text-gray-400">Hz Network Member</div>
                                </div>
                            </div>
                            <a href="/profile/{{ f.id }}" class="bg-[#2d2e30] hover:bg-[#3c3d40] px-4 py-2 rounded-lg text-xs font-semibold text-white transition">View Profile</a>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <p class="text-sm text-gray-400 italic">You haven't added any friends yet. Visit <a href="/find-friends" class="text-blue-400 hover:underline">Find Friends</a> to connect!</p>
            {% endif %}
        </div>
    </div>
""")

FIND_FRIENDS_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    <div class="max-w-4xl mx-auto p-8 space-y-6">
        <h1 class="text-3xl font-extrabold text-white">Find Friends</h1>
        <div class="bg-[#1e1f20] border border-[#333537] p-6 rounded-2xl space-y-4">
            <div class="space-y-3">
                {% for u in users %}
                    {% if u.id != current_user.id %}
                        <div class="flex items-center justify-between p-3 bg-[#131314] rounded-xl border border-[#333537]">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center font-bold text-white uppercase">{{ u.username[0] }}</div>
                                <div>
                                    <div class="font-bold text-white text-sm">{{ u.display_name if u.display_name else u.username }}</div>
                                    <div class="text-xs text-gray-400">{{ u.bio }}</div>
                                </div>
                            </div>
                            <div class="flex gap-2">
                                <a href="/profile/{{ u.id }}" class="bg-[#2d2e30] hover:bg-[#3c3d40] px-3 py-2 rounded-lg text-xs font-semibold text-white transition">Profile</a>
                                <form action="/add-friend/{{ u.id }}" method="POST">
                                    <button type="submit" class="bg-blue-600 hover:bg-blue-500 px-3 py-2 rounded-lg text-xs font-semibold text-white transition">Add Friend</button>
                                </form>
                            </div>
                        </div>
                    {% endif %}
                {% endfor %}
            </div>
        </div>
    </div>
""")

PROFILE_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    <div class="max-w-2xl mx-auto p-8 space-y-6">
        <h1 class="text-3xl font-extrabold text-white">User Profile</h1>
        <div class="bg-[#1e1f20] border border-[#333537] p-8 rounded-2xl space-y-6 shadow-xl">
            <div class="flex items-center gap-4">
                <div class="w-16 h-16 rounded-full bg-gradient-to-tr from-blue-500 to-purple-600 flex items-center justify-center text-2xl font-bold text-white uppercase">
                    {{ profile_user.username[0] }}
                </div>
                <div>
                    <h2 class="text-xl font-bold text-white">{{ profile_user.display_name if profile_user.display_name else profile_user.username }}</h2>
                    <p class="text-xs text-blue-400">@{{ profile_user.username }}</p>
                </div>
            </div>
            <div>
                <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Bio / Status</label>
                <p class="text-sm text-gray-300 bg-[#131314] p-3 rounded-lg border border-[#333537]">{{ profile_user.bio }}</p>
            </div>
            {% if profile_user.id == current_user.id %}
            <form action="/update-profile" method="POST" class="space-y-4 pt-4 border-t border-[#333537]">
                <div class="text-xs font-bold text-blue-400 uppercase">Edit Profile</div>
                <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1">Display Name</label>
                    <input type="text" name="display_name" value="{{ profile_user.display_name }}" class="w-full bg-[#131314] border border-[#333537] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500">
                </div>
                <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1">Bio</label>
                    <textarea name="bio" rows="2" class="w-full bg-[#131314] border border-[#333537] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500">{{ profile_user.bio }}</textarea>
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 rounded-lg text-sm transition">Save Profile</button>
            </form>
            {% endif %}
        </div>
    </div>
""")

# ----------------- ROUTES -----------------
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template_string(AUTH_TEMPLATE)
    surveys = SurveyIdea.query.all() if current_user.is_admin else []
    return render_template_string(HOME_TEMPLATE, surveys=surveys)

@app.route('/', methods=['POST'])
def handle_auth():
    username = request.form.get('username')
    password = request.form.get('password')
    action = request.form.get('action')

    user = User.query.filter_by(username=username).first()

    if action == 'login':
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password!')
    elif action == 'register':
        if user:
            flash('Username already exists!')
        else:
            hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, display_name=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))
    return render_template_string(AUTH_TEMPLATE)

@app.route('/google-login')
def google_login():
    # Simulated quick Google OAuth login for the platform
    google_user = User.query.filter_by(username="google_user").first()
    if not google_user:
        hashed_pw = generate_password_hash("google123", method='pbkdf2:sha256')
        google_user = User(username="google_user", display_name="Google User", password=hashed_pw)
        db.session.add(google_user)
        db.session.commit()
    login_user(google_user)
    flash('Successfully signed in with Google!')
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/terms')
@login_required
def terms():
    return render_template_string(TERMS_TEMPLATE)

@app.route('/privacy')
@login_required
def privacy():
    return render_template_string(PRIVACY_TEMPLATE)

@app.route('/friends')
@login_required
def friends():
    friendships = Friendship.query.filter_by(user_id=current_user.id).all()
    friend_ids = [f.friend_id for f in friendships]
    friends_list = User.query.filter(User.id.in_(friend_ids)).all() if friend_ids else []
    return render_template_string(FRIENDS_TEMPLATE, friends=friends_list)

@app.route('/find-friends')
@login_required
def find_friends():
    users = User.query.all()
    return render_template_string(FIND_FRIENDS_TEMPLATE, users=users)

@app.route('/add-friend/<int:friend_id>', methods=['POST'])
@login_required
def add_friend(friend_id):
    if friend_id != current_user.id:
        existing = Friendship.query.filter_by(user_id=current_user.id, friend_id=friend_id).first()
        if not existing:
            db.session.add(Friendship(user_id=current_user.id, friend_id=friend_id))
            db.session.commit()
            flash('Friend added successfully!')
    return redirect(url_for('friends'))

@app.route('/profile')
@login_required
def profile():
    return render_template_string(PROFILE_TEMPLATE, profile_user=current_user)

@app.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    target_user = User.query.get_or_404(user_id)
    return render_template_string(PROFILE_TEMPLATE, profile_user=target_user)

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    current_user.display_name = request.form.get('display_name', current_user.display_name)
    current_user.bio = request.form.get('bio', current_user.bio)
    db.session.commit()
    flash('Profile updated successfully!')
    return redirect(url_for('profile'))

@app.route('/submit-survey', methods=['POST'])
@login_required
def submit_survey():
    user_name = request.form.get('user_name')
    description = request.form.get('description')
    if user_name and description:
        db.session.add(SurveyIdea(user_name=user_name, description=description))
        db.session.commit()
        flash('Thank you! Your app idea survey has been submitted.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
