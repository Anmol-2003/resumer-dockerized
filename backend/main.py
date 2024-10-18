import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from utils.db_connector import get_async_session
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, Response
from models import api_models, db_models
from utils.agent.resumer import agent, generateLatexCode
# from utils.agent.latexToPdf import generatePDF
import asyncio
import subprocess
import os
app = FastAPI()



@app.get('/')
def buffer():
    return api_models.BufferResponse(message='Request received', status_code=200)

@app.post('/register')
async def register(user : dict, session : AsyncSession = Depends(get_async_session)):
    ## registering the user. 
    dataToRegister = db_models.Users(
        firstName = user['firstName'], 
        lastName = user['lastName'], 
        email = user['email'], 
        linkedinLink = user['linkedinLink'], 
        githubLink = user['githubLink']
    )
    print(dataToRegister)
    async with session.begin():
        session.add(dataToRegister)
        await session.commit()
    
    return api_models.Response(message='User successfully registered', data= 'gay', status_code=201)

@app.post('/saveUserDetails')
async def saveUserDetails(user_id : int, projects : api_models.Projects, exp : api_models.Experience, skills : api_models.Skills, session : AsyncSession = Depends(get_async_session)):
    async with session.begin():
        session.add(db_models.Projects(projects))
        session.add(db_models.Experience(exp))
        session.add(db_models.Skills(skills))
        await session.commit()
    return api_models.Success(message='Data saved successfully', status_code=201)

@app.post('/saveProject')
async def saveProject(data : api_models.Projects, session : AsyncSession = Depends(get_async_session)):
    project = db_models.Projects(
            userId = data.userId, 
            title = data.title, 
            description = data.description, 
            techStack = data.techStack)
    async with session.begin():
        session.add(project)
        await session.commit()
    return api_models.Success(message='Project Saved Successfully')

@app.post('/saveExperience')
async def saveExperience(data : api_models.Experience,  session : AsyncSession = Depends(get_async_session)):
    expDetails = db_models.Experience(
        userId = data.userId, 
        title = data.title, 
        employer = data.employer, 
        description = data.description, 
        duration = data.duration
    )
    async with session.begin():
        session.add(expDetails)
        await session.commit()
    return api_models.Success(message='Experience saved successfully')

@app.post('/saveSkills')
async def saveSkills(data : api_models.Skills, session : AsyncSession = Depends(get_async_session)):
    skillsDetails = db_models.Skills(
            userId = data.userId,
        languages = data.languages, 
        frameworks = data.frameworks, 
        courses = data.courses, 
        certifications = data.certifications
    )
    async with session.begin():
        session.add(skillsDetails)
        await session.commit()
    return api_models.Success(message='Skills saved')

# generate resume API under development
@app.post('/generateResume')
async def generateResume(data : dict, session : AsyncSession=Depends(get_async_session)):
    print('received request')
    user_id = data['user_id']
    project_stmt = text('select projects.title, projects.description, projects.techStack from users join projects where users.userId = :user_id')
    experience_stmt = text('select experience.title, experience.employer, experience.duration, experience.description from users join experience where users.userId=:user_id')
    skills_stmt = text('select skills.languages, skills.frameworks, skills.certifications, skills.courses from skills join users where users.userId = :user_id')
    user_stmt = text('select firstName, lastName, email, linkedinLink, githubLink from users where userId = :user_id')
    edu_stmt = text('select education.institution, education.grade, education.duration from education JOIN users where users.userId = :user_id')
    
    async with session.begin():
        projects = await session.execute(project_stmt, {'user_id' : user_id})
        experience = await session.execute(experience_stmt, {'user_id' : user_id})
        skills = await session.execute(skills_stmt, {'user_id' : user_id})
        userDetails = await session.execute(user_stmt, {'user_id' : user_id})
        education = await session.execute(edu_stmt, {'user_id' : user_id})

    projectData = f"""PROJECTS \n"""
    experienceData = f"""EXPERIENCE \n"""
    skillsData = f"""SKILLS \n"""
    for title, desc, techStack in projects.fetchall():
        t = f"Title: {title} \nTechStack: {techStack} \n Description: {desc}"
        projectData += t + '\n\n'

    for title, emp, dur, desc in experience.fetchall():
        t = f"Title: {title} \nEmployer: {emp} \nDuration: {dur} \nDescription: {desc}"
        experienceData += t + '\n\n'
    
    for langs, frames, cert, courses in skills.fetchall():
        t = f"Languages: {langs} \nFrameworks: {frames} \nCertifications: {cert} \nCourses: {courses}"
        skillsData += t + '\n\n'
    print('data extracted from db')
    await asyncio.sleep(1)

    print("Invoking the agent")
    result = agent.invoke({'job_description' : data['job_description'], 'userProjects' : projectData, 'userExperience' : experienceData, 'userSkills' : skillsData})
    print(f"\n\n\n RESULT \n\n\n{result['resume']}")


    educationDetails = ""
    for inst, grade, dur in education.fetchall():
        t = f"Institution : {inst} \nGrade: {grade} \nDuration: {dur}"
        educationDetails += t + '\n\n'


    resumeData = f"""
    User Details \n
    {userDetails.fetchall()}\n\n
    Education \n
    {educationDetails} \n\n
    {result['resume']} \n\n
    {skillsData}
    """
    # Generating the LaTeX code. 
    latex = await generateLatexCode(resume=resumeData, latex_code=latex_code)
    print('Latex Code generated')
    print('\n\n\n LATEX CODE \n\n',latex['Data']) 

    # Generaating the PDF from the .tex file
    #await generatePDF(latex['Data'])
    
    CMD = "pdflatex -interaction=nonstopmode resume.tex"

    with open('resume.tex', 'w') as f:
        f.write(latex['Data'])
    if os.path.exists('resume.tex'):
        process = subprocess.run(CMD, shell=True, capture_output=True, text=True)
        print('ERROR: \t', process.stderr, end='\n\n')
        print('OUTPUT: \t', process.stdout, end='\n\n')
    if os.path.exists('resume.pdf'):
      return FileResponse(
              path='resume.pdf', 
              media_type = 'application/pdf'
              )
    return Response(status_code = 500, content="Resume.pdf doesn't exist")
    #return api_models.Success(message="Resume generated successfully")


