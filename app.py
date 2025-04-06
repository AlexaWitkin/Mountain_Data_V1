# Alexa Witkin 
# CS 2500

from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import pwinput as pw
import sqlite3 # included in standard python distribution
import pandas as pd
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import io

"""
Similar to setting up a main in Python, this is how we initialize our app.py or our routing page in Flask!
"""
app = Flask(__name__)
saveCustomerId = ""

@app.route("/")
def index():
    '''
    The login page will be the home page.
    '''
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    result = render_template("login.html")

    if request.method == "POST":
        con = sqlite3.connect('mountain_data.db', isolation_level=None)
        cur = con.cursor()

        '''
        Create a Python script that uses SQLite integration and Python input() 
        '''
        #print("Welcome to Mountain Data Lite") -> goes in html landing page
        customer_name = request.form.get("username", None)

        customer_id = request.form.get("password", None)

        '''
        Then use the name and id to check if the name matches the 
        id in the database.
        '''
        cur.execute(f"SELECT firstName FROM Customers WHERE firstName = " + '"' + customer_name + '"' + ";")
        firstName = cur.fetchone() 
        if (firstName != None):     
            cur.execute(f"SELECT customerId FROM Customers WHERE firstName = " + '"' + customer_name + '"' + ";")
            customerId = cur.fetchone()
            if (customerId != None):
                global saveCustomerId 
                saveCustomerId = customerId[0]
        ''' 
        If the username is incorrect, the page will prompt the user again.  
        If password is incorrect for a username, the page will prompt the user again.  
        In both cases, prompt again for username/password.  
        The user has unlimited attempts to gain access.
        '''
        if (firstName != None) and (customerId != None) and (customer_name == firstName[0]) and (str(customer_id) == str(customerId[0])):
            result = render_template("successful.html")
        else:
            result = render_template("login.html")
       
    return result


@app.route("/about")
def about():
    '''
    Should contain a summary of this project and what the website aims to do.
    Users should not be able to alter this information, it is simply for viewing.
    '''
    return render_template("about.html")

        
@app.route("/successful")
def successful():
    '''
    Simply shows the list of options user can select from to navigate to once they've logged in.
    '''
    return render_template("successful.html")

        
@app.route("/customer_info", methods=["GET", "POST"])
def customer_info():
    '''
    Show only that customer's info.
    Allow user to edit their lastName, age, numDays.
    Validate they are only editing from those options.
    '''
    #global saveCustomerId
    customerId = saveCustomerId
    
    con = sqlite3.connect('mountain_data.db', isolation_level=None)
    cur = con.cursor()

    '''
    customers num times per day will get updated automatically by count of 
    customers id appearing on given day (ie: WHERE date = ?)
    '''

    cur.execute(f'SELECT count(DISTINCT "date") as "count" FROM LiveData WHERE customerId = "{customerId}";')
    numDays = cur.fetchone()

    cur.execute(f"UPDATE Customers SET numDays = '{numDays[0]}' WHERE customerId = '{customerId}';")
    con.commit()

    
    cur.execute(f"SELECT * FROM Customers WHERE customerId = '{customerId}';")
    data = cur.fetchall()

    # Column names 
    columns = ["index", "date", "customerId", "firstName", "lastName", "age", "numDays"]

    # Format data as a list of dictionaries
    formatted_data = [dict(zip(columns, row)) for row in data]


    if request.method == "POST":
        '''
        Create a Python script that uses SQLite integration and Python input() 
        '''
        column = request.form.get("selection", None)
        newValue = request.form.get("value", None)

        # do the edit in the db 
        # get the old value to be replaced
        cur.execute(f"SELECT '{column}' FROM Customers WHERE customerId = '{customerId}';")
        oldVal = cur.fetchone()
        # replace old value with new value in db
        cur.execute(f"UPDATE Customers SET '{column}' = '{newValue}' WHERE '{column}' = '{oldVal[0]}' AND customerId = '{customerId}';")
        con.commit()

        cur.execute(f"SELECT * FROM Customers WHERE customerId = '{customerId}';")
        data = cur.fetchall()
    
        # Column names 
        columns = ["index", "date", "customerId", "firstName", "lastName", "age", "numDays"]

        # Format data as a list of dictionaries
        formatted_data = [dict(zip(columns, row)) for row in data]
        

    # Pass data to the template
    return render_template("customer_info.html", customer_data=formatted_data)
        

    # return render_template("customer_info.html", customer_data = formatData)


