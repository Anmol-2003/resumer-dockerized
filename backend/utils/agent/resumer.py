from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from .generators import *
import json
import google.generativeai as genai
import os 
from dotenv import load_dotenv
load_dotenv()

os.environ['gemini_api'] = os.getenv('gemini_api')
genai.configure(api_key=os.environ['gemini_api'])

class AgentState(TypedDict):
    job_description : str
    instructions: str
    iterations : int
    userProjects: str
    userExperience : str 
    userSkills : str
    resume : str
    review : str

def instructionGenerator(state : AgentState):
    job_description = state['job_description']
    instructions = instructor_generator.invoke({'job_details' : job_description, 'projects' : state['userProjects'], 'experience' : state['userExperience']})
    print('INSTRUTIONS GENERATED\n', instructions)
    return {'instructions' : instructions, 'iterations' : 0}

# can remove this node and directly use the raw user entered data into the reflection loop 
def resumeGenerator(state: AgentState):
    try:
        projects = project_generator.invoke({'projects' : state['userProjects'], 'instructions' : state['instructions']})
        experience = experience_generator.invoke({'experience': state['userExperience'], 'instructions' : state['instructions']})
        
        print('RESUME DRAFT GENERATED')
        resume = 'PROJECTS\n' + projects + '\n\nEXPERIENCE\n' + experience 
        return {'resume' : resume}
    except Exception as e: 
        print("Exception occured while generating the resume content", e)
        return
    
def reviewer(state: AgentState):
    review = review_generator.invoke({'resume' : state['resume'], 'job_details' : state['job_description']})
    print('REVIEW GENERATED')
    return {'review' : review}

# re evaluating the revised resume using self-reflection loops
def reevaluation(state: AgentState):
    originalData = f"{state['userProjects']} \n {state['userExperience']}"
    resume = reevaluator.invoke({'originalData' : originalData, 'resume' : state['resume'], 'review' : json.dumps(state['review'], indent=2)})
    print('RESUME DRAFT RE-EVALUATED')
    return {'resume' : resume, 'iterations' : state['iterations'] + 1}

def reflect(state: AgentState):
    review = state['review']
    print('\n\n REVIEW \n\n', review)
    threshold = 85

    review_lines = review.splitlines()
    print(review_lines)
    overall_score_line = next(line for line in review_lines if line.startswith("Overall Score:"))
    overall_score = int(overall_score_line.split(":")[1].strip())

    if state['iterations'] > 3:
        return END
    if overall_score >= threshold:
        return END
    return 'reevaluateResume'


graph = StateGraph(AgentState)
graph.add_node('generate_instructions', instructionGenerator)
graph.add_node('generateResume', resumeGenerator)
graph.add_node('generateReview', reviewer)
graph.add_node('reevaluateResume', reevaluation)
# graph.add_node('generatelatex', generateLatex)

graph.set_entry_point('generate_instructions')
graph.add_edge('generate_instructions', 'generateResume')
graph.add_edge('generateResume', 'generateReview')
graph.add_edge('reevaluateResume', 'generateReview')
graph.add_conditional_edges('generateReview', reflect)


model = genai.GenerativeModel('gemini-1.5-pro', 
                                system_instruction= r"""
                                You are a professional LaTeX code developer. You will be provided with two inputs:
                                A Draft of a Resume: This contains the actual information about a candidate, such as their education, experience, projects, skills, etc.
                                A LaTeX Code Template: This template contains placeholders or synthetic information.

                                Your Task:
                                Fill in the LaTeX Template: Correctly insert the given data from the resume draft into the LaTeX code. Ensure that all provided information is accurately reflected in the final LaTeX code.
                                
                                INSTRUCTIONS:
                                Add a backslash '\' before every percentage '%' symbol if used any for representing data. Example : "Developed a model with cross validation accuracy of 96\%"
                                Fix Any Errors: If there are any errors in the LaTeX code, such as missing arguments, incorrect formatting, or redundant commands, you must fix them.
                                Do not change the latex code, you just have to rewrite it but with different data.

                                Match Data with Placeholders:
                                If the placeholders in the template do not match the given data (e.g., placeholders for "Courses" but you are given "Certifications"), update the placeholders to reflect the actual data provided.
                                If there are more sections or details in the resume draft than placeholders in the template, add the necessary placeholders and format them correctly.
                                Do Not Add Additional Content: Do not introduce any new information or content that is not provided in the resume draft. Stick strictly to the information given.

                                Preserve Consistency: Ensure that the formatting is consistent throughout the document, such as section headings, bullet points, and alignment.
                                Follow the syntax of the given template properly with proper indentations.

                                Maintain Professional Quality: The final LaTeX code should be clean, professional, and ready for immediate use without further modifications.
                                Example:
                                If the resume draft provides details for "Certifications" but the template has a placeholder for "Courses," update the LaTeX code to use "Certifications" instead.
                                If the "Projects" section in the resume draft contains two projects but the template has placeholders for only one, add another project placeholder and format it accordingly.
                                Ensure the LaTeX code is fully functional, error-free, and accurately represents the provided resume information.
                                """)

async def generateLatexCode(resume : str, latex_code : str):
    # output = latex_node.invoke({'resume' : resume, 'latex_code' : latex_code})
    output = model.generate_content(f"Resume Data: {resume} \n\n Latex Code: {latex_code}")
    return {'Data' : output.text}    

agent = graph.compile()
