from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from functools import wraps 
import bcrypt

app = Flask(__name__)  


app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="banking"

mysql = MySQL(app) 

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return jsonify("Login required"), 401
        
        email = auth.username
        password = auth.password 
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        
        if not user: 
            return jsonify("Invalid email or password"), 401 
        #Needs to be changed to the number of the column that stores salts
        salt = user[2].encode('utf-8') 

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        #Needs to be changed to the number of the column that stores passwords
        if hashed_password.decode('utf-8') != user[0]:
            return jsonify("Invalid email or password "), 401
        return f(*args, **kwargs)

    return decorated

@app.route('/') 
@auth_required
def index(): 
    return "Hello"
# 1 get_courses_no_lecturer takes nothing
@app.route('/get_courses_no_lecturer', methods=['GET'])
def get_courses_no_lecturer_handler(): 
    return get_courses_no_lecturer()   
    
def get_courses_no_lecturer():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'" # would need to get every row for courses where lecturer is null
    response = cur.execute(query) 
    if response == 0:
        error_message = 'No courses found'
        return jsonify({'error': error_message}), 404
    courses = cur.fetchall()
    cur.close()
    return jsonify(courses), 200

# 2 get_courses_with_room_by_teacher_semester takes a teacher and a semester
@app.route('/get_courses_with_room_by_teacher_semester', methods=['GET'])
def get_courses_with_room_by_teacher_semester_handler():
    teacher = request.args.get('teacher')
    semester = request.args.get('semester')
    if not teacher or not semester:
        error_message = 'Teacher or semester parameter missing'
        return jsonify({'error': error_message}), 400 
    return get_courses_with_room_by_teacher_semester(teacher, semester) 
     

def get_courses_with_room_by_teacher_semester(teacher, semester): 
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` = %s" # would need to get every course_id where teacher and semester are the same as those given as arguments for a table not yet created. Or check the datetime for the bookings of the courses and see if that time is in the given semester
    cur.execute(query, (teacher))#cur.execute(query, (teacher, semester))
    courses = cur.fetchall()
    cur.close()  
    if courses == 0:
        error_message = 'No courses found'
        return jsonify({'error': error_message}), 404
    return jsonify(courses), 200
# 3 get_courses_by_room_date_timerange a room, a date and a time range (start and end times) 
@app.route('/get_courses_by_room_date_timerange', methods=['GET'])
def get_courses_by_room_date_timerange_handler():
    room = request.args.get('room')
    date = request.args.get('date')  
    time_range = request.args.get('time_range') 
    if not room or not date or not time_range:
        error_message = 'One or more parameter(s) missing'
        return jsonify({'error': error_message}), 400
    return get_courses_by_room_date_timerange(room, date, time_range)

def get_courses_by_room_date_timerange(room, date, time_range): 
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` = 'Trondheim'" #Get all courses in bookings where either the start time or end time is in the given timerange for the given room and date 
    cur.execute(query, (room,date,time_range))#cur.execute(query, (teacher, semester))
    courses = cur.fetchall()
    cur.close()  
    if courses == 0:
        error_message = 'No courses found'
        return jsonify({'error': error_message}), 404
    return jsonify(courses), 200
# 4 get_courses_by_room_date_time takes a room, a date and time 
@app.route('/get_courses_by_room_date_time', methods=['GET'])
def get_courses_by_room_date_time_handler():
    room = request.args.get('room')
    date = request.args.get('date')
    time = request.args.get('time')
    if not room or not date or not time:
        error_message = 'One or more parameter(s) missing'
        return jsonify({'error': error_message}), 400 
    return get_courses_by_room_date_time(room,date,time)



def get_courses_by_room_date_time(room,date,time): 
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"# Get all courses for bookings where the times is between the start time and end time for the course
    response = cur.execute(query, (room, date, time))
    if response == 0:
        error_message = 'No courses found'
        return jsonify({'error': error_message}), 404
    courses = cur.fetchall()
    cur.close()
    return jsonify(courses), 200

# 5 get_courses takes nothing
@app.route('/get_courses', methods=['GET'])
def get_courses_handler():
    return get_courses()
    
def get_courses():  
    cur = mysql.connection.cursor()    
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"#Get every course and use the foreign key for teacher to get name and email
    cur.execute(query)
    courses = cur.fetchall()
    cur.close()
    return jsonify(courses), 200

# 6 get_courses_with_institute_faculty_by_teacher takes a teacher 
@app.route('/get_courses_with_institute_faculty_by_teacher', methods=['GET'])
def get_courses_with_institute_faculty_by_teacher_handler():
    teacher = request.args.get('teacher')
    if not teacher:
        error_message = 'Lecturer parameter missing'
        return jsonify({'error': error_message}), 400 
    return get_courses_with_institute_faculty_by_teacher(teacher)
def get_courses_with_institute_faculty_by_teacher(teacher):  
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"##
    response = cur.execute(query, (teacher,))
    if response == 0:
        error_message = 'No courses found for this lecturer'
        return jsonify({'error': error_message}), 404

    courses = cur.fetchall()
    cur.close()
    return jsonify(courses), 200

# 7 get_courses_with_institute_faculty_by_lecturer takes a lecturer
@app.route('/get_courses_with_institute_faculty_by_lecturer', methods=['GET'])
def get_courses_with_institute_faculty_by_lecturer_handler():
    lecturer = request.args.get('lecturer')
    if not lecturer:
        error_message = 'Lecturer parameter missing'
        return jsonify({'error': error_message}), 400
    return get_courses_with_institute_faculty_by_lecturer(lecturer)


