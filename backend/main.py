from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.db_connector import get_async_session
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from models import api_models, db_models
from utils.agent.resumer import agent, generateLatexCode
import asyncio
import subprocess
import os
from authentication.auth import router as authentication_route

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for specific domains
    allow_credentials=True,
    allow_methods=["*"], # METHODS to be allowed to the server
    allow_headers=["*"], # pdf, json etc
)

# Attaching the authentication route with the main application
app.include_router(authentication_route, tags=["auth"])

@app.get('/')
def buffer():
    return api_models.BufferResponse(message='Request received', status_code=200)
@app.post('/saveUserProfile/{userId}')
async def save_user_profile(userId: int, data: api_models.Profile, session: AsyncSession = Depends(get_async_session)):
    profile = db_models.Profiles(
        userId=userId,
        firstName=data.firstName,
        lastName=data.lastName,
        email=data.email,
        githubLink=data.githubLink,
        linkedinLink=data.linkedinLink
    )
    try:
        async with session.begin():
            session.add(profile)
            print('Profile added to database')
    except Exception as e:
        print(e)
        return JSONResponse(content={'message': 'Exception occurred while inserting data', 'status_code': 500, 'data': ''})
    return JSONResponse(content={'message': 'success', 'status_code': 200})

'''
@app.post('/saveUserProfile/{userId}')
async def saveUserProfile(userId : int, data : api_models.Profile, session : AsyncSession = Depends(get_async_session)):
    profile = db_models.Profiles(userId = userId, firstName = data.firstName, lastName = data.lastName, email = data.email, githubLink = data.githubLink, linkedinLink = data.linkedinLink)
    try:
        await session.begin()
        await session.add(profile)
        await session.commit()
    except Exception as e: 
        print(e)
        return JSONResponse(content={'message' : 'Exception occured while inserting data' , 'status_code' : 500, 'data' : ''})
    return JSONResponse(content={'message' :'success', 'status_code' : 200})
'''
@app.post('/saveProject')
async def saveProject( data : api_models.Projects, session : AsyncSession = Depends(get_async_session)):
    try:
      project = db_models.Projects(
              userId = data.userId, 
              title = data.title, 
              description = data.description, 
              techStack = data.techStack)
      async with session.begin():
          session.add(project)
      return JSONResponse(content={'message' : 'Data saved successfully', 'status_code' : 200})
    except Exception as e:
        print(e)
        return JSONResponse(content={'message' : 'Error occured in saving the data', 'status_code' : 500})
    
@app.post('/saveExperience')
async def saveExperience(data : api_models.Experience,  session : AsyncSession = Depends(get_async_session)):
    try:
      expDetails = db_models.Experience(
          userId = data.userId, 
          title = data.title, 
          employer = data.employer, 
          description = data.description, 
          duration = data.duration
      )
      async with session.begin():
          session.add(expDetails)
      return JSONResponse(content={'message' : 'Data saved successfully', 'status_code' : 200})
    except Exception as e:
        print(e)
        return JSONResponse(content={'message' : 'Error occured in saving the data', 'status_code' : 500})
    

@app.post('/saveEducation')
async def saveEducation(data : api_models.Education, session : AsyncSession = Depends(get_async_session)):
    try:
        eduDetails = db_models.Education(
            userId = data.userId, 
            institution = data.institution, 
            duration = data.duration, 
            location = data.location, 
            grade = data.grade
        )
        async with session.begin():
          session.add(eduDetails)
        return JSONResponse(content={'message' : 'Data saved successfully', 'status_code' : 200})
    except Exception as e:
        print(e)
        return JSONResponse(content={'message' : 'Error occured in saving the data', 'status_code' : 500})
    


# @app.post('/saveSkills')
# async def saveSkills(data : api_models.Skills, session : AsyncSession = Depends(get_async_session)):
#     skillsDetails = db_models.Skills(
#             userId = data.userId,
#         languages = data.languages, 
#         frameworks = data.frameworks, 
#         courses = data.courses, 
#         certifications = data.certifications
#     )
#     async with session.begin():
#         session.add(skillsDetails)
#         await session.commit()
#     return api_models.Success(message='Skills saved')


