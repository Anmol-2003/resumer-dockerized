from pydantic import BaseModel

class BufferResponse(BaseModel):
    message : str
    status_code : int

class Response(BaseModel):
    message : str
    status_code : int 
    data : str

class ErrorResponse(BaseModel):
    message : str
    status_code : int

class Success(BaseModel):
    message : str
    status_code : int = 200

class User(BaseModel):
    firstName : str
    lastName : str
    email : str
    linkedinLink : str
    githubLink : str

class Projects(BaseModel):
    userId : int
    title: str
    description : str
    techStack : str


class Experience(BaseModel):
    userId : int 
    title : str
    employer : str
    duration : str
    description : str

class Skills(BaseModel):
    userId : int 
    languages : str
    frameworks : str
    certifications : str
    courses : str

class Education(BaseModel):
    userId : int 
    institution : str
    grade : float 
    duration : str
    location : str

class SignUp(BaseModel):
    name: str
    email : str
    password : str

class Login(BaseModel):
    email : str
    password : str