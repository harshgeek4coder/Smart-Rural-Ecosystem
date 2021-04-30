from flask import render_template , flash , redirect , url_for , request
import csv
import pandas as pd
from app import app
from app.forms import RegForm , LoginForm
from app.models import User
from app import app, db, pwd
from flask_login import login_user , current_user , logout_user , login_required

from app.tweet_Scraper import Import_tweet_sentiment
from app.jobs_scraper import find_jobs_from,clean_job_titles
from app.crop_forecast_profile import crop_profile,TopFiveLosers,TopFiveWinners

from app.crop_prod import get_estimate_yield
from app import disease_prediction
from app.disease_prediction import predict_disease
from app.symptoms import get_precautions,get_description

tw_obj=Import_tweet_sentiment()
desired_chars=['titles','companies','links','date_listed']

data_sever='app/static/Medical/Symptom_severity.csv'
data_precaution='app/static/Medical/symptom_precaution.csv'
data_desc='app/static/Medical/symptom_Description.csv'


df_prec=pd.read_csv(data_precaution)
df_prec.columns=['Disease','Precaution1','Precaution2','Precaution3','Precaution4']

descr=pd.read_csv(data_desc)
descr.columns=['Disease','Description']


with open('app/static/medical_Testing.csv', newline='') as f:
        reader = csv.reader(f)
        symptoms = next(reader)
        symptoms = symptoms[:len(symptoms)-1]



@app.route('/')
def homepage():
    return render_template("information.html" , )

@app.route("/signup" , methods = ['GET' , 'POST'])
def signuppage() :
    if current_user.is_authenticated :
        flash("You are already logged in." , "warning")
        return redirect(url_for("homepage"))
    form = RegForm(request.form)
    if request.method == "POST" and form.validate():
        hashed = pwd.generate_password_hash(form.password.data).decode('utf-8')
        element = User(uname = form.uname.data , email = form.email.data , password = hashed)
        db.session.add(element)
        db.session.commit()
        flash("Account created for %s!" % (form.uname.data) , "success")
        return redirect(url_for("loginpage"))
    return render_template("signup.html" , form = form)

@app.route("/login" , methods = ['GET' , 'POST'])
def loginpage():
    if current_user.is_authenticated :
        flash("You are already logged in." , "warning")
        return redirect(url_for("homepage"))
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        member = User.query.filter_by(uname = form.uname.data).first()
        if member and pwd.check_password_hash(member.password , form.password.data) :
            login_user(member)
            flash("Welcome, %s!" % (form.uname.data) , "success")
            return redirect(url_for("homepage"))
        else :
            flash("Username or Password doesn't match, please try again." , "danger")
            return redirect(url_for("loginpage"))
    return render_template("login.html" , form = form)

@app.route("/tweet_updates" , methods = ['GET' , 'POST'])
def tweet_updates():
    if current_user.is_authenticated :        

        text = request.form.get('text','MoRD_GOI')
        all_tweets=tw_obj.get_hashtag(text)

        return render_template("tweet.html" ,all_tweets=all_tweets,query=text)

    else :
            flash("Username or Password doesn't match, please try again." , "danger")
            return redirect(url_for("loginpage"))
            
    return render_template("tweet.html" ,all_tweets=all_tweets,query=text)

    

@app.route("/jobs_updates" , methods = ['GET' , 'POST'])
def jobs_updates():

    if current_user.is_authenticated :    

        job_title = request.form.get('job_title','intern')
        job_location = request.form.get('job_location','india')

        jobs_list, num_listings=find_jobs_from("Indeed",job_title,job_location,desired_chars)

        words=clean_job_titles(jobs_list['titles'])

        res=zip(words,jobs_list['companies'],jobs_list['links'],jobs_list['date_listed'])
        res=list(res) 

        return render_template("jobs.html" ,res=res,num_listings=num_listings) 

    else :
            flash("Username or Password doesn't match, please try again." , "danger")
            return redirect(url_for("loginpage"))    

    return render_template("jobs.html" ,res=res,num_listings=num_listings)



@app.route("/crop_analysis" , methods = ['GET' , 'POST'])
def crop_analysis():
    if current_user.is_authenticated :

        crop_name = request.form.get('crop_name','arhar')

        crop_context=crop_profile(crop_name)

        topfive=TopFiveWinners()
        bottomfive=TopFiveLosers()

        return render_template("crop_analysis.html", context=crop_context,topfive=topfive,bottomfive=bottomfive)

    else :
            flash("Username or Password doesn't match, please try again." , "danger")
            return redirect(url_for("loginpage")) 
    

    return render_template("crop_analysis.html", context=crop_context,topfive=topfive,bottomfive=bottomfive)





@app.route("/crop_production_estimate" , methods = ['GET' , 'POST'])
def crop_production_estimate():
    if current_user.is_authenticated :

        temp = request.form.get('temp',0)
        area=  request.form.get('area',0)
        topfive=TopFiveWinners()
        bottomfive=TopFiveLosers()

        possible_prod,st=get_estimate_yield(temp,area)



        return render_template("crop_prod_estimate.html", possible_prod=possible_prod,topfive=topfive,bottomfive=bottomfive,st=st)

    else :
            flash("Username or Password doesn't match, please try again." , "danger")
            return redirect(url_for("loginpage")) 
    

    return render_template("crop_prod_estimate.html", possible_prod=possible_prod)





@app.route("/medical_consult" , methods = ['GET' , 'POST'])
def medical_consult():
    if current_user.is_authenticated :
        if request.method == 'POST':
            selected_symptoms = []        
            if(request.form['Symptom1']!="") and (request.form['Symptom1'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom1'])
            if(request.form['Symptom2']!="") and (request.form['Symptom2'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom2'])
            if(request.form['Symptom3']!="") and (request.form['Symptom3'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom3'])
            if(request.form['Symptom4']!="") and (request.form['Symptom4'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom4'])
            if(request.form['Symptom5']!="") and (request.form['Symptom5'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom5'])

            disease = predict_disease(selected_symptoms)
            prec1,prec2,prec3,prec4=get_precautions(disease[0])
            descript=get_description(disease[0])

            return render_template("medical_consult.html",disease=disease[0],symptoms=symptoms , prec1=prec1 , prec2=prec2 , prec3=prec3 ,prec4=prec4 ,descript=descript)
        else:

            return render_template("medical_consult.html",symptoms=symptoms)
            
    else :
            flash("Username or Password doesn't match, please try again." , "danger")
            return redirect(url_for("loginpage")) 
    

    return render_template("medical_consult.html" ,symptoms=symptoms)









@app.route("/logout")
def logoutpage():
    logout_user()
    flash("Successfuly logged out." , "success")
    return redirect(url_for("homepage"))

@app.route("/member-page")
@login_required
def member():
    return render_template("members.html")