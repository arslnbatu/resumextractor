import flask
import os
import json
from datetime import datetime
from pytz import timezone
from werkzeug.utils import secure_filename
from server import *
from flask import request, jsonify, render_template, redirect, url_for
import xlsxwriter
from flask import send_file

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('api', filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)))

    return render_template('index.html')


@app.route('/result', methods=['GET'])
def api():
    filepath = request.args.get('filepath')
    if not filepath:
        return render_template('result.html', message='No file selected.')

    # Process the selected file
    jsons = []
    text = extract_text_from_pdf(filepath)
    text = text.lower()
    text = "* " + text + " *"
    translationTable = str.maketrans("ğĞıİöÖüÜşŞçÇ", "gGiIoOuUsScC")
    text = text.translate(translationTable)

    # Extract information
    created = str(datetime.now(timezone))
    phone_number = extract_phone_number(text)
    email = extract_emails(text)
    website = extract_website(text)
    education = extract_education2(text)
    skills = extract_skills(text)
    occupation = extract_occupation(text)
    lang = extract_lang(text)

    # Create JSON for the selected PDF file
    jsons.append({
        'filepath': filepath,
        'created': created,
        'phone_number': phone_number,
        'email': email,
        'website': website,
        'work_experience1': occupation,
        'education': education,
        'skills': skills,
        'languages': lang
    })

    data_results = json.dumps(jsons, indent=4)
    if len(data_results) == 0:
        return render_template('result.html', message='No results found.')
    else:
        data_results = json.loads(data_results)
        return render_template('result.html', data_results=data_results)



@app.route('/download', methods=['GET','POST'])
def api2():

    # Iterate through all file
    filepath = request.args.get('filepath')
    if not filepath:
        return render_template('result.html', message='No file selected.')

    # Process the selected file
    jsons = []
    text = extract_text_from_pdf(filepath)
    text = text.lower()
    text = "* " + text + " *"
    translationTable = str.maketrans("ğĞıİöÖüÜşŞçÇ", "gGiIoOuUsScC")
    text = text.translate(translationTable)

    # Extract information
    created = str(datetime.now(timezone))
    phone_number = extract_phone_number(text)
    email = extract_emails(text)
    website = extract_website(text)
    education = extract_education2(text)
    skills = extract_skills(text)
    occupation = extract_occupation(text)
    lang = extract_lang(text)

    # Create JSON for the selected PDF file
    jsons.append({
        'filepath': filepath,
        'created': created,
        'phone_number': phone_number,
        'email': email,
        'website': website,
        'work_experience1': occupation,
        'education': education,
        'skills': skills,
        'languages': lang
    })
    data_results = json.dumps(jsons, indent=4)
    with open('data.json',"w") as f:
        json.dump(jsons, f)

    with open('data.json') as f:
        data_results = json.load(f)
    workbook = xlsxwriter.Workbook('data2.xlsx')
    worksheet = workbook.add_worksheet()

    # Writing headers
    worksheet.write(0, 0, 'Filepath')
    worksheet.write(0, 1, 'Created')
    worksheet.write(0, 2, 'Phone Number')
    worksheet.write(0, 3, 'Email')
    worksheet.write(0, 4, 'Website')
    worksheet.write(0, 5, 'Work Experience')
    worksheet.write(0, 6, 'Education')
    worksheet.write(0, 7, 'Skills')
    worksheet.write(0, 8, 'Languages')

    row = 1
    for d in data_results:
        worksheet.write(row, 0, d['filepath'])
        worksheet.write(row, 1, d['created'])
        worksheet.write(row, 2, d['phone_number'])
        worksheet.write(row, 3, d['email'])
        if d['website']:
            website = ', '.join(d['website'])
            worksheet.write(row, 4, website)

        if d['work_experience1']:
            work_experience1 = ', '.join(d['work_experience1'])
            worksheet.write(row, 5, work_experience1)
        try:
            if d['education']:
                education = ', '.join(d['education'])
                worksheet.write(row, 6, education)
        except TypeError as e:
            print(f"Error writing education to row {row}: {e}")

        # if d['work_ai']:
        #     work = d['work_ai']['work_experience']
        #     for i in range(len(work)):
        #         if i < 5:
        #             worksheet.write(row, i + 5, work[i]['company_name'] + ', ' + work[i]['position'] + ', ' + work[i]['WorkingYears'])
        #
        # if d['education_ai']:
        #     edu = d['education_ai']['education']
        #     for i in range(len(edu)):
        #         if i < 5:
        #             worksheet.write(row, i + 8, edu[i]['school_name'])

        if d['skills']:
            skills = ', '.join(d['skills'])
            worksheet.write(row, 7, skills)

        if d['languages']:
            languages = ', '.join(d['languages'])
            worksheet.write(row, 8, languages)

        row += 1

    workbook.close()
    return send_file('data2.xlsx', as_attachment=True)

@app.route('/redirect-after-download')
def redirect_after_download():
    return redirect('/index')

if __name__ == '__main__':
    app.run()
