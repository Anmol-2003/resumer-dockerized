from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, TIMESTAMP
from sqlalchemy.sql import func

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    userId = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(255), nullable = False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
class Profiles(Base):
    __tablename__ = 'profiles'

    # profileId = Column(Integer, primary_key = True, autoincrement=True)
    userId = Column(Integer, ForeignKey('users.userId'), nullable=False, primary_key = True)
    firstName = Column(String(255), nullable = False)
    lastName = Column(String(255), nullable= False)
    email = Column(String(255), unique=True, nullable=False)
    linkedinLink = Column(String(500), nullable = True)
    githubLink = Column(String(500), nullable = True)

class Education(Base):
    __tablename__ = 'education'

    eduId = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('users.userId'), nullable=False)
    institution = Column(Text, nullable=True)
    grade = Column(Float, nullable=True)
    duration = Column(Text, nullable=True)

class Experience(Base): 
    __tablename__ = 'experience'

    expId = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('users.userId'), nullable=False)
    title = Column(String(255), nullable = False)
    employer = Column(Text, nullable = False)
    duration = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

class Projects(Base):
    __tablename__ = 'projects'

    projectId = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('users.userId'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    techStack = Column(Text, nullable=False)

class Skills(Base): 
    __tablename__ = 'skills'

    skillsId = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('users.userId'), nullable=False)
    languages = Column(Text, nullable = False)
    frameworks = Column(Text, nullable=False)
    courses = Column(Text, nullable=False)
    certifications = Column(Text, nullable=False)


