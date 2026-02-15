from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import re
from datetime import datetime, timedelta
import PyPDF2
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

# ========== APP CONFIGURATION ========== #

app = Flask(__name__)
# Add custom Jinja filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value) if value else []
    except:
        return []
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

os.makedirs('uploads', exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ========== DATABASE MODELS ========== #

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    original_name = db.Column(db.String(200))
    extracted_text = db.Column(db.Text)
    skills = db.Column(db.Text)
    experience_years = db.Column(db.Integer, default=0)
    education = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    score = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    matches = db.relationship('Match', backref='resume', lazy=True, cascade='all, delete-orphan')

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_required = db.Column(db.Text)
    experience_required = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    job_type = db.Column(db.String(50), default='Full-time')
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    matches = db.relationship('Match', backref='job', lazy=True, cascade='all, delete-orphan')

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    match_score = db.Column(db.Float, default=0.0)
    matching_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ========== HELPER CLASSES ========== #

class ResumeParser:
    """Advanced Resume Parser with NLP"""
    
    SKILLS_DATABASE = [
        # Programming Languages
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 
        'kotlin', 'go', 'rust', 'typescript', 'scala', 'r', 'matlab',
        
        # Web Technologies
        'html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 
        'django', 'flask', 'fastapi', 'spring', 'asp.net', 'jquery',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 
        'sqlite', 'dynamodb', 'cassandra', 'elasticsearch',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 
        'terraform', 'ansible', 'ci/cd', 'linux', 'unix',
        
        # Data Science & AI
        'machine learning', 'deep learning', 'nlp', 'tensorflow', 
        'pytorch', 'scikit-learn', 'pandas', 'numpy', 'keras',
        
        # Tools & Others
        'git', 'github', 'gitlab', 'jira', 'agile', 'scrum', 
        'rest api', 'graphql', 'microservices', 'testing'
    ]
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            print(f"PDF Error: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX"""
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"DOCX Error: {e}")
            return ""
    
    @classmethod
    def extract_skills(cls, text):
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in cls.SKILLS_DATABASE:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))
    
    @staticmethod
    def extract_email(text):
        """Extract email from text"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        emails = re.findall(pattern, text)
        return emails[0] if emails else None
    
    @staticmethod
    def extract_phone(text):
        """Extract phone number"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        for pattern in patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    @staticmethod
    def extract_experience(text):
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)',
            r'(?:experience|exp).*?(\d+)\+?\s*(?:years?|yrs?)'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([int(m) for m in matches])
        
        return max(years) if years else 0
    
    @staticmethod
    def extract_education(text):
        """Extract education level"""
        education_keywords = {
            'phd': 'PhD',
            'doctorate': 'PhD',
            'master': "Master's",
            'm.tech': "Master's",
            'mba': 'MBA',
            'bachelor': "Bachelor's",
            'b.tech': "Bachelor's",
            'b.e': "Bachelor's",
            'b.sc': "Bachelor's"
        }
        
        text_lower = text.lower()
        for keyword, level in education_keywords.items():
            if keyword in text_lower:
                return level
        
        return 'Not specified'
    
    @staticmethod
    def calculate_score(skills, experience, education, text):
        """Calculate overall resume score"""
        score = 0
        
        # Skills (40 points)
        score += min(len(skills) * 4, 40)
        
        # Experience (30 points)
        if experience >= 5:
            score += 30
        elif experience >= 3:
            score += 20
        elif experience >= 1:
            score += 10
        
        # Education (20 points)
        edu_scores = {'PhD': 20, 'MBA': 18, "Master's": 15, "Bachelor's": 12}
        score += edu_scores.get(education, 5)
        
        # Resume length (10 points)
        word_count = len(text.split())
        if 300 <= word_count <= 1000:
            score += 10
        elif word_count > 200:
            score += 5
        
        return min(score, 100)
    
    @classmethod
    def parse(cls, file_path):
        """Main parsing function"""
        if file_path.endswith('.pdf'):
            text = cls.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = cls.extract_text_from_docx(file_path)
        else:
            return None
        
        if not text:
            return None
        
        skills = cls.extract_skills(text)
        experience = cls.extract_experience(text)
        education = cls.extract_education(text)
        score = cls.calculate_score(skills, experience, education, text)
        
        return {
            'text': text,
            'skills': skills,
            'experience_years': experience,
            'education': education,
            'email': cls.extract_email(text),
            'phone': cls.extract_phone(text),
            'score': score
        }