def get_courses_with_institute_faculty_by_lecturer(lecturer):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"#Just get the room number from the booking where the courseId are the same as those where the parameter matches a lecturer
    response = cur.execute(query, (lecturer,))
    if response == 0:
        error_message = 'No courses found for this lecturer'
        return jsonify({'error': error_message}), 404

    data = cur.fetchall()
    cur.close()
    return jsonify(data), 200


# 8 get_avaiable_rooms_by_date_timerange takes a date and time range (start and end times)
@app.route('/get_avaiable_rooms_by_date_timerange', methods=['GET'])
def get_avaiable_rooms_by_date_timerange_handler():
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    if not date or not start_time or not end_time:
        error_message = 'Date, start_time, or end_time parameter missing'
        return jsonify({'error': error_message}), 400 
    return get_avaiable_rooms_by_date_timerange_handler(date,start_time,end_time) 

def get_avaiable_rooms_by_date_timerange_handler(date,start_time,end_time):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"#Gets the roomNo of all the rooms that are not in bookings where an end time or a start time is between the given time range 
    response = cur.execute(query, (date, start_time, end_time))
    if response == 0:
        error_message = 'No available rooms found'
        return jsonify({'error': error_message}), 404

    rooms = cur.fetchall()
    cur.close()
    return jsonify(rooms), 200


# 9 get_bookings_with_room_building_by_user takes a user
@app.route('/get_bookings_with_room_building_by_user', methods=['GET'])
def get_bookings_with_room_building_by_user_handler():
    user = request.args.get('user')
    if not user:
        error_message = 'User parameter missing'
        return jsonify({'error': error_message}), 400 
    return get_bookings_with_room_building_by_user(user) 

def get_bookings_with_room_building_by_user(user): 
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"#Get all bookings where the user is the same as the given one
    response = cur.execute(query, (user,))
    if response == 0:
        error_message = 'No bookings found for this user'
        return jsonify({'error': error_message}), 404

    bookings = cur.fetchall()
    cur.close()
    return jsonify(bookings), 200


# 10 get_rooms_with_bookings_and_booker takes nothing
@app.route('/get_rooms_with_bookings_and_booker', methods=['GET'])
def get_rooms_with_bookings_and_booker_handler(): 
    return get_rooms_with_bookings_and_booker_handler() 

def get_rooms_with_bookings_and_booker():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"#Get all rooms from room table and for each room show their bookings(with username from booking)
    response = cur.execute(query)
    if response == 0:
        error_message = 'No rooms with bookings found'
        return jsonify({'error': error_message}), 404

    rooms = cur.fetchall()
    cur.close()
    return jsonify(rooms), 200


# 11 get_rooms_with_number_of_bookings takes nothing
@app.route('/get_rooms_with_number_of_bookings', methods=['GET'])
def get_rooms_with_number_of_bookings_handler(): 
    return get_rooms_with_number_of_bookings() 
def get_rooms_with_number_of_bookings(): 
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"#
    response = cur.execute(query)
    if response == 0:
        error_message = 'No rooms found'
        return jsonify({'error': error_message}), 404

    rooms = cur.fetchall()
    cur.close()
    return jsonify(rooms), 200


# 13 get_teachers_with_courses_and_course_locations takes nothing
@app.route('/get_teachers_with_courses_and_course_locations', methods=['GET'])
def get_teachers_with_courses_and_course_locations_handler(): 
    return get_teachers_with_courses_and_course_locations() 
def get_teachers_with_courses_and_course_locations(): 
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"
    response = cur.execute(query)
    if response == 0:
        error_message = 'No teachers found'
        return jsonify({'error': error_message}), 404

    teachers = cur.fetchall()
    cur.close()
    return jsonify(teachers), 200


# 14 get_teachers_with_teaching_hours takes nothing
@app.route('/get_teachers_with_teaching_hours', methods=['GET'])
def get_teachers_with_teaching_hours_handler(): 
    return get_teachers_with_teaching_hours() 
def get_teachers_with_teaching_hours(): 
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"
    response = cur.execute(query)
    if response == 0:
        error_message = 'No teachers found'
        return jsonify({'error': error_message}), 404

    teachers = cur.fetchall()
    cur.close()
    return jsonify(teachers), 200


# 15 get_monday_courses_with_teachers_info takes nothing
@app.route('/get_monday_courses_with_teachers_info', methods=['GET'])
def get_monday_courses_with_teachers_info_handler(): 
    return get_monday_courses_with_teachers_info() 
def get_monday_courses_with_teachers_info():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"
    response = cur.execute(query)
    if response == 0:
        error_message = 'No courses found'
        return jsonify({'error': error_message}), 404

    courses = cur.fetchall()
    cur.close()
    return jsonify(courses), 200


# 16 get_teachers_withaverage_numberstudents takes nothing, sorted by students
@app.route('/get_teachers_with_average_number_students', methods=['GET'])
def get_teachers_with_average_numberstudents_handler(): 
    return get_teachers_with_average_numberstudents()  

def get_teachers_with_average_numberstudents(): 
    cur = mysql.connection.cursor()
    query = "SELECT * FROM `customer` WHERE `customer`.`City` ='Trondheim'"
    response = cur.execute(query)
    if response == 0:
        error_message = 'No teachers found'
        return jsonify({'error': error_message}), 404

    teachers = cur.fetchall()
    cur.close()
    return jsonify(teachers), 200 

if __name__ == '__main__':
    app.run(debug=True) 

