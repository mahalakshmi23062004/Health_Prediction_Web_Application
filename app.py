import numpy as np
from flask import Flask,render_template,request,redirect,url_for
import pickle
from flask_mysqldb import MySQL


app = Flask(__name__)

app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="health_prediction"


mysql = MySQL(app)



cal=pickle.load(open('calories.pkl','rb'))
risk=pickle.load(open('health.pkl','rb'))
act=pickle.load(open('activity.pkl','rb'))
temp=pickle.load(open('body_temp.pkl','rb'))

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/calories')
def calories():
    return render_template('calories.html')


@app.route('/predict_calories', methods=['GET', 'POST'])
def predict_calories():
    if request.method == 'POST':
        # Collecting form data
        a = request.form.get('gender')
        b = request.form.get('age')
        c = request.form.get('height')
        d = request.form.get('weight')  
        e = request.form.get('duration') 
        f = request.form.get('heart_rate')
        g = request.form.get('body_temp') 

        # Insert into database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO calories (Gender, Age, Height, Weight, Duration, `Heart rate`, `Body temperature`) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                    (a, b, c, d, e, f, g))
        mysql.connection.commit()
        cur.close()

        # Make prediction
        gender = int(a)
        age = int(b)
        height = float(c)
        weight = float(d)
        duration = float(e)
        heart_rate = float(f)
        body_temp = float(g)

        input_data = [[gender, age, height, weight, duration, heart_rate, body_temp]]
        prediction = cal.predict(input_data)[0]
        result = f"Predicted Calories Burned: {round(prediction, 2)} kcal"

        return render_template('calories.html', result=result)
    
    # If GET request, just show form
    return render_template('calories.html')


@app.route('/activity')
def activity():
    return render_template('activity.html')

@app.route('/predict_activity', methods=['GET','POST'])
def predict_activity():
    if request.method == 'POST':
        h = request.form.get('duration')
        i = request.form.get('heart_rate')
        j = request.form.get('body_temp')
        k = request.form.get('age')  
        l = request.form.get('gender') 
        
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO activity(Duration, `Heart rate`, `Body temperature`, Age, Gender) VALUES (%s, %s, %s, %s, %s)", (h,i,j,k,l))
        mysql.connection.commit()
        cur.close()
    
    
        duration = float(request.form['duration'])
        heart_rate = float(request.form['heart_rate'])
        body_temp = float(request.form['body_temp'])
        age = int(request.form['age'])
        
        gender_str = request.form['gender'].lower()
        gender = 0 if gender_str == 'male' else 1  # Convert to 0 or 1

        # Arrange features in correct order as expected by the model
        input_data = [[duration, heart_rate, body_temp, age, gender]]

        prediction = act.predict(input_data)[0]  
        print("Raw prediction output:", prediction)

        activity_map = {0: "Walking", 1: "Cycling", 2: "Running"}
        result = f"Predicted Activity: {activity_map.get(int(prediction), 'Unknown')}"

        return render_template('activity.html', result=result)
    
    return render_template('activity.html')


@app.route('/risk')
def risk_page():
    return render_template('risk.html')
@app.route('/predict_risk', methods=['GET', 'POST'])
def predict_risk():
    result = None
    if request.method == 'POST':
        m = request.form.get('age')
        n = request.form.get('weight')
        o = request.form.get('duration')
        p = request.form.get('heart_rate')  
        q = request.form.get('body_temp') 
        
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO risk(Age,Weight,Duration,`Heart rate`,`Body temperature`)VALUES(%s,%s,%s,%s,%s)",(m,n,o,p,q))
        mysql.connection.commit()
        cur.close()
        
        
        age = int(request.form['age'])
        weight = float(request.form['weight'])
        duration = float(request.form['duration'])
        heart_rate = float(request.form['heart_rate'])
        body_temp = float(request.form['body_temp'])

        input_data = [[age, weight, duration, heart_rate, body_temp]]

        prediction = risk.predict(input_data)[0]  
        print("Raw prediction output:", prediction)  

        prediction = int(prediction)  # ensure it's an integer
        risk_levels = {0: "High", 1: "Medium", 2: "Low"}
        result = f"Predicted Health Risk: {risk_levels.get(prediction, 'Unknown')}"

        return render_template('risk.html', result=result)
    
    return render_template('risk.html')




@app.route('/temperature')
def temperature():
    return render_template('temperature.html')

@app.route('/predict_temperature', methods=['GET', 'POST'])
def predict_temperature():
    result = None
    if request.method == 'POST':
        r = request.form.get('age')
        s = request.form.get('duration')
        t = request.form.get('heart_rate')  
    
        
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO temp(Age,Duration,`Heart rate`)VALUES(%s,%s,%s)",(r,s,t))
        mysql.connection.commit()
        cur.close()
        
        
        age = int(request.form['age'])
        heart_rate = float(request.form['heart_rate'])
        duration = float(request.form['duration'])

        # Make sure the model is trained and loaded as `temp_model`
        input_data = [[age, heart_rate, duration]]
        prediction = temp.predict(input_data)[0]
        result = f"Your Body Temperature is: {round(prediction, 2)}"

        return render_template('temperature.html', result=result)
    
    return render_template('temperature.html')



