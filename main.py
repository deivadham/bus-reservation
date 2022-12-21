from flask import Flask, request, render_template
import mysql.connector
app = Flask(__name__, template_folder='template', static_folder='static')
from datetime import datetime

@app.route('/')
def home():
    return render_template('enter.html')

def confirm_no(Fone, Lend,Lone, Fend):
    now = datetime.now()
    dt_string = now.strftime("%d%m%H%M%S")
    print(dt_string)
    confirmno= Fone+Lend+dt_string+Lone+Fend
    return confirmno


@app.route('/enter/reserve', methods =["GET", "POST"])
def res_info():
    if request.method == "POST":
       busRte = request.form.get("Route_Number")
       noSeats = request.form.get("Num_Seats")
       Fname = request.form.get("First_Name")
       Lname = request.form.get("Last_Name")
       Date = request.form.get("Date")
       try:
           connection = mysql.connector.connect(host='localhost',
                                         database=<DB NAME>,
                                         user=<DB USER>,
                                         password=<PASSWORD>)
           cursor = connection.cursor()
           sqlquery = """select bookedseats, totalseats, traveldate  from bus_db.reserve_seat where routeno = %s"""
           cursor.execute(sqlquery, [busRte])
           fetch = cursor.fetchone()
           bookedseats = fetch[0]
           totalseats = fetch[1]
           traveldate = fetch[2]
           st = 1
           print(bookedseats, ":", totalseats, ":", st)
           potseats = bookedseats + int(noSeats)
           if(potseats <= totalseats):
               print("Can book")
               confirmNo = confirm_no(Fname[0],Lname[-1],Lname[0],Fname[-1])
               updatequery1 = """Update reserve_seat set bookedseats = %s where routeno = %s"""
               cursor.execute(updatequery1, [potseats, busRte])
               updatequery2 = """INSERT INTO reservations
                                (confirm_no, first_name, last_name, routeno, traveldate, seats)
                                values
                                (%s, %s, %s, %s, %s, %s);"""
               cursor.execute(updatequery2, [confirmNo, Fname, Lname,busRte,Date, noSeats])
               connection.commit()
               return render_template('yeseats.html', confirmNo=confirmNo, Fname=Fname, Lname=Lname,busRte=busRte,Date=Date,noSeats= noSeats)
               print("Record Updated successfully ")
           else:
               print("Sorry")
               return render_template('noseats.html')
       except mysql.connector.Error as error:
           print("Failed to update table record: {}".format(error))

       finally:
           if connection.is_connected():
               connection.close()
               print("MySQL connection is closed")
    else:
        return render_template('reserve.html')

@app.route('/enter/cancel', methods =["GET", "POST"])
def cancel_info():
    if request.method == "POST":
        confirm_no = request.form.get("Confirmation_Number")
        confirm_no = confirm_no
        print(confirm_no)
        try:
            connection = mysql.connector.connect(host='localhost',
                                         database=<DB NAME>,
                                         user=<DB USER>,
                                         password=<PASSWORD>)
            cursor = connection.cursor()

        #Querying booked seats
            sqlquery1 = """select routeno, seats, first_name, last_name, traveldate from bus_db.reservations where confirm_no = %s;"""
            cursor.execute(sqlquery1, [confirm_no] )
            fetch1 = cursor.fetchone()
            print("fetch1:", fetch1)
            if fetch1==None:
                return render_template('noconfirm.html')
            else:
                routeno = fetch1[0]
                allocseats = fetch1[1]
                fName= fetch1[2]
                lName = fetch1[3]
                Tdate = fetch1[4]
                sqlquery2 = """select bookedseats from bus_db.reserve_seat where routeno = %s;"""
                cursor.execute(sqlquery2, [routeno])
                fetch2 = cursor.fetchone()
                bookedseat = fetch2[0]
                updatebookseats = bookedseat-allocseats
                print("Record Exists", routeno,bookedseat, updatebookseats)
                updatequery1 = """DELETE FROM reservations WHERE confirm_no = %s;"""
                cursor.execute(updatequery1, [confirm_no])
                connection.commit()
                updatequery2 = """Update reserve_seat set bookedseats=%s where routeno = %s;"""
                cursor.execute(updatequery2, [updatebookseats, routeno])
                connection.commit()
                print("Record Updated successfully ")
                return render_template('yesconfirm.html', fName=fName, lName= lName, routeno= routeno, Tdate=Tdate, allocseats= allocseats)
        except mysql.connector.Error as error:
            print("Failed to update table record: {}".format(error))

        finally:
            if connection.is_connected():
                connection.close()
                print("MySQL connection is closed")
    return render_template('cancel.html')

@app.route('/enter/enter/reserve/status')
def status():
    return render_template('noseats.html')



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)

