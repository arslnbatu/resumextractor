import openai
from PyPDF2 import PdfReader


def education_history(text):

    # Set up OpenAI API credentials
    openai.api_key = "****"
    prompt2 = (f"""Tabular Data Extraction Please generate only education information in json format for a employee. Include the employee's last 3 education school_name, majors, degree, start date and end date.the output JSON should have the following format:{{"education": [{{"school_name": "","majors": "","degree": "","start_date": "","end_date": ""}},{{"school_name": "","majors": "","degree": "","start_date": "","end_date": ""}},{{"school_name": "","majors": "","degree": "","start_date": "","end_date": ""}}]}}. {text}  """)
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
    work = response.choices[0].text.strip()
    return work

    # Print the extracted work experience, education, and skill


