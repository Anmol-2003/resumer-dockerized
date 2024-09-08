from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from models import llm_output_models

# MODEL INITIALIZATION
model_v1 = ChatGroq(model='llama3-8b-8192', api_key='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', temperature=0.1)
model_v2 = ChatGroq(model='llama-3.1-8b-instant', api_key='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', temperature=0.1)


# Node Prompts

instruction_parser = JsonOutputParser(pydantic_object=llm_output_models.Instruction)
instruction_generator_prompt = PromptTemplate(
    template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a Hiring Manager at a reputed MNC and are looking for exceptional resumes for the job.
    You will be details of a job/internship opening along with candidate's projects and experiences.

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Your have to follow the following instructions:
    1. Shortlist what projects, experience and skills would be relevant for the given job description. Pick carefully. 
    2. for each project and experience, give suggestions of at most 1 point focusing on instructing the candidate to stress on what part of the project or experience.
    3. You have to shortlist a minimum of 2 projects and 2 experience.

    Here is the required information.
    Projects : \n {projects} \n
    Experience : \n {experience} \n
    Job Details : \n {job_details} \n
    Output instructions : \n {format_instructions} \n

    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
      """,
    input_variables = ["job_details", 'projects', 'experience'], 
    partial_variables = {'format_instructions' : instruction_parser.get_format_instructions()}
)
instructor_generator = instruction_generator_prompt | model_v2 | instruction_parser

project_generator_prompt = PromptTemplate(
    template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a university student with exceptional grades in language and grammar. \
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    You will be given projects section of the resume and some suggestions which have the names of the shortlisted projects that have to kept and rest to be removed. 
    Follow the suggestions and rewrite the project section of the resume only keeping the shortlisted ones.
    The input will be in json serialized format. 

    suggestions : \n {instructions} \n
    Projects List : \n {projects} \n

    Output should be in the following format :
    1. Name of project 1
      - description 1
      - description 2
    2. Name of project 2
      and so on...
    Don't add anything of your own to the output, and also don't add wuantifying data which is not provided in the original data provided.
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables = ['projects', 'instructions']
    )

project_generator = project_generator_prompt | model_v1 | StrOutputParser()
experience_generator_prompt = PromptTemplate(
    template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a university student with exceptional grades in language and grammar. \

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    You will be given experience section of the resume and some suggestions which have the names of the shortlisted experiences that have to kept and rest to be removed. 
    Follow the suggestions and rewrite the experience section of the resume only keeping the shortlisted ones.
    The input will be in json serialized format. 

    Output should be in points describing the work experience.
    Suggestions : \n {instructions} \n
    Experience List : \n {experience} \n

    Output should be in the following format :
    1. Firm/Internship name - Role - Duration
      - description 1
      - description 2
    2. Firm/Internship name - Role - Duration
      and so on...
    Don't add anything of your own to the output, and also don't add quantifying data which is not provided in the original data provided.
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """, input_variables = ['experience', 'instructions']
)
experience_generator = experience_generator_prompt | model_v1 | StrOutputParser()


reviewParser = JsonOutputParser(pydantic_object= llm_output_models.Review)
reviewer_prompt = PromptTemplate(
    template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a Hiring Manager at a major corporation. You have been given the "Projects" and "Experience" sections of a candidate's resume, along with the job description for the position they are applying for. \
    Your task is to critically evaluate each of these sections based on the following four criteria: Impact, Brevity and Style.

    Impact: Assess the effectiveness of the content in terms of the quantifiable impact of the candidate's contributions, the variety of action verbs used, the presence of any weak or repetitive verbs, and any spelling or grammatical errors.
    Brevity: Evaluate how concise and to-the-point the content is. Consider the overall length of the resume, the use of bullet points, and the length of each bullet point. Determine whether the content could be made more succinct without losing essential details.
    Style: Analyze the writing style for clarity, professionalism, and alignment with industry standards. Look for consistency in formatting, use of active voice, and how well the candidate's achievements are highlighted.

    Frame the suggestions so that it can be given as input to an llm for refining the resume. \
    The overall score will be the average of the score given to resume on individual aspects, that is impact, brevity and style. Scoring should be out of 100.
    MAKE SURE NOT TO SUGGEST THE CANDIDATE TO ADD NON-FACTUAL DATA. 
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Here are the required information. FOLLOW THE OUTPUT FORMAT INSTRUCTIONS NO MATTER WHAT.
    Resume Draft: \n {resume} \n\n
    Job Description: \n {job_details} \n\n
    Output format instructions: \n{format_instructions} \n
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables = ['resume', 'job_details'], 
    partial_variables={'format_instructions' : reviewParser.get_format_instructions()}
)
review_generator = reviewer_prompt | model_v2 | reviewParser

reeval_prompt = PromptTemplate(
    template="""
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a university student applying for jobs online. Given a review of your resume from one of the best ATS reviewer, \
    you have to follow the suggestions on 3 different aspects of your resume which are:
    1.Impact: Assess the effectiveness of the content in terms of the quantifiable impact of the candidate's contributions, the variety of action verbs used, the presence of any weak or repetitive verbs, and any spelling or grammatical errors.
    2.Brevity: Evaluate how concise and to-the-point the content is. Consider the overall length of the resume, the use of bullet points, and the length of each bullet point. Determine whether the content could be made more succinct without losing essential details.
    3.Style: Analyze the writing style for clarity, professionalism, and alignment with industry standards. Look for consistency in formatting, use of active voice, and how well the candidate's achievements are highlighted.
    
    Your task is to follow the suggestions carefully and improve the resume content such that it improves the previous overall score and not worsen it.
    You will also be given the original content of projects and experience sections for your reference. Make sure not to add anything on your own which doesn't exist in the reference material.
    The review will be in the form of a json serialized string.
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Here are the required information. 
    Revise and improve the resume based on the ATS suggestions and also taking reference from the original content. 
    Original Content: \n {originalData} \n\n
    Resume: \n {resume} \n\n
    Review: \n {review} \n\n
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """, 
    input_variables=['originalData', 'resume', 'review']
)

reevaluator = reeval_prompt | model_v2 | StrOutputParser()
