import os
import smtplib
import sys
import speech_recognition as sr
from flask import Flask, render_template, url_for, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#reference this
application = app = Flask(__name__)
#sqlite relative path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#initialize db
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # content is task name
    content = db.Column(db.String(200), nullable=False) #no blank task
    # completed task
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default= datetime.utcnow) #mark timestamp created
    # dategoal
    def __repr__(self):
        return '<Task %r>' % self.id

# CONNECT GMAIL
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login('cloudcomputingontechu@gmail.com', 'Cloud12345')


# VOICE Function
@app.route('/voice/')
def voice():
    r = sr. Recognizer()
    mic = sr.Microphone()
    
    
    with mic as source:
        print("Speak...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            # Print text
            print(f"TASK NAME SENT '{text}'")
            
        except sr.UnknownValueError:
            # No voice
            print("Didnt hear that try again")
    return text


@app.route('/', methods=['POST','GET']) # add POST & GET to add functionality
# define function for route
def index():
    if request.method == 'POST':
        # POST a task from input
        task_content = request.form['content']
        # todo object
        new_task = Todo(content=task_content)
        # Email
        email = request.form['emailaddress'].strip()


        # If input text box is blank use voice command
        if not task_content:
            #voice() #return voice()
            # Import and call voice function
            text = voice()
            text_content=text
            
            # TEMP TEXT INPUT IN REPLACEMENT OF VOICE
            #text_content=input("What's your task?")
            new_text_task = Todo(content=text_content)

            if email:
                server.sendmail('cloudcomputingontechu@gmail.com', email, text_content)
        try:
           db.session.add(new_text_task)
           db.session.commit()
           return redirect('/')
        except:
           return 'Error adding a new task'


        #IF WITHOUT VOICE

        #if email:
            #server.sendmail('cloudcomputingontechu@gmail.com', email, task_content)

        # Push new task to db
        #try:
           # db.session.add(new_task)
           # db.session.commit()
           # return redirect('/')
        #except:
            #return 'Error adding a new task'
    
    else:
        tasks = Todo.query.order_by(Todo.date_created).all() #look at db contents in order they were created then grab all
        return render_template('index.html', tasks=tasks)

# Delete Task using ID
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error deleting this task'

# Update method
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')

        except:
            return 'Error updating this task'

    else:
        return render_template('update.html', task= task)


# Complete Method
@app.route('/complete/<int:id>')
def complete(id):
    task = Todo.query.get_or_404(id)

    #return this
    result = ''
    for c in (task.content):
        result = result + c + '\u0336'
        
    return result

# Strikethrough method
def strike(text):
    result = ''
    for c in text:
        result = result + c + '\u0336'
    return result

# Check if app is working or not
if __name__ == "__main__":
    #will show errors on the webpage
    app.run(debug=True)