class JobMatcher:
    """Advanced Job Matching Algorithm"""
    
    @staticmethod
    def calculate_skill_match(resume_skills, job_skills):
        """Calculate skill matching percentage"""
        if not job_skills:
            return 100, [], []
        
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills.split(','))
        
        matching = list(resume_set & job_set)
        missing = list(job_set - resume_set)
        
        match_percentage = (len(matching) / len(job_set)) * 100 if job_set else 0
        
        return match_percentage, matching, missing
    
    @staticmethod
    def calculate_text_similarity(resume_text, job_description):
        """Calculate text similarity using TF-IDF"""
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity * 100
        except:
            return 0
    
    @staticmethod
    def calculate_experience_match(resume_exp, required_exp):
        """Calculate experience match"""
        if required_exp == 0:
            return 100
        return min((resume_exp / required_exp) * 100, 100) if resume_exp else 0
    
    @classmethod
    def match(cls, resume, job):
        """Calculate overall match score"""
        skill_match, matching, missing = cls.calculate_skill_match(
            json.loads(resume.skills) if resume.skills else [],
            job.skills_required or ""
        )
        
        text_sim = cls.calculate_text_similarity(
            resume.extracted_text or "",
            job.description or ""
        )
        
        exp_match = cls.calculate_experience_match(
            resume.experience_years or 0,
            job.experience_required or 0
        )
        
        overall = (skill_match * 0.5) + (text_sim * 0.3) + (exp_match * 0.2)
        
        return {
            'score': round(overall, 1),
            'matching_skills': matching,
            'missing_skills': missing
        }