@app.post('/saveSkills') 
async def saveSkills(data : api_models.Skills, session : AsyncSession = Depends(get_async_session)):
    print(data)
    skillsData = db_models.Skills(
            userId = data.userId, 
            languages = data.languages, 
            courses = data.courses, 
            frameworks = data.frameworks, 
            certifications = data.certifications)
    try:
        async with session.begin(): 
            session.add(skillsData)
    except Exception as e: 
        print(e)
        return JSONResponse(content={'message' : 'Internal server error', 'status_code' : 500})
    return JSONResponse(content={'message' : 'Data saved', 'status_code' : 200})



@app.get('/fetchUserDetails/{userId}')
async def fetchUserDetails(userId : str,  session : AsyncSession = Depends(get_async_session)):
    details = None

    def result_to_dict(results):
      return [dict(row._mapping) for row in results] # list of dicts
    try:
      async with session.begin():
          # Profile
          stmt = text('select * from profiles where userId = :userId')
          profile = await session.execute(stmt, {'userId' : userId})
          profile = result_to_dict(profile.fetchall())

          # Projects
          stmt = text('select * from projects where userId = :userId')
          projects = await session.execute(stmt, {'userId' : userId})
          projects = result_to_dict(projects.fetchall())

          # Experience 
          stmt = text('select * from experience where userId = :userId')
          experience = await session.execute(stmt, {'userId' : userId})
          experience = result_to_dict(experience.fetchall())

          # education
          stmt = text('select * from education where userId = :userId')
          education = await session.execute(stmt, {'userId' : userId})
          education = result_to_dict(education.fetchall())

          # skills
          stmt = text('select * from skills where userId = :userId')
          skills = await session.execute(stmt, {'userId' : userId})
          skills = result_to_dict(skills.fetchall())
      
      
      details = {
          'Profile' : profile, 
          'Projects' : projects, 
          'Experience' : experience, 
          'Education' : education, 
          'Skills' : skills
      }
      print('DETAILS\n\n', details)
      if not details:
          return JSONResponse(content={'message' : 'User not found', 'status_code' : 500})
      
      
      return JSONResponse(content={
          'message' : 'successful retrieval of data', 
          'status_code' : 200, 
          'data' : details
      })
    except Exception as e: 
        print(e)
        return JSONResponse(content = {'message' : 'Host error', 'status_code' : 500})
    
## Deleting data
@app.delete('/deleteDetails/{content}/{itemId}')
async def deleteDetails(content : str, itemId : int, session : AsyncSession = Depends(get_async_session)):
    try:
        if content == 'experience':
            await session.begin()
            stmt = text('delete from experience where expId = :expId')
            await session.execute(stmt, {'expId' : itemId})
            await session.commit()
        elif content == 'projects':
            await session.begin()
            stmt = text('delete from projects where projectId = :projectId')
            await session.execute(stmt, {'projectId' : itemId})
            await session.commit()
        elif content == 'education':
            await session.begin()
            stmt = text('delete from education where eduId = :eduId')
            await session.execute(stmt, {'eduId' : itemId})
            await session.commit()
        else :
            return JSONResponse(content={
                'message' : 'Invalid client request', 
                'status_code' : 400,
            })
        return JSONResponse(content={'message' : 'Detail deleted successfully', 'status_code' : 200})
    except Exception as e:
        print(e)
        return JSONResponse(content={'message' : 'Error while deleting data', 'status_code' : 500})

