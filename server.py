import os
from datetime import datetime
import json
import re
from itertools import chain
import numpy as np
import pandas as pd
import pytz
import spacy
from PyPDF2 import PdfReader
import experience
import degree
import openpyxl
from unidecode import unidecode
import cv2 #opencv-python
import xlsxwriter
from itertools import zip_longest

# Load spacy pre-trained model
nlp = spacy.load('en_core_web_sm')

# Regex / Reference List
UNIVERSITIES_REF = 'davinci\\reference\\world-universities.csv'
MAJOR_REF = 'davinci\\reference\\majors-list.csv'
SKILL_REF = 'davinci\\reference\\skills.csv'
DEGREE_REF = ['s3', 'doctoral', 'doktor', 's2', 'master', 'magister', 's1', 'bachelor', 'sarjana', 'vokasi', 'lisans', 'yuksek lisans']
LANG_REF = 'davinci\\reference\\lang-list.csv'
OCCUPATION_REF = 'davinci\\reference\\occupation.csv'
BIRTHPLACE_REF = 'davinci\\reference\\birthplace.csv'
PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
WEB_REG = re.compile(r'\b(?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})(?:/[\w\.-]*)*/?)')


# Function
def extract_text_from_pdf(pdf_path):

    with open(pdf_path, 'rb') as file:
        # Load the PDF file using PdfReader
        pdf = PdfReader(file)
        # Loop through each page and extract the text
        text = ''
        for page in pdf.pages:
            # Check if the page has a "Text" attribute
            if 'Text' in page.keys():
                text += page.Text
            else:
                # If the page does not have a "Text" attribute, try extracting the text using the "extract_text" method
                text += page.extract_text()
        # Return the extracted text
        return text



def extract_phone_number(text):
    text = text.replace(' ', '')
    phone = set(re.findall(PHONE_REG, text))
    if phone:
        for number in phone:
            if len(number) >= 10 and len(number) < 16 and '.' not in number:
                return number


def extract_emails(text):
    email = re.findall(EMAIL_REG, text)
    if email:
        mail = email
        return mail[0]


def extract_website(text):
    text = text = re.sub(r'[()]', '', text)
    temp = re.findall(WEB_REG, text)
    temp = list(set(temp))
    web = []
    if temp:
        for w in temp:
            if '/' in w:
                web.append(w)
        if web:
            return web


def extract_college(text):
    file = UNIVERSITIES_REF
    df = pd.read_csv(file, header=None)
    universities = [i.lower() for i in df[1]]
    college_name = []

    for i in range(len(text)):
        for univ in universities:
            if univ in text[i]:
                if univ not in college_name:
                    college_name.append(univ)

    if len(college_name) == 0:
        for i in range(len(text)):
            if text[i].startswith('university'):
                if text[i] not in college_name:
                    college_name.append(text[i].strip())

    if college_name:
        return college_name


def extract_major(text, univ):
    file = MAJOR_REF
    df = pd.read_csv(file)
    major_specific = [x for x in df['SPECIFIC'].str.lower().values if x is not np.nan]
    major_general = [x for x in df['GENERAL'].str.lower().values if x is not np.nan]
    major = set([])
    for i in range(len(text)):
        if univ in text[i]:
            try:
                out = text[i - 2] + ' ' + text[i - 1] + ' ' + text[i] + ' ' + text[i + 1] + ' ' + text[i + 2]
            except:
                out = text[i - 2] + ' ' + text[i - 1] + ' ' + text[i]
            for row in major_specific:
                if row in out:
                    major.add(row)
            if len(major) == 0:
                for row in major_general:
                    if row in out:
                        major.add(row)
            if major:
                return ' '.join(major)


def extract_degree(text, univ):
    for i in range(len(text)):
        if univ in text[i]:
            try:
                out = text[i - 2] + ' ' + text[i - 1] + ' ' + text[i] + ' ' + text[i + 1] + ' ' + text[i + 2]
            except:
                out = text[i - 2] + ' ' + text[i - 1] + ' ' + text[i]
            for degree in DEGREE_REF:
                if degree in out:
                    return degree


def extract_education2(text):
    filter = ['develop', 'create', 'make', 'collaborate', 'education']
    text = [s for s in text.split('\n') if not any(x in s for x in filter)]

    uni = extract_college(text)
    edu = []
    deg = []

    for degree in DEGREE_REF:
        for i in range(len(text)):
            if text[i].startswith(degree):
                deg.append(degree)

    if uni:
        if len(uni) == 1 and len(deg) > 1:
            for i in range(len(deg)):
                dct = {}
                dct['college'] = uni[0]
                dct['major'] = extract_major(text, deg[i])
                dct['degree'] = extract_degree(text, uni[0])
                edu.append(dct)
            if len(edu) == 3:
                edu[1]['degree'] = 'master'
                edu[2]['degree'] = 'bachelor'
            elif len(edu) == 2:
                edu[1]['degree'] = 'bachelor'
        else:
            for item in uni:
                dct = {}
                dct['college'] = item
                dct['major'] = extract_major(text, item)
                dct['degree'] = extract_degree(text, item)
                edu.append(dct)
        return edu


def extract_skills(text):
    nlp_text = nlp(text)
    noun_chunks = nlp_text.noun_chunks
    tokens = [token.text for token in nlp_text if not token.is_stop]
    df = pd.read_csv(SKILL_REF, header=None)
    skills = df[0].values
    skillset = []

    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)

    skillset = list(set(skillset))
    return sorted(skillset)



def extract_occupation(text):
    filter = ['regression', 'degree', 'major', 'improve', 'sometimes', 'create', 'creating', ' to ', 'progress', 'education', 'pinball', '']
    text = [x.encode("ascii", "ignore").decode() for x in text.split('\n') if not any(s in x for s in filter)]
    df = pd.read_csv(OCCUPATION_REF)
    joblist_specific = [x for x in df['specific'].str.lower().values if x is not np.nan]
    joblist_general = [x for x in df['general'].str.lower().values if x is not np.nan]
    occupation = set([])

    for i in range(len(text)):
        temp = re.sub(r'[^\w\s]', '', text[i]).strip()
        temp = re.sub(r' +', ' ', temp)
        for job in joblist_specific:
            if job in temp and len(temp.split()) < 5:
                occupation.add(temp)
        for job in joblist_general:
            if job in temp and len(temp.split()) < 5:
                occupation.add(temp)

    if occupation:
        return list(occupation)


def extract_lang(text):
    lang_text = nlp(text)
    noun_chunks = lang_text.noun_chunks
    lanf = [token.text for token in lang_text if not token.is_stop]
    df = pd.read_csv(LANG_REF, header=None)
    langu = df[0].values
    languages = []

    for token in lanf:
        if token.lower() in langu:
            languages.append(token)

    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in langu:
            languages.append(token)

    languages = list(set(languages))
    return sorted(languages)