@app.route("/live_data", methods=["GET", "POST"])
def live_data():
    '''
    Show the live_data.
    Allow the user to add a new entry about themself.
    Validate they are entering their own information only.
    '''
    #global saveCustomerId
    
    con = sqlite3.connect('mountain_data.db', isolation_level=None)
    cur = con.cursor()
    
    cur.execute(f"SELECT * FROM LiveData WHERE customerId = '{saveCustomerId}';")
    data = cur.fetchall()

    # Column names 
    columns = ["index", "date", "time", "customerId", "location", "plateId"]

    # Format data as a list of dictionaries
    formatted_data = [dict(zip(columns, row)) for row in data]

    if request.method == "POST":
        '''
        Create a Python script that uses SQLite integration and Python input() 
        '''
        removeIndex = request.form.get("index", None)

        if (removeIndex != None):
            # remove unwanted data from db
            cur.execute(f'DELETE FROM LiveData WHERE "index" = "{removeIndex}";')
            con.commit()

            cur.execute(f"SELECT * FROM LiveData WHERE customerId = '{saveCustomerId}';")
            data = cur.fetchall()

            # column names (throw away index)
            columns = ["index", "date", "time", "customerId", "location", "plateId"]

            # format like a dictionary
            formatted_data = [dict(zip(columns, row)) for row in data]
        
            return render_template("live_data.html", live_data=formatted_data)

        customerId = saveCustomerId
        date = request.form.get("date", None)
        hours = request.form.get("hours", None)
        minutes = request.form.get("minutes", None)
        plateId = request.form.get("plateId", None)
        
        if (int(minutes) < 10):
            time = (f'{hours}:0{minutes}')
        else:
            time = (f'{hours}:{minutes}')

        # do the edit in the db 
        # get the old value to be replaced
        cur.execute(f"SELECT location FROM Plates WHERE plateId = '{plateId}';")
        location = cur.fetchone()

        cur.execute(f"SELECT count('index') as 'count' FROM LiveData;")
        index = cur.fetchone()
        # replace old value with new value in db
        cur.execute(f"INSERT INTO LiveData ('index', date, time, customerId, location, plateId) VALUES ('{index[0]}', '{date}','{time}','{customerId}', '{location[0]}', '{plateId}');")
        con.commit()

        cur.execute(f"SELECT * FROM LiveData WHERE customerId = '{customerId}';")
        data = cur.fetchall()

        # column names (throw away index)
        columns = ["index", "date", "time", "customerId", "location", "plateId"]

        # format like a dictionary
        formatted_data = [dict(zip(columns, row)) for row in data]
        
        return render_template("live_data.html", live_data=formatted_data)
    
    return render_template("live_data.html", live_data=formatted_data)


@app.route("/plate_info")
def plate_info():
    '''
    Show the plate_info.
    Users should not be able to alter this information, it is simply for viewing.
    '''
    con = sqlite3.connect('mountain_data.db', isolation_level=None)
    cur = con.cursor()
    
    cur.execute(f"SELECT * FROM Plates;")
    data = cur.fetchall()

    # Column names 
    columns = ["index", "plateNum", "plateId", "location", "liftType"]

    # Format data as a list of dictionaries
    formatted_data = [dict(zip(columns, row)) for row in data]
    return render_template("plate_info.html", plate_info=formatted_data)


@app.route("/frequency_log", methods=["GET", "POST"])
def frequency_log():

    con = sqlite3.connect('mountain_data.db', isolation_level=None)
    cur = con.cursor()

    customerId = saveCustomerId
    
    ''' 
    date with most runs + number of runs that day, 
    date with least runs + number of runs that day
    '''
    # least runs 
    cur.execute(f'SELECT "date", count("date") as "count" FROM LiveData WHERE customerId = "{customerId}" GROUP BY "date" ORDER BY "count" ASC LIMIT "1";')
    leastRuns = cur.fetchall()

    # most runs
    cur.execute(f'SELECT "date", count("date") as "count" FROM LiveData WHERE customerId = "{customerId}" GROUP BY "date" ORDER BY "count" DESC LIMIT "1";')
    mostRuns = cur.fetchall()

    # avg runs
    formatAvgRuns = []
    cur.execute(f'SELECT AVG("count") as "avg" FROM (SELECT count("date") as "count" FROM LiveData WHERE customerId = "{customerId}" GROUP BY "date" ORDER BY "count");')
    avgRuns = cur.fetchone()
    cur.execute(f'SELECT DISTINCT "date" FROM LiveData WHERE customerId = "{customerId}";')
    dates = cur.fetchall()
    formatAvgRuns.append(dates[0][0])
    formatAvgRuns.append(dates[len(dates)-1][0])
    formatAvgRuns.append(f'{avgRuns[0]:.2f}')

    return render_template("frequency_log.html", least=leastRuns, most=mostRuns, avg=formatAvgRuns)


# This will dynamically generate a graph for the graph page
@app.route('/line_graph_image')
def line_graph_image():

    con = sqlite3.connect('mountain_data.db', isolation_level=None)
    cur = con.cursor()

    customerId = saveCustomerId

    cur.execute(f'SELECT "date", count("date") as "count" FROM LiveData WHERE customerId = "{customerId}" GROUP BY "date" ORDER BY "date" ASC;')
    data = cur.fetchall()

    # Generate data for plotting (these are just random numbers)
    dates = []
    runs = []
    for i in range(0,len(data)):
        dates.append(data[i][0])
        runs.append(data[i][1])

    plotData = {'Date': dates,
            'Number of Runs': runs}
    
    df = pd.DataFrame(plotData)

    # Create a simple line plot using Matplotlib
    plt.figure(figsize=(8, 6))
    plt.plot(df['Date'], df['Number of Runs'], marker='o')
    plt.xlabel('Date')
    plt.ylabel('Number of Runs')
    plt.title('Number of Runs Each Day')

    # Convert the graph to a base64 encoded string
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close("all")

    # Return the image as a response with a type of image/png
    return make_response(img.read()), 200, {'Content-Type': 'image/png'}


