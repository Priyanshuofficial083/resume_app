import os
import sys

def reset_database():
    """Force delete and recreate database"""
    db_file = 'resume.db'
    
    # Check if database exists
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"✅ Deleted old database: {db_file}")
        except PermissionError:
            print("❌ ERROR: Database file is locked!")
            print("   Please close all applications using it and try again.")
            print("   Close VS Code, terminal, and any SQLite viewers.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            sys.exit(1)
    else:
        print("⚠️  No old database found (this is fine)")
    
    # Import app and create fresh database
    print("\n🔄 Creating new database...")
    
    try:
        from app import app, db, User, generate_password_hash, Job
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Created database tables")
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@resumeanalyzer.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            
            # Create sample jobs
            jobs = [
                Job(
                    title='Senior Python Developer',
                    company='Tech Corp',
                    description='Python developer with Django/Flask experience needed.',
                    skills_required='python,django,flask,rest api,postgresql,git',
                    experience_required=5,
                    location='San Francisco, CA',
                    salary='$120,000 - $150,000',
                    job_type='Full-time'
                ),
                Job(
                    title='Full Stack Developer',
                    company='StartUp Inc',
                    description='Full Stack Developer with React and Node.js experience.',
                    skills_required='javascript,react,nodejs,mongodb,html,css',
                    experience_required=3,
                    location='New York, NY',
                    salary='$90,000 - $120,000',
                    job_type='Full-time'
                ),
                Job(
                    title='Data Scientist',
                    company='AI Solutions',
                    description='Data Scientist with ML and Python expertise.',
                    skills_required='python,machine learning,tensorflow,pandas,numpy,sql',
                    experience_required=4,
                    location='Boston, MA',
                    salary='$110,000 - $140,000',
                    job_type='Full-time'
                )
            ]
            
            for job in jobs:
                db.session.add(job)
            
            db.session.commit()
            
            print("✅ Created admin user (admin/admin123)")
            print("✅ Created sample jobs")
            print("\n" + "="*60)
            print("🎉 DATABASE RESET COMPLETE!")
            print("="*60)
            print("\nNow run: python app.py")
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("="*60)
    print("🔄 RESETTING DATABASE")
    print("="*60)
    reset_database()