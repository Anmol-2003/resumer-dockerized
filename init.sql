CREATE DATABASE IF NOT EXISTS resumer;
USE resumer;

CREATE TABLE users (
    userId INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE profiles (
    userId INTEGER PRIMARY KEY,
    firstName VARCHAR(255) NOT NULL,
    lastName VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    linkedinLink VARCHAR(500),
    githubLink VARCHAR(500),
    FOREIGN KEY (userId) REFERENCES users(userId)
);

CREATE TABLE projects (
    projectId INT PRIMARY KEY AUTO_INCREMENT, 
    userId INT, 
    title TEXT, 
    description TEXT, 
    duration TEXT, 
    techStack TEXT, 
    FOREIGN KEY (userId) REFERENCES users(userId)
);

CREATE TABLE education (
    eduId INT PRIMARY KEY AUTO_INCREMENT, 
    userId INT, 
    institution TEXT NOT NULL, 
    duration TEXT, 
    grade FLOAT NOT NULL,
    location CHAR(255), 
    FOREIGN KEY (userId) REFERENCES users(userId)
);

CREATE TABLE skills (
    skillsId INT PRIMARY KEY AUTO_INCREMENT, 
    userId INT, 
    languages TEXT, 
    frameworks TEXT, 
    certifications TEXT, 
    courses TEXT, 
    FOREIGN KEY (userId) REFERENCES users(userId)
);

CREATE TABLE experience (
    expId INT PRIMARY KEY AUTO_INCREMENT, 
    userId INT, 
    title TEXT, 
    employer TEXT,
    duration TEXT, 
    description TEXT, 
    FOREIGN KEY (userId) REFERENCES users(userId)
);