# This will dynamically generate a graph for the graph page
@app.route('/hist_graph_image')
def hist_graph_image():

    con = sqlite3.connect('mountain_data.db', isolation_level=None)
    cur = con.cursor()

    customerId = saveCustomerId

    cur.execute(f'SELECT "date", count("date") as "count" FROM LiveData WHERE customerId = "{customerId}" GROUP BY "date" ORDER BY "date" ASC;')
    data2 = cur.fetchall()

    # Generate data for plotting (these are just random numbers)
    dates2 = []
    runs2 = []
    for i in range(0,len(data2)):
        dates2.append(data2[i][0])
        runs2.append(data2[i][1])

    plotData2 = {'Date': dates2,
            'Number of Runs': runs2}
    
    df2 = pd.DataFrame(plotData2)

    # Create a simple histogram plot using Matplotlib
    plt.figure(figsize=(8, 6))
    plt.hist(df2['Date'], bins=20, weights=df2['Number of Runs'])
    plt.xlabel('Date')
    plt.ylabel('Number of Runs')
    plt.title('Number of Runs Each Day')

    # Convert the graph to a base64 encoded string
    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    plt.close("all")

    # Return the image as a response with a type of image/png
    return make_response(img2.read()), 200, {'Content-Type': 'image/png'}


@app.route("/leaderboard")
def leaderboard():
    con = sqlite3.connect('mountain_data.db', isolation_level=None)
    cur = con.cursor()

    cur.execute(f'SELECT count("date") as "count" FROM LiveData GROUP BY customerId')
    numRuns = cur.fetchall()

    # NEED TO LOOP THROUGH FOR EACH CUSTOMER ID
    prefLift = []
    for i in range (0, len(numRuns)):
        cur.execute(f'SELECT location, count(DISTINCT "time") as "count" FROM LiveData WHERE customerId = "{i+1}" GROUP BY location ORDER BY "count" DESC;')
        temp = cur.fetchone()
        prefLift.append(temp[0])

    cur.execute(f'DROP TABLE IF EXISTS Leaderboard;')
    con.commit()
    
    cur.execute(f'CREATE TABLE Leaderboard AS SELECT customerId, firstName, lastName, numDays FROM Customers')
    con.commit()

    cur.execute("ALTER TABLE Leaderboard ADD numRuns TEXT")
    cur.execute("ALTER TABLE Leaderboard ADD prefLift TEXT")
    con.commit()

    for i in range (0, len(numRuns)):
        cur.execute(f'UPDATE Leaderboard SET numRuns = "{numRuns[i][0]}" WHERE customerId = "{i + 1}";')
    con.commit()

    for i in range (0, len(prefLift)):
        cur.execute(f'UPDATE Leaderboard SET prefLift = "{prefLift[i]}" WHERE customerId = "{i + 1}";')
    con.commit()

    cur.execute(f'DROP TABLE IF EXISTS LeaderboardSorted;')
    con.commit()

    cur.execute(f'CREATE TABLE LeaderboardSorted AS SELECT * FROM Leaderboard ORDER BY numRuns DESC;')
    con.commit()

    cur.execute(f"SELECT * FROM LeaderboardSorted;")
    data = cur.fetchall()


    # Column names 
    columns = ["customerId", "firstName", "lastName", "numDays", "numRuns", "prefLift"]

    # Format data as a list of dictionaries
    formatted_data = [dict(zip(columns, row)) for row in data]

    # get most frequently used lift -> use to get most used plates
    cur.execute(f'SELECT prefLift, count(DISTINCT customerId) as "count" FROM LeaderboardSorted GROUP BY prefLift ORDER BY "count" DESC LIMIT "1";')
    freqLift = cur.fetchone()

    freqPlates = []
    cur.execute(f'SELECT plateId FROM Plates JOIN LeaderboardSorted ON LeaderboardSorted.prefLift = Plates.location  WHERE LeaderboardSorted.prefLift = "{freqLift[0]}" GROUP BY plateId;')
    tempPlates = cur.fetchall()
    for i in range(0,len(tempPlates)):
        freqPlates.append(tempPlates[i][0])

    freqPlatesNum = []
    cur.execute(f'SELECT plateNum FROM Plates JOIN LeaderboardSorted ON LeaderboardSorted.prefLift = Plates.location  WHERE LeaderboardSorted.prefLift = "{freqLift[0]}" GROUP BY plateId;')
    tempPlatesNum = cur.fetchall()
    for i in range(0,len(tempPlatesNum)):
        freqPlatesNum.append(tempPlatesNum[i][0])


    return render_template("leaderboard.html", leaderboard_info=formatted_data, freq_plates=freqPlates, freq_plates_nums=freqPlatesNum)


if __name__ == "__main__":
    app.run(debug=True)



''' 
look into application context 
'''