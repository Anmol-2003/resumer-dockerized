import subprocess
import os
CMD = "pdflatex -interaction=nonstopmode resume.tex"

async def generatePDF(code : str):
    with open('resume.tex', 'w') as f:
        f.write(code)
    if os.path.exists('resume.tex'):
        process = subprocess.run(CMD, shell=True, capture_output=True, text=True)