# ========== UTILITY FUNCTIONS ========== #

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========== ROUTES ========== #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validation
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if email and User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        hashed = generate_password_hash(password)
        user = User(username=username, email=email or None, password=hashed)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    
    # Calculate statistics
    total_resumes = len(resumes)
    avg_score = sum(r.score for r in resumes) / total_resumes if total_resumes else 0
    total_matches = Match.query.join(Resume).filter(Resume.user_id == current_user.id).count()
    
    stats = {
        'total_resumes': total_resumes,
        'avg_score': round(avg_score, 1),
        'total_matches': total_matches
    }
    
    return render_template('dashboard.html', resumes=resumes, stats=stats)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'resume' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(url_for('dashboard'))
    
    file = request.files['resume']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('dashboard'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Only PDF and DOCX allowed', 'danger')
        return redirect(url_for('dashboard'))
    
    # Save file
    original_name = file.filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{current_user.id}_{timestamp}_{secure_filename(original_name)}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Parse resume
    parsed = ResumeParser.parse(filepath)
    
    if not parsed:
        os.remove(filepath)
        flash('Failed to parse resume. Please check the file format.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Save to database
    resume = Resume(
        user_id=current_user.id,
        filename=filename,
        original_name=original_name,
        extracted_text=parsed['text'],
        skills=json.dumps(parsed['skills']),
        experience_years=parsed['experience_years'],
        education=parsed['education'],
        email=parsed['email'],
        phone=parsed['phone'],
        score=parsed['score']
    )
    
    db.session.add(resume)
    db.session.commit()
    
    flash(f'Resume uploaded! Score: {parsed["score"]}/100', 'success')
    return redirect(url_for('view_resume', resume_id=resume.id))

@app.route('/resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    
    if resume.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    skills = json.loads(resume.skills) if resume.skills else []
    matches = Match.query.filter_by(resume_id=resume_id).order_by(Match.match_score.desc()).limit(10).all()
    
    return render_template('resume_detail.html', resume=resume, skills=skills, matches=matches)

@app.route('/match/<int:resume_id>')
@login_required
def match_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    
    if resume.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    jobs = Job.query.filter_by(is_active=True).all()
    
    if not jobs:
        flash('No active jobs available', 'warning')
        return redirect(url_for('view_resume', resume_id=resume_id))
    
    # Delete old matches
    Match.query.filter_by(resume_id=resume_id).delete()
    
    # Create new matches
    for job in jobs:
        result = JobMatcher.match(resume, job)
        
        match = Match(
            resume_id=resume_id,
            job_id=job.id,
            match_score=result['score'],
            matching_skills=json.dumps(result['matching_skills']),
            missing_skills=json.dumps(result['missing_skills'])
        )
        db.session.add(match)
    
    db.session.commit()
    
    flash(f'Matched with {len(jobs)} jobs!', 'success')
    return redirect(url_for('view_resume', resume_id=resume_id))

@app.route('/jobs')
def jobs():
    search = request.args.get('search', '').strip()
    
    query = Job.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            db.or_(
                Job.title.ilike(f'%{search}%'),
                Job.company.ilike(f'%{search}%'),
                Job.skills_required.ilike(f'%{search}%')
            )
        )
    
    all_jobs = query.order_by(Job.posted_date.desc()).all()
    
    return render_template('jobs.html', jobs=all_jobs, search=search)

@app.route('/job/<int:job_id>')
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    skills = job.skills_required.split(',') if job.skills_required else []
    
    return render_template('job_detail.html', job=job, skills=skills)

@app.route('/delete-resume/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    
    if resume.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Delete file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], resume.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    db.session.delete(resume)
    db.session.commit()
    
    flash('Resume deleted successfully', 'success')
    return redirect(url_for('dashboard'))

# ========== ADMIN ROUTES ========== #

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('index'))
    
    stats = {
        'total_users': User.query.count(),
        'total_resumes': Resume.query.count(),
        'total_jobs': Job.query.count(),
        'total_matches': Match.query.count(),
        'active_jobs': Job.query.filter_by(is_active=True).count()
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_resumes = Resume.query.order_by(Resume.uploaded_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', stats=stats, recent_users=recent_users, recent_resumes=recent_resumes)

@app.route('/admin/add-job', methods=['GET', 'POST'])
@login_required
def add_job():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        job = Job(
            title=request.form.get('title'),
            company=request.form.get('company'),
            description=request.form.get('description'),
            skills_required=request.form.get('skills_required'),
            experience_required=int(request.form.get('experience_required', 0)),
            location=request.form.get('location'),
            salary=request.form.get('salary'),
            job_type=request.form.get('job_type', 'Full-time')
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('admin_jobs'))
    
    return render_template('add_job.html')

@app.route('/admin/jobs')
@login_required
def admin_jobs():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('index'))
    
    all_jobs = Job.query.order_by(Job.posted_date.desc()).all()
    return render_template('admin_jobs.html', jobs=all_jobs)

@app.route('/admin/toggle-job/<int:job_id>', methods=['POST'])
@login_required
def toggle_job(job_id):
    if not current_user.is_admin:
        return jsonify({'success': False}), 403
    
    job = Job.query.get_or_404(job_id)
    job.is_active = not job.is_active
    db.session.commit()
    
    return jsonify({'success': True, 'is_active': job.is_active})

@app.route('/admin/delete-job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('index'))
    
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    
    flash('Job deleted successfully', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('index'))
    
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=all_users)

# ========== ERROR HANDLERS ========== #

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(413)
def file_too_large(e):
    flash('File too large. Maximum size is 16MB', 'danger')
    return redirect(url_for('dashboard'))

# ========== DATABASE INITIALIZATION ========== #

def init_db():
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@resumeanalyzer.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            
            # Sample jobs
            jobs = [
                Job(
                    title='Senior Python Developer',
                    company='Tech Corp',
                    description='We are looking for an experienced Python developer with expertise in Django/Flask frameworks and REST API development.',
                    skills_required='python,django,flask,rest api,postgresql,git',
                    experience_required=5,
                    location='San Francisco, CA',
                    salary='$120,000 - $150,000',
                    job_type='Full-time'
                ),
                Job(
                    title='Full Stack JavaScript Developer',
                    company='StartUp Inc',
                    description='Join our team as a Full Stack Developer. Experience with React, Node.js, and MongoDB required.',
                    skills_required='javascript,react,nodejs,mongodb,html,css',
                    experience_required=3,
                    location='New York, NY',
                    salary='$90,000 - $120,000',
                    job_type='Full-time'
                ),
                Job(
                    title='Data Scientist',
                    company='AI Solutions',
                    description='Looking for a Data Scientist with strong machine learning background and Python expertise.',
                    skills_required='python,machine learning,tensorflow,pandas,numpy,sql',
                    experience_required=4,
                    location='Boston, MA',
                    salary='$110,000 - $140,000',
                    job_type='Full-time'
                ),
                Job(
                    title='DevOps Engineer',
                    company='Cloud Systems',
                    description='DevOps engineer needed for cloud infrastructure management and CI/CD pipeline development.',
                    skills_required='aws,docker,kubernetes,jenkins,terraform,linux',
                    experience_required=4,
                    location='Remote',
                    salary='$100,000 - $130,000',
                    job_type='Full-time'
                ),
                Job(
                    title='Frontend React Developer',
                    company='Web Agency',
                    description='Frontend developer specializing in React with modern JavaScript expertise.',
                    skills_required='react,javascript,typescript,html,css,redux',
                    experience_required=2,
                    location='Austin, TX',
                    salary='$80,000 - $100,000',
                    job_type='Full-time'
                )
            ]
            
            for job in jobs:
                db.session.add(job)
            
            db.session.commit()
            print("✅ Database initialized with admin and sample jobs!")
        else:
            print("✅ Database already initialized")

# ========== RUN APP ========== #

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("🚀 Resume Analyzer Server Starting...")
    print("="*60)
    print("📍 URL: http://127.0.0.1:5000")
    print("👤 Admin Login: admin / admin123")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)