## Updating the details
@app.post('/updateDetails/{content}/{itemId}')
async def updateDetails(content: str, itemId: int, data: dict, session: AsyncSession = Depends(get_async_session)):
    try:
        # Updating the values depending on the content being updated
        old_data = None
        
        if content == 'experience':
            await session.begin()
            stmt = text('select * from experience where expId = :expId')
            result = await session.execute(stmt, {'expId': itemId})
            old_data = result.fetchone()
            new_values = {**dict(old_data._mapping), **data}  # Merging old and new data
            stmt = update(db_models.Experience).where(db_models.Experience.expId == itemId).values(new_values)
            print(new_values)
            await session.execute(stmt)
            await session.commit()

        elif content == 'projects':
            await session.begin()
            stmt = text('select * from projects where projectId = :projectId')
            result = await session.execute(stmt, {'projectId': itemId})
            old_data = result.fetchone()
            new_values = {**dict(old_data._mapping), **data}
            stmt = update(db_models.Projects).where(db_models.Projects.projectId == itemId).values(new_values)
            await session.execute(stmt)
            await session.commit()

        elif content == 'profiles':
            await session.begin()
            stmt = text('select * from profiles where userId = :userId')
            result = await session.execute(stmt, {'userId': itemId})
            old_data = result.fetchone()
            new_values = {**dict(old_data._mapping), **data}
            stmt = update(db_models.Profiles).where(db_models.Profiles.userId == itemId).values(new_values)
            await session.execute(stmt)
            await session.commit()

        elif content == 'education':
            await session.begin()
            stmt = text('select * from education where eduId = :eduId')
            result = await session.execute(stmt, {'eduId': itemId})
            old_data = result.fetchone()
            new_values = {**dict(old_data._mapping), **data}
            stmt = update(db_models.Education).where(db_models.Education.eduId == itemId).values(new_values)
            await session.execute(stmt)
            await session.commit()

        elif content == 'skills':
            await session.begin()
            stmt = text('select * from skills where skillsId = :skillsId')
            result = await session.execute(stmt, {'skillsId': itemId})
            old_data = result.fetchone()
            new_values = {**dict(old_data._mapping), **data}
            stmt = update(db_models.Skills).where(db_models.Skills.skillsId == itemId).values(new_values)
            await session.execute(stmt)
            await session.commit()

        else:
            return JSONResponse(content={'message': 'Incorrect content type', 'status_code': 400, 'data': ''})
        
        return JSONResponse(content={'message': 'Data updated', 'status_code': 200, 'data': ''})

    except Exception as e:
        print(e)
        return JSONResponse(content={'message': 'Error in updating the details', 'status_code': 500, 'data': ''})


# generate resume API under development
@app.post('/generateResume/{template}')
async def generateResume(template : int, data : dict, session : AsyncSession=Depends(get_async_session)):
    try:
      print('received request')
      user_id = data['user_id']
      project_stmt = text('select projects.title, projects.description, projects.techStack from users join projects where users.userId = :user_id')
      experience_stmt = text('select experience.title, experience.employer, experience.duration, experience.description from users join experience where users.userId=:user_id')
      skills_stmt = text('select skills.languages, skills.frameworks, skills.certifications, skills.courses from skills join users where users.userId = :user_id')
      user_stmt = text('select firstName, lastName, email, linkedinLink, githubLink from profiles where userId = :user_id')
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

      print('USER PROJECTS IN DB\n\n', projectData)
      print('USER EXPERIENCE IN DB\n\n', experienceData)
      print('USER SKILLS IN DB\n\n', skillsData)

      result = agent.invoke({'job_description' : data['job_description'], 'userProjects' : projectData, 'userExperience' : experienceData, 'userSkills' : skillsData})
      print(f"\n FINAL RESUME CONTENT \n\n{result['resume']}")


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
      template_file = f'./utils/templates/latex_template_{template}.txt'
      print('TEMPLATE FILE : ', template_file)
      with open(template_file, 'r') as f:
          latex_code = f.read()
      # Generating the LaTeX code. 
      latex = await generateLatexCode(resume=resumeData, latex_code=latex_code) 
      CMD = "pdflatex -interaction=nonstopmode resume.tex"

      with open('resume.tex', 'w') as f:
          f.write(latex['Data'])
      if os.path.exists('resume.tex'):
          process = subprocess.run(CMD, shell=True, capture_output=True, text=True)
          # print('ERROR: \t', process.stderr, end='\n\n')
          print('OUTPUT: \n', process.stdout, end='\n\n')
      if os.path.exists('resume.pdf'):
        return FileResponse(path='./resume.pdf', media_type = 'application/pdf', status_code=200)
      
    except HTTPException as e:  
      return Response(status_code = 500, content=str(e))