latex_code = r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}




\begin{document}

%----------HEADING----------
% \begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
%   \textbf{\href{http://sourabhbajaj.com/}{\Large Sourabh Bajaj}} & Email : \href{mailto:sourabh@sourabhbajaj.com}{sourabh@sourabhbajaj.com}\\
%   \href{http://sourabhbajaj.com/}{http://www.sourabhbajaj.com} & Mobile : +1-123-456-7890 \\
% \end{tabular*}

\begin{center}
    \textbf{\Huge \scshape Jake Ryan} \\ \vspace{1pt}
    \small 123-456-7890 $|$ \href{mailto:x@x.com}{\underline{jake@su.edu}} $|$ 
    \href{https://linkedin.com/in/...}{\underline{linkedin.com/in/jake}} $|$
    \href{https://github.com/...}{\underline{github.com/jake}}
\end{center}


%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Southwestern University}{Georgetown, TX}
      {Bachelor of Arts in Computer Science, Minor in Business}{Aug. 2018 -- May 2021}
    \resumeSubheading
      {Blinn College}{Bryan, TX}
      {Associate's in Liberal Arts}{Aug. 2014 -- May 2018}
  \resumeSubHeadingListEnd


%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart

    \resumeSubheading
      {Undergraduate Research Assistant}{June 2020 -- Present}
      {Texas A\&M University}{College Station, TX}
      \resumeItemListStart
        \resumeItem{Developed a REST API using FastAPI and PostgreSQL to store data from learning management systems}
        \resumeItem{Developed a full-stack web application using Flask, React, PostgreSQL and Docker to analyze GitHub data}
        \resumeItem{Explored ways to visualize GitHub collaboration in a classroom setting}
      \resumeItemListEnd
      
% -----------Multiple Positions Heading-----------
%    \resumeSubSubheading
%     {Software Engineer I}{Oct 2014 - Sep 2016}
%     \resumeItemListStart
%        \resumeItem{Apache Beam}
%          {Apache Beam is a unified model for defining both batch and streaming data-parallel processing pipelines}
%     \resumeItemListEnd
%    \resumeSubHeadingListEnd
%-------------------------------------------

    \resumeSubheading
      {Information Technology Support Specialist}{Sep. 2018 -- Present}
      {Southwestern University}{Georgetown, TX}
      \resumeItemListStart
        \resumeItem{Communicate with managers to set up campus computers used on campus}
        \resumeItem{Assess and troubleshoot computer problems brought by students, faculty and staff}
        \resumeItem{Maintain upkeep of computers, classroom equipment, and 200 printers across campus}
    \resumeItemListEnd
  \resumeSubHeadingListEnd


%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
          {\textbf{Gitlytics} $|$ \emph{Python, Flask, React, PostgreSQL, Docker}}{June 2020 -- Present}
          \resumeItemListStart
            \resumeItem{Developed a full-stack web application using with Flask serving a REST API with React as the frontend}
            \resumeItem{Implemented GitHub OAuth to get data from user’s repositories}
            \resumeItem{Visualized GitHub data to show collaboration}
            \resumeItem{Used Celery and Redis for asynchronous tasks}
          \resumeItemListEnd
    \resumeSubHeadingListEnd

%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Languages}{: Java, Python, C/C++, SQL (Postgres), JavaScript, HTML/CSS, R} \\
     \textbf{Frameworks}{: React, Node.js, Flask, JUnit, WordPress, Material-UI, FastAPI} \\
     \textbf{Developer Tools}{: Git, Docker, TravisCI, Google Cloud Platform, VS Code, Visual Studio, PyCharm, IntelliJ, Eclipse} \\
     \textbf{Libraries}{: pandas, NumPy, Matplotlib}
    }}
 \end{itemize}
\end{document}
"""
