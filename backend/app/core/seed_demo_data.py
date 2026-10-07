import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.models.profile import Profile
from app.models.skill import Skill
from app.models.user_skill import UserSkill, SkillType
from app.core.security import hash_password

DEMO_STUDENTS = [
    {
        "email": "sophia.chen.demo@skillswap.edu",
        "full_name": "Sophia Chen",
        "college": "Stanford University",
        "branch": "UI/UX & Product Design",
        "year": 3,
        "bio": "Passionate UI/UX designer with 3 years of Figma experience. Love building clean, accessible component libraries and interactive prototypes.",
        "location": "Stanford Campus / Remote",
        "availability": "Mon/Wed/Fri after 4 PM",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
        "gender_preference": "Female",
        "offered_skills": [("Figma", "UI/UX & Graphic Design", 5), ("UI/UX Design", "UI/UX & Graphic Design", 4)],
        "wanted_skills": [("React.js", "Programming & Web Dev", 3), ("Python", "Data Science & AI", 2)]
    },
    {
        "email": "marcus.vance.demo@skillswap.edu",
        "full_name": "Marcus Vance",
        "college": "Stanford University",
        "branch": "Data Science & AI",
        "year": 4,
        "bio": "Senior studying Data Science. Specializing in Python data analysis, pandas, and machine learning models. Happy to tutor math & Python!",
        "location": "Green Library / Online",
        "availability": "Tue/Thu evenings",
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80",
        "gender_preference": "Male",
        "offered_skills": [("Python", "Data Science & AI", 5), ("Machine Learning", "Data Science & AI", 4)],
        "wanted_skills": [("React.js", "Programming & Web Dev", 3), ("UI/UX Design", "UI/UX & Graphic Design", 2)]
    },
    {
        "email": "elena.rostova.demo@skillswap.edu",
        "full_name": "Elena Rostova",
        "college": "UC Berkeley",
        "branch": "Foreign Languages & International Relations",
        "year": 2,
        "bio": "Fluent native Spanish and French speaker. Eager to practice conversational languages and help peers master grammar and public speaking.",
        "location": "Berkeley / Zoom",
        "availability": "Weekends",
        "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80",
        "gender_preference": "Female",
        "offered_skills": [("Spanish", "Foreign Languages", 5), ("Public Speaking", "Business", 4)],
        "wanted_skills": [("Python", "Data Science & AI", 2), ("Web Development", "Programming & Web Dev", 2)]
    },
    {
        "email": "alex.rivera.demo@skillswap.edu",
        "full_name": "Alex Rivera",
        "college": "Stanford University",
        "branch": "Computer Science",
        "year": 3,
        "bio": "Full-stack enthusiast working with React, Node.js, and PostgreSQL. Excited to swap code reviews for UI design tips!",
        "location": "Campus / Remote",
        "availability": "Weekday afternoons",
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80",
        "gender_preference": "Male",
        "offered_skills": [("React.js", "Programming & Web Dev", 5), ("Web Development", "Programming & Web Dev", 4)],
        "wanted_skills": [("Figma", "UI/UX & Graphic Design", 3), ("Spanish", "Foreign Languages", 2)]
    },
    {
        "email": "sarah.jenkins.demo@skillswap.edu",
        "full_name": "Sarah Jenkins",
        "college": "MIT",
        "branch": "Mechanical Engineering & Physics",
        "year": 4,
        "bio": "Robotics student passionate about Calculus, Physics, and 3D Modeling. Looking to learn video production and graphic design.",
        "location": "Boston / Remote",
        "availability": "Flexible",
        "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&auto=format&fit=crop&q=80",
        "gender_preference": "Female",
        "offered_skills": [("Calculus", "Math & Physics", 5), ("Physics", "Math & Physics", 4)],
        "wanted_skills": [("Video Production", "Media", 2), ("Graphic Design", "UI/UX & Graphic Design", 2)]
    }
]

def seed_demo_profiles(db: Session):
    """
    Seeds controlled demo student profiles into PostgreSQL with is_demo=True, is_test=False.
    """
    for data in DEMO_STUDENTS:
        existing_user = db.scalar(select(User).where(User.email == data["email"]))
        if existing_user:
            # Update profile is_demo flag if user exists
            prof = db.get(Profile, existing_user.id)
            if prof:
                prof.is_demo = True
                prof.is_test = False
                prof.avatar_url = data["avatar_url"]
                prof.gender_preference = data["gender_preference"]
            continue

        # Create demo user
        user = User(
            email=data["email"],
            password_hash=hash_password("DemoPass123!"),
            is_active=True
        )
        db.add(user)
        db.flush()

        # Create demo profile
        profile = Profile(
            user_id=user.id,
            full_name=data["full_name"],
            college=data["college"],
            branch=data["branch"],
            year=data["year"],
            bio=data["bio"],
            location=data["location"],
            availability=data["availability"],
            avatar_url=data["avatar_url"],
            gender_preference=data["gender_preference"],
            is_demo=True,
            is_test=False
        )
        db.add(profile)
        db.flush()

        # Add offered skills
        for name, cat, prof_lvl in data["offered_skills"]:
            skill = db.scalar(select(Skill).where(Skill.name == name))
            if not skill:
                skill = Skill(name=name, category=cat)
                db.add(skill)
                db.flush()
            us = UserSkill(
                user_id=user.id,
                skill_id=skill.id,
                skill_type=SkillType.OFFER,
                proficiency=prof_lvl
            )
            db.add(us)

        # Add wanted skills
        for name, cat, prof_lvl in data["wanted_skills"]:
            skill = db.scalar(select(Skill).where(Skill.name == name))
            if not skill:
                skill = Skill(name=name, category=cat)
                db.add(skill)
                db.flush()
            us = UserSkill(
                user_id=user.id,
                skill_id=skill.id,
                skill_type=SkillType.WANT,
                proficiency=prof_lvl
            )
            db.add(us)

    db.commit()
    print("Demo profiles successfully seeded into PostgreSQL!")
