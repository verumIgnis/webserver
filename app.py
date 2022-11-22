from flask import request
from flask import Flask, jsonify
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

passwd = os.getenv("PASSWD")

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=passwd
)

print(mydb)

dbCursor = mydb.cursor(buffered=True)
dbCursor.execute("USE clocksys")

app = Flask(__name__)

@app.route("/clocksys/keepalive", methods=['GET', 'POST'])
def keepAlive():
    print("KA recieved")
    return "True"

@app.route("/clocksys/clockin", methods=['POST'])
def clockIn():
    print(request.json)
    clockMinute = request.json["minute"]
    clockHour = request.json["hour"]

    dbCursor.execute("SELECT total FROM clocklogs ORDER BY id DESC LIMIT 0, 1;")
    total = dbCursor.fetchone()

    print(total[0])

    dbCursor.execute(f"INSERT INTO clocklogs (clockedin, total, time, minute, hour) VALUES (1, {total[0]}, '{clockHour}:{clockMinute}', {clockMinute}, {clockHour});")
    mydb.commit()
    return "True"

@app.route("/clocksys/clockout", methods=['POST'])
def clockOut():
    print(request.json)
    clockMinute = request.json["minute"]
    clockHour = request.json["hour"]

    dbCursor.execute("SELECT total FROM clocklogs ORDER BY id DESC LIMIT 0, 1;")
    total = dbCursor.fetchone()

    dbCursor.execute("SELECT minute FROM clocklogs ORDER BY id DESC LIMIT 0, 1;")
    lastClockMinute = dbCursor.fetchone()

    dbCursor.execute("SELECT hour FROM clocklogs ORDER BY id DESC LIMIT 0, 1;")
    lastClockHour = dbCursor.fetchone()

    newTotal = float(total[0]) + float(lastClockHour[0]) + float(lastClockMinute[0] / 60.0)
    dbCursor.execute(f"INSERT INTO clocklogs (clockedin, total, time, minute, hour) VALUES (0, {newTotal}, '{clockHour}:{clockMinute}', {clockMinute}, {clockHour})")
    mydb.commit()
    return "True"

@app.route("/clocksys/getlogs", methods=['GET'])
def getLogs():
    numLogs = "10"
    numLogs = request.args.get('num')
    dbCursor.execute(f"SELECT * FROM clocklogs ORDER BY id DESC LIMIT 0, {numLogs};")
    out = dbCursor.fetchall()
    return out

if __name__ == '__app__':
    app.run(port=5000, host='127.0.0.1')