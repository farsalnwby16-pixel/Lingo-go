import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

# تحديد مسار القوالب بدقة ليعمل مع Vercel
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'lingo_go_permanent_secret_key'

# الربط الثابت والدائم بقاعدة بيانات Neon PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_ZECSXyova0b9@ep-fragrant-firefly-zaojv26y-pooler.c-2.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(10), nullable=False)

class CompletedLesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, index=True)
    student_name = db.Column(db.String(150), nullable=False)
    lesson_id = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()
    # حقن الدروس تلقائياً في القاعدة الدائمة إن كانت فارغة لضمان ظهور المحتوى بكل الأقسام والمستويات
    if Lesson.query.count() == 0:
        categories = ['Lessons', 'Listening', 'Accent', 'Shadowing', 'Stories']
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        sample_lessons = []
        for cat in categories:
            for lvl in levels:
                sample_lessons.append(Lesson(title=f"درس {cat} - مستوى {lvl} (1)", url="https://www.youtube.com/embed/dQw4w9WgXcQ", category=cat, level=lvl))
                sample_lessons.append(Lesson(title=f"درس {cat} - مستوى {lvl} (2)", url="https://www.youtube.com/embed/dQw4w9WgXcQ", category=cat, level=lvl))
        db.session.bulk_save_objects(sample_lessons)
        db.session.commit()

@app.route('/')
def index():
    cat = request.args.get('cat', 'Lessons')
    level = request.args.get('level', 'A1')
    
    user_id = request.cookies.get('lingo_user_id')
    if not user_id:
        user_id = str(uuid.uuid4())

    student_name = session.get('student_name', 'طالب لغة')

    lessons_query = Lesson.query.filter_by(category=cat, level=level).all()
    lessons = [{'id': l.id, 'title': l.title, 'url': l.url} for l in lessons_query]

    completed_records = CompletedLesson.query.filter_by(user_id=user_id).all()
    completed_ids = [r.lesson_id for r in completed_records]

    total = len(lessons)
    completed_count = sum(1 for l in lessons if l['id'] in completed_ids)
    progress_pct = int((completed_count / total) * 100) if total > 0 else 0

    resp = make_response(render_template('index.html', 
                               lessons=lessons, 
                               current_cat=cat, 
                               current_level=level, 
                               student_name=student_name,
                               completed_ids=completed_ids,
                               progress_pct=progress_pct))
    
    resp.set_cookie('lingo_user_id', user_id, max_age=60*60*24*365*10)
    return resp

@app.route('/mark_done/<int:lesson_id>', methods=['POST', 'GET'])
def mark_done(lesson_id):
    user_id = request.cookies.get('lingo_user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        
    student_name = session.get('student_name', 'طالب لغة')
    
    existing = CompletedLesson.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if not existing:
        new_comp = CompletedLesson(user_id=user_id, student_name=student_name, lesson_id=lesson_id)
        db.session.add(new_comp)
        db.session.commit()
        
    resp = jsonify({'status': 'success'})
    resp.set_cookie('lingo_user_id', user_id, max_age=60*60*24*365*10)
    return resp

@app.route('/update_student_name', methods=['POST'])
def update_student_name():
    session['student_name'] = request.form.get('full_name', 'طالب لغة')
    return redirect(request.referrer or url_for('index'))

@app.route('/certificate')
def certificate():
    student_name = session.get('student_name', 'طالب لغة')
    return render_template('certificate.html', student_name=student_name)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
