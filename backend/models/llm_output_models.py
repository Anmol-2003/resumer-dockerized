from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

## Reviewing model
class Impact(BaseModel):
    score : int = Field(description='Score for this section')
    suggestions : str = Field(description='Suggestions for improving the Impact section')

class Brevity(BaseModel): 
    score : int = Field(description='Score for this section')
    suggestions : str = Field(description='Suggestions for improving the Brevity section')

class Style(BaseModel):
    score : int = Field(description='Score for this section')
    suggestions : str = Field(description='Suggetions to improve style of the content')

class Data(BaseModel):
    impact : Impact
    brevity : Brevity
    style : Style

class Review(BaseModel):
    overall_score: int = Field(description='overall resume score')
    data : Data

## Instruction model

class Project(BaseModel):
    title: str = Field(description='Title of the projec to be included in the resume')
    suggestions: str = Field(description='Suggestions to keep in mind while describing the project in the resume.')
class Experience(BaseModel):
    title: str = Field(description='Title of the role in the experience')
    suggestions: str = Field(description='Suggestions to keep in mind while describing the experience in the resume.')

class Instruction(BaseModel):
    projects: List[Project]
    experience : List[Experience]