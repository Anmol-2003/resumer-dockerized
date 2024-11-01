from pydantic import BaseModel, Field
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
    title: str = Field(description='Title of the project')
    suggestions: str = Field(description='Suggestions to instruct the candidate to focus on which part of the project and to properly describe and highlight different parts of the project')
class Experience(BaseModel):
    title: str = Field(description='Title of the experience')
    suggestions: str = Field(description='Suggestions to instruct the candidate for properly describing the experience')
class Instruction(BaseModel):
    projects: List[Project]
    experience : List[Experience]