@app.route("/view calories")
def view_calories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM calories")
    userdetails = cur.fetchall()
    cur.close()
    
    return render_template('view calories.html',userdetails=userdetails)



@app.route('/update_calories/<int:id>',methods=['GET','POST'])  
def update_calories(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM calories WHERE id = %s",(id,))
    data = cur .fetchone()
    cur.close()
    if request.method == 'POST':
        a = request.form.get('gender')
        b = request.form.get('age')
        c = request.form.get('height')
        d = request.form.get('weight')  
        e = request.form.get('duration') 
        f = request.form.get('heart_rate')
        g = request.form.get('body_temp') 

        # Insert into database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE data INTO SET Gender =%s, Age =%s, Height =%s, Weight =%s,Duration =%s,`Heart rate` =%s,`body temperature` =%s WHERE id =%s",(a,b,d,e,f,g,id))
        mysql.connection.commit()
        cur.close()
    
        return redirect(url_for('view_calories'))
    
    return render_template('update calories.html',calories=calories)

@app.route('/delete_calories/<int:id>',methods=['GET','POST'])  
def delete_calories(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM calories WHERE id = %s",(id,))
    mysql.connection.commit()
    cur.close()
    
    return redirect(url_for('view_calories'))



@app.route("/view activity")
def view_activity():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM activity")
    userdetails = cur.fetchall()
    cur.close()
    
    return render_template('view activity.html',userdetails=userdetails)



@app.route('/update_activity/<int:id>',methods=['GET','POST'])  
def update_activity(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM activity WHERE id = %s",(id,))
    data = cur .fetchone()
    cur.close()
    if request.method == 'POST':
        h = request.form.get('duration')
        i = request.form.get('heart_rate')
        j = request.form.get('body_temp')
        k = request.form.get('age')  
        l = request.form.get('gender') 

        # Insert into database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE data INTO SET Duration =%s,`Heart rate` =%s,`body temperature` =%s ,Gender =%s, Age =%s WHERE id =%s",(h,i,j,k,l,id))
        mysql.connection.commit()
        cur.close()
    
        return redirect(url_for('view_activity'))
    
    return render_template('update activity.html',activity=activity)

@app.route('/delete_activity/<int:id>',methods=['GET','POST'])  
def delete_activity(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM activity WHERE id = %s",(id,))
    mysql.connection.commit()
    cur.close()
    
    return redirect(url_for('view_activity'))


@app.route("/view risk")
def view_risk():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM risk")
    userdetails = cur.fetchall()
    cur.close()
    
    return render_template('view risk.html',userdetails=userdetails)



@app.route('/update_risk/<int:id>',methods=['GET','POST'])  
def update_risk(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM risk WHERE id = %s",(id,))
    data = cur .fetchone()
    cur.close()
    if request.method == 'POST':
        m = request.form.get('age')
        n = request.form.get('weight')
        o = request.form.get('duration')
        p = request.form.get('heart_rate')
        q = request.form.get('body_temp')
        
        # Insert into database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE data INTO SET  Age =%s, Weight =%s, Duration =%s,`Heart rate` =%s,`body temperature` =%s , WHERE id =%s",(m,n,o,p,q,id))
        mysql.connection.commit()
        cur.close()
    
        return redirect(url_for('view_risk'))
    
    return render_template('update risk.html',risk=risk)

@app.route('/delete_risk/<int:id>',methods=['GET','POST'])  
def delete_risk(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM risk WHERE id = %s",(id,))
    mysql.connection.commit()
    cur.close()
    
    return redirect(url_for('view_risk'))


@app.route("/view temp")
def view_temp():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM temp")
    userdetails = cur.fetchall()
    cur.close()
    
    return render_template('view temp.html',userdetails=userdetails)



@app.route('/update_temp/<int:id>',methods=['GET','POST'])  
def update_temp(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM temp WHERE id = %s",(id,))
    data = cur .fetchone()
    cur.close()
    if request.method == 'POST':
        r = request.form.get('age')
        s = request.form.get('duration')
        t = request.form.get('heart_rate')
        
        # Insert into database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE data INTO SET  Age =%s , Duration =%s,`Heart rate` =%s , WHERE id =%s",(r,s,t,id))
        mysql.connection.commit()
        cur.close()
    
        return redirect(url_for('view_temp'))
    
    return render_template('update temp.html',temp=temp)

@app.route('/delete_temp/<int:id>',methods=['GET','POST'])  
def delete_temp(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM temp WHERE id = %s",(id,))
    mysql.connection.commit()
    cur.close()
    
    return redirect(url_for('view_temp'))

if __name__=='__main__':
    app.run(debug=True)