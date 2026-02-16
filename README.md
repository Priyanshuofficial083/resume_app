# resume_app
# 🚀 AI Resume Analyzer & Job Matching System

A comprehensive full-stack web application that uses **Natural Language Processing (NLP)** and **Machine Learning** to analyze resumes, extract information, and match candidates with job opportunities.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Screenshots](#screenshots)
- [Contributing](#contributing)

## ✨ Features

### Core Features
- ✅ **Resume Upload & Parsing** - Upload PDF/DOCX files and extract text
- ✅ **Skill Extraction** - Automatically identify technical skills using NLP
- ✅ **Experience Detection** - Extract years of experience from resume text
- ✅ **Education Parsing** - Identify educational qualifications
- ✅ **Resume Scoring** - Calculate overall resume score (0-100)
- ✅ **Job Matching** - Intelligent matching algorithm using TF-IDF and cosine similarity
- ✅ **Skill Gap Analysis** - Identify missing skills for job requirements
- ✅ **Personalized Recommendations** - Get actionable advice to improve your resume

### Advanced Features
- 🔐 **JWT Authentication** - Secure user authentication and authorization
- 👤 **User Management** - Complete user registration and login system
- 🛡️ **Admin Dashboard** - Manage users, jobs, and view analytics
- 📊 **Analytics & Statistics** - Track resume scores, matches, and trends
- 🎯 **Multi-Job Matching** - Match one resume against multiple job descriptions
- 💾 **Database Storage** - All data stored in SQLite/PostgreSQL
- 🎨 **Modern UI/UX** - Beautiful, responsive interface with animations
- 📱 **Mobile Responsive** - Works seamlessly on all devices

## 🛠 Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **Flask-JWT-Extended** - JWT authentication

### NLP & ML Libraries
- **NLTK** - Natural Language Toolkit
- **spaCy** - Advanced NLP
- **scikit-learn** - Machine learning algorithms
- **PyPDF2 / pdfplumber** - PDF text extraction
- **python-docx** - DOCX file handling

### Frontend
- **HTML5 / CSS3**
- **JavaScript (Vanilla)**
- **Font Awesome** - Icons

### Database
- **SQLite** (Development)
- **PostgreSQL** (Production ready)

## 📁 Project Structure

```
resume_analyzer/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
│
├── database/
│   ├── models.py              # SQLAlchemy models
│   └── resume.db              # SQLite database (auto-generated)
│
├── utils/
│   ├── resume_parser.py       # Resume parsing logic
│   └── matcher.py             # Job matching algorithms
│
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Landing page
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # User dashboard
│   ├── resume_detail.html     # Resume analysis results
│   ├── jobs.html              # Job listings
│   ├── job_detail.html        # Job details
│   ├── admin_dashboard.html   # Admin panel
│   ├── admin_jobs.html        # Job management
│   ├── admin_users.html       # User management
│   ├── add_job.html           # Add new job
│   └── 404.html               # Error page
│
├── static/
│   ├── style.css              # Comprehensive CSS
│   └── script.js              # JavaScript functions
│
└── uploads/                    # Resume uploads (auto-generated)
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd resume_analyzer
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download NLP Models
```bash
# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 5: Initialize Database
```bash
python app.py
```
This will:
- Create the database
- Set up tables
- Create admin user (username: `admin`, password: `admin123`)
- Add sample job listings

### Step 6: Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## 📖 Usage

### For Job Seekers

1. **Register an Account**
   - Go to `/register`
   - Create your account with username, email, and password

2. **Login**
   - Go to `/login`
   - Enter your credentials

3. **Upload Resume**
   - From dashboard, click "Choose File"
   - Upload your resume (PDF or DOCX)
   - System will analyze automatically

4. **View Analysis**
   - See your resume score (0-100)
   - View extracted skills and experience
   - Check education information

5. **Find Job Matches**
   - Click "Find Jobs" on your resume
   - System will match with available jobs
   - View match scores and recommendations

### For Recruiters/Admins

1. **Login as Admin**
   - Username: `admin`
   - Password: `admin123`

2. **Post Jobs**
   - Go to Admin Dashboard
   - Click "Add New Job"
   - Fill in job details and required skills

3. **Manage Jobs**
   - View all job listings
   - Activate/Deactivate jobs
   - Track applications

4. **View Analytics**
   - Total users, resumes, and matches
   - Recent activity
   - User engagement metrics

## 🔌 API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /logout` - User logout

### Resume Management
- `POST /upload` - Upload and analyze resume
- `GET /resume/<id>` - View resume details
- `GET /match/<resume_id>` - Match resume with jobs

### Job Listings
- `GET /jobs` - View all active jobs
- `GET /job/<id>` - View job details
- `POST /admin/add-job` - Add new job (Admin)
- `POST /admin/job/<id>/toggle` - Toggle job status (Admin)

### Dashboard & Analytics
- `GET /dashboard` - User dashboard
- `GET /admin` - Admin dashboard
- `GET /api/stats` - Get user statistics

## 🗄 Database Schema

### Users Table
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- is_admin (Boolean)
- created_at (Timestamp)
```

### Resumes Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- filename
- extracted_text
- skills (JSON)
- experience_years
- education
- email_extracted
- phone_extracted
- overall_score
- uploaded_at (Timestamp)
```

### Job Descriptions Table
```sql
- id (Primary Key)
- title
- company
- description
- required_skills (JSON)
- experience_required
- location
- salary_range
- job_type
- posted_date (Timestamp)
- is_active (Boolean)
```

### Match Results Table
```sql
- id (Primary Key)
- resume_id (Foreign Key)
- job_id (Foreign Key)
- match_score
- matching_skills (JSON)
- missing_skills (JSON)
- recommendations (JSON)
- created_at (Timestamp)
```

## 🎯 Key Algorithms

### Resume Scoring Algorithm
```python
- Skills Score: 40% (based on number of skills)
- Experience Score: 30% (years of experience)
- Education Score: 15% (degree level)
- Resume Quality: 15% (length and formatting)
```

### Job Matching Algorithm
```python
- Skill Match: 50% (matching vs required skills)
- Text Similarity: 30% (TF-IDF + Cosine Similarity)
- Experience Match: 20% (candidate vs required experience)
```

## 🎨 Features Showcase

### Skill Extraction
The system recognizes 70+ technical skills across categories:
- Programming Languages
- Web Technologies
- Databases
- Cloud Platforms
- Data Science & ML
- Tools & Frameworks

### Smart Recommendations
Personalized advice based on:
- Missing skills for target jobs
- Experience gaps
- Resume optimization tips
- Career advancement suggestions

## 🔒 Security Features

- Password hashing using Werkzeug
- Session-based authentication with Flask-Login
- JWT token support for API access
- CSRF protection
- SQL injection prevention (SQLAlchemy ORM)
- File upload validation
- Admin-only routes protection

## 📊 Performance Optimizations

- Efficient database queries with SQLAlchemy
- Caching of parsed resumes
- Batch processing for multiple job matches
- Optimized NLP model loading
- Indexed database columns

## 🌐 Deployment

### Deploy on Render / Railway / Heroku

1. **Update Database URI** (for production)
```python
# app.py
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
```

2. **Add Procfile**
```
web: gunicorn app:app
```

3. **Update requirements.txt**
```
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

4. **Set Environment Variables**
```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
```

## 🧪 Testing

Run tests (if you add them):
```bash
pytest tests/
```

## 📝 Default Credentials

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change the admin password after first login!

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues

- Large PDF files (>16MB) are not supported
- Some scanned PDFs may not extract text properly
- Complex formatting may affect parsing accuracy

## 🔮 Future Enhancements

- [ ] Real-time resume editing
- [ ] Video resume support
- [ ] Interview scheduling
- [ ] Email notifications
- [ ] LinkedIn integration
- [ ] Advanced analytics dashboard
- [ ] Resume templates
- [ ] Cover letter generator
- [ ] Salary prediction ML model

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Your Name - [Your GitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- NLTK & spaCy teams for NLP libraries
- Flask community for excellent documentation
- All contributors and testers

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@resumeanalyzer.com

---

Made with ❤️ for job seekers and recruiters

**⭐ Star this repo if you find it useful!**

