from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from models import llm_output_models

# MODEL INITIALIZATION
# model_v1 = ChatGroq(model='llama3-8b-8192', api_key='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', temperature=0.1)
model_v2 = ChatGroq(model='llama-3.1-8b-instant', api_key='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', temperature=0)
model_v3 = ChatGroq(model='llama-3.3-70b-versatile', api_key='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', temperature=0.1)


# Node Prompts

instruction_generator_prompt = PromptTemplate(
    template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a Hiring Manager at a prestigious multinational corporation (MNC) such as Google or Microsoft. Your goal is to evaluate candidates for job or internship openings and provide guidance on how they can effectively present their qualifications.

    Your task involves analyzing the candidate's projects and experiences in relation to a specific job description. You need to shortlist relevant projects and experiences that align best with the job role, ensuring that at least two projects and two experiences are selected.

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Follow these instructions carefully:
    1. Review the job description and identify key skills and qualifications that are essential for the role.
    2. Shortlist a minimum of two projects (preferrably 3) and two experiences from the candidate's background that directly relate to the job requirements.
    3. For each selected project and experience, provide a brief suggestion (maximum one point long) on how the candidate should highlight specific aspects of their work to demonstrate relevance.
    4. Give the output in a readable format which would be easier to interpret. 

    Here is the required information:
    Projects: \n {projects} \n
    Experience: \n {experience} \n
    Job Details: \n {job_details} \n

    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables = ["job_details", 'projects', 'experience'], 
)
instructor_generator = instruction_generator_prompt | model_v3 | StrOutputParser()

project_generator_prompt = PromptTemplate(
    template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a university student with exceptional grades in language and grammar. 
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    You will receive the projects section of a resume along with suggestions indicating which projects should be kept and which should be removed. 
    Your task is to follow these suggestions and rewrite the projects section of the resume, only including the shortlisted projects.
    Please ignore any suggestions related to the experience section and focus solely on the project section.

    Suggestions: \n {instructions} \n
    Projects List: \n {projects} \n

    Please adhere strictly to the following output format:
    1. **Project Name 1**
       - Description point 1
       - Description point 2
    2. **Project Name 2**
       - Description point 1
       - Description point 2
    ... and so on for each shortlisted project.
    
    Ensure that you do not add any additional content, and do not quantify or modify any details that are not present in the original data.
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables = ['projects', 'instructions']
    )

project_generator = project_generator_prompt | model_v2 | StrOutputParser()

experience_generator_prompt = PromptTemplate(
    template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a university student with exceptional grades in language and grammar.

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    You will receive the experience section of a resume along with suggestions indicating which experiences should be kept and which should be removed. 
    Your task is to follow these suggestions strictly and rewrite the experience section of the resume, only including the shortlisted experiences.
    Please ignore any suggestions related to the projects section and focus solely on the experience section.

    Suggestions: \n {instructions} \n
    Experience List: \n {experience} \n

    Please adhere strictly to the following output format:
    1. **Firm/Internship Name - Role - Duration**
       - Description point 1
       - Description point 2
    2. **Firm/Internship Name - Role - Duration**
       - Description point 1
       - Description point 2
    ... and so on for each shortlisted experience.

    Ensure that you do not add any additional content, and do not quantify or modify any details that are not present in the original data.
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """, 
  input_variables = ['experience', 'instructions']
)
experience_generator = experience_generator_prompt | model_v2 | StrOutputParser()


reviewParser = JsonOutputParser(pydantic_object= llm_output_models.Review)
reviewer_prompt = PromptTemplate(
    template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a Hiring Manager at a large corporation. You have been given the "Projects" and "Experience" sections of a candidate's resume, along with the job description for the position they are applying for. 
    Your task is to critically evaluate each of these sections based on the following four criteria: Impact, Brevity, and Style.
    1. Impact: Assess the effectiveness of the content in terms of the quantifiable impact of the candidate's contributions, the variety of action verbs used, the presence of any weak or repetitive verbs, and any spelling or grammatical errors.
    2. Brevity: Evaluate how concise and to-the-point the content is. Consider the overall length of the resume, the use of bullet points, and the length of each bullet point. Determine whether the content could be made more succinct without losing essential details.
    3. Style: Analyze the writing style for clarity, professionalism, and alignment with industry standards. Look for consistency in formatting, use of active voice, and how well the candidate's achievements are highlighted.

    Frame the suggestions so that they can be given as input to an LLM for refining the resume. 
    Make sure not to suggest the candidate to add non-factual data.

    Here are the required information. FOLLOW THE OUTPUT FORMAT INSTRUCTIONS NO MATTER WHAT.
    Resume Draft: \n {resume} \n
    Job Description: \n {job_details} \n

    OUTPUT FORMAT --- \n
    
    Overall Score: [score out of 100]
    Impact:
    - Score: [score out of 100]
    - Suggestions: [detailed suggestions for improvement]
    Brevity:
    - Score: [score out of 100]
    - Suggestions: [detailed suggestions for improvement]
    Style:
    - Score: [score out of 100]
    - Suggestions: [detailed suggestions for improvement]

    DON'T USE the * symbol around the headings of the output.
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    """,
    input_variables = ['resume', 'job_details'], 
)
review_generator = reviewer_prompt | model_v3 | StrOutputParser()

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
