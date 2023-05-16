import openai
from PyPDF2 import PdfReader


def experience_work(text):

    # Set up OpenAI API credentials
    openai.api_key = "*****"
    prompt2 = (f"""Tabular Data Extraction Please generate only three work experience information in json format for a employee. Include the employee's previous "work_experience": company_name, position and WorkingYears. the output JSON should have the following format: {{"work_experience": [{{"company_name": "","position": "","WorkingYears": ""}},{{"company_name": "","position": "","WorkingYears": ""}},{{"company_name": "","position": "","WorkingYears": ""}}]}}. {text} """)
    # Prompt for extracting work experience

    # Use OpenAI's GPT-3 to generate the work experience section
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt2,
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Extract the generated work experience section from the OpenAI response
    work_experience = response.choices[0].text.strip()
    return work_experience

    # Print the extracted work experience, education, and skill


