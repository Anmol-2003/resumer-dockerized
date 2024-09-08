CREATE DATABASE IF NOT EXISTS resumer;
USE resumer;

create table users(
    userId int primary key auto_increment, 
    firstName char(255) not null, 
    lastName char(255) not null, 
    email varchar(255) unique not null, 
    linkedinLink varchar(500) unique not null, 
    githubLink varchar(500) unique not null
);

create table projects(
    projectId int primary key auto_increment, 
    userId int, 
    title text, 
    description text, 
    duration text, 
    techStack text, 
    foreign key (userId) references users(userId)
);

create table education(
    eduId int primary key auto_increment, 
    userId int , 
    institution text not null, 
    duration text, 
    grade float not null,
    location char(255), 
    foreign key (userId) references users(userId)
);

create table skills(
    skillsId int primary key auto_increment, 
    userId int, 
    languages text, 
    frameworks text, 
    certifications text, 
    courses text, 
    foreign key (userId) references users(userId)
);
create table experience(
   expId int primary key auto_increment, 
   userId int, 
   title text, 
   employer text,
   duration text, 
   description text, 
   foreign key (userId) references users(userId));

insert into users(firstName, lastName, email, linkedinLink, githubLink) values('Anmol', 'Bhardwaj', 'anmol03kw@gmail.com', 'https://www.linkedin.com/in/anmol-bhardwaj-55374321a/', 'https://github.com/Anmol-2003');
insert into experience(userId, title, employer, duration, description) 
values
(
  1, 
  'Research Intern', 
  'Goldsmiths University, London', 
  'November 2023 - February 2024', 
  'Mapped MELD mulimodal dataset inputs to MBTI classes for classification of personalities based on audio and text input. Developed a neural network in keras framework for accepting audio and text features achieving 95.8% accuracy. Creating the dataset was aided using a Roberta model trained on MBTI with 98% accuracy.'
), 
(
  1, 
  'AI Engineer',
  'RizzAI, Delhi', 
  'February 2024 - April 2024', 
  'Developed inference scripts for various SOTA vision language and CV models for producing descriptions of image data. Scraped over 1000 shopify based websites using asynchronous python script and stored the data into postgres using ORM for efficient retrieval.'
), 
(
    1, 
    'Full Stack Developer', 
    'Gabbit Trans systems pvt Ltd., Delhi', 
    'June 2024 - September 2024', 
    'Lead the development of the mobile application using flutter. Worked together with other peers to implment the relational database model in MySQL. Developed APIs for fetching user data like pdfs, appointments etc.'
);

insert into projects(userId, title, description, duration, techStack) values 
(
    1, 
    'Resumer', 
    "Developed a web application for generating resumes using candidate's information and provided job-description. A reflexion based AI agent developed using langgraph powered by state-of-the-art models like Gemini-1.5 pro and llama 3.1 is the backbone behind the product. 
    Generated resumes achieve high target and open-ended scores on multiple ATS scanning websites. Deployed the entire system on google cloud using a multi-container application using docker.", 
    'August 2024 - September 2024', 
    'FastAPI, Langgraph, Google cloud platform, Docker, Google AI Studio, Meta Llama 3.1'
), 
(
    1, 
    "SocioTrackr", 
    "Developed a web-application for providing meaningful insights on social media profiles based on video, images and text modailities. Developed multiple model inference API's for efficient and low-latency responses. Combination of models like Clip and Blip were used to extract insights from video data. Implemented the system on Youtube Shorts, Instagram and Reddit.", 
    "November 2023 - December 2023", 
    "Selenium, Flask, GCP, Hugging face, OpenAI"
), 
(
    1, 
    "LegalEase", 
    "Developed a mobile application in Flutter for generating legal documents using RAG model built using langchain. Utilized chromaDB for efficient query and retrieval of vectorized documents, produced using SOTA embedding models. Used HNSW similarity search algorithnm for retrieval and re-ranker module for post-retreival process.", 
    "April 2024 - April 2024", 
    "Langchain, Flutter, Python"
);

insert into education(userId, institution, location, grade, duration) values
(
    1, 
    'Delhi Technological University', 
    'Delhi', 
    8.44, 
    'Nov 2024 - July 2026'

);

insert into skills(userId, languages, frameworks, certifications, courses) 
values(
    1, 
    'Python, C++, Dart, SQL, Js(basics)', 
    'Langchain, FastAPI, Express.js, tensorflow, keras, pytorch, MySQL, PostgreSQL, Cassandra, Scikit-learn, Flutter, llama-index', 
    'Machine Learning Specialization, Machine Learning for Production (MLOPs)', 
    'OOPS, DBMS, Data Structures and Algorithms, Operating Systems'); 
