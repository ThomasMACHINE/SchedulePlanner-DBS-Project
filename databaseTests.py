from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from functools import wraps 
import bcrypt

app = Flask(__name__)  


app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="prosjekt"

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
        
        passwd_to_check = bytes(password, 'utf-8') 
        #Needs to be changed to the number of the column that stores passwords
        passwd = bytes(user[0], 'utf8')
        if bcrypt.hashpw(passwd_to_check, passwd) != passwd:
            return jsonify("Invalid email or password "), 401
        return f(*args, **kwargs)

    return decorated


def administrator_required(f):
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
        #Needs to be changed to the number of the column that stores admin flag 
        if user[0] != 1: 
            return jsonify("No permission"), 401
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
    query = "SELECT course.*, CourseBooking.roomNo, building.Name FROM course INNER JOIN CourseBooking ON course.ID = CourseBooking.courseID LEFT JOIN rooms ON rooms.roomNo = CourseBooking.roomNo LEFT JOIN building ON rooms.buildingId = building.Id WHERE course.userID IS NULL"
    response = cur.execute(query) 
    if response == 0:
        error_message = 'No courses found'
        return jsonify({'error': error_message}), 404
    courses = cur.fetchall()
    cur.close()
    return jsonify(courses), 200

# 2 get_courses_with_room_by_teacher_semester takes a teacher and a semester
# Semester has to be formatted like "2023S" and "2023F"
@app.route('/get_courses_with_room_by_teacher_semester', methods=['GET'])
def get_courses_with_room_by_teacher_semester_handler():
    teacher = request.args.get('teacher')
    yearAndSemester = request.args.get('semester') 
    semester = yearAndSemester[-1] 
    year = yearAndSemester[:-1] 
    semester_start = ''  
    semester_end = ''
    if(semester == 'S'):
        semester_start = year + '-01-01'  
        semester_end =  year + '-06-01' 
    if(semester == 'F'): 
        semester_start = year + '-06-02'   
        semester_end =  year + '-12-31'
    if not teacher or not yearAndSemester:
        error_message = 'Teacher or semester parameter missing'
        return jsonify({'error': error_message}), 400 
    return get_courses_with_room_by_teacher_semester(teacher, semester_start, semester_end) 
     



def get_courses_with_room_by_teacher_semester(teacher, semester_start, semester_end): 
    cur = mysql.connection.cursor() 
    #First getting the course ID from every course with the correct teacher, then getting every booking with that same course_id + date that is in the same year and is between semester_start and semester_end 
    query = "SELECT course.* FROM course INNER JOIN CourseBooking ON course.ID = CourseBooking.courseID WHERE course.userID = %s AND CourseBooking.date BETWEEN %s AND %s"# would need to get every course_id where teacher and semester are the same as those given as arguments for a table not yet created. Or check the datetime for the bookings of the courses and see if that time is in the given semester
    cur.execute(query, (teacher, semester_start, semester_end))#cur.execute(query, (teacher, semester))
    courses = cur.fetchall()
    cur.close()
    if courses == 0:
        error_message = 'No courses found'
        return jsonify({'error': error_message}), 404
    return jsonify(courses), 200 

# 3 get_courses_by_room_date_timerange a room, a date and a time range (start and end times)  
# The timerange must be in the format start-end, HH:MM:SS-HH:MM:SS, 06:45:11-22:15:34
@app.route('/get_courses_by_room_date_timerange', methods=['GET'])
def get_courses_by_room_date_timerange_handler():
    room = request.args.get('room')
    date = request.args.get('date')  
    time_range = request.args.get('time_range')  
    time_start, time_end = time_range.split("-")
    if not room or not date or not time_range:
        error_message = 'One or more parameter(s) missing'
        return jsonify({'error': error_message}), 400
    return get_courses_by_room_date_timerange(room, date, time_start, time_end)

def get_courses_by_room_date_timerange(room, date, time_range_start, time_range_end): 
    cur = mysql.connection.cursor()
    query = "SELECT course.* FROM course INNER JOIN CourseBooking ON course.ID = CourseBooking.courseID WHERE `CourseBooking`.`roomNo` = %s AND `CourseBooking`.`date` = %s AND `CourseBooking`.`start_time` > %s AND `CourseBooking`.`end_time` < %s" #Get all courses in bookings where either the start time or end time is in the given timerange for the given room and date 
    cur.execute(query, (room,date,time_range_start,time_range_end))#cur.execute(query, (teacher, semester))
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
        error_message = 'Missing room, date or time'
        return jsonify({'error': error_message}), 400 
    return get_courses_by_room_date_time(room,date,time)



def get_courses_by_room_date_time(room,date,time): 
    cur = mysql.connection.cursor()
    query = "SELECT course.* FROM course INNER JOIN CourseBooking ON course.ID = CourseBooking.courseID WHERE `CourseBooking`.`roomNo` = %s AND `CourseBooking`.`date` = %s AND  %s BETWEEN `CourseBooking`.`start_time` AND `CourseBooking`.`end_time`"# Get all courses for bookings where the times is between the start time and end time for the course
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
    query = "SELECT course.*, users.FirstName, users.email FROM course INNER JOIN users ON course.userId = users.Id"#Get every course and use the foreign key for teacher to get name and email
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
    query = "SELECT course.*, teacher.faculty, teacher.institute FROM course INNER JOIN teacher ON course.userId = teacher.userId WHERE course.userId = %s"
    response = cur.execute(query, (teacher,))
    if response == 0:
        error_message = 'No courses found for this lecturer'
        return jsonify({'error': error_message}), 404
    
    courses = cur.fetchall()
    cur.close()
    return jsonify(courses), 200

# 7 get_courses_with_room_by_lecturer takes a lecturer
@app.route('/get_courses_with_room_by_lecturer', methods=['GET'])
def get_courses_with_room_by_lecturer_handler():
    lecturer = request.args.get('lecturer')
    if not lecturer:
        error_message = 'Lecturer parameter missing'
        return jsonify({'error': error_message}), 400
    return get_courses_with_room_by_lecturer(lecturer)


def get_courses_with_room_by_lecturer(lecturer):
    cur = mysql.connection.cursor()
    query = "SELECT course.*, CourseBooking.roomNo, building.Name FROM course INNER JOIN CourseBooking ON course.ID = CourseBooking.courseID LEFT JOIN rooms ON rooms.roomNo = CourseBooking.roomNo LEFT JOIN building ON rooms.buildingId = building.Id  WHERE course.userId = %s"#Just get the room number from the booking where the courseId are the same as those where the parameter matches a lecturer
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
    time_range = request.args.get('time_range')  
    time_start, time_end = time_range.split("-") 
    if not date or not time_range: 
        error_message = 'Date or time_range parameter missing' 
        return jsonify({'error': error_message}), 400 
    return get_avaiable_rooms_by_date_timerange_handler(date,time_start,time_end) 
#Shows only rooms that are available for the entire time range given 
def get_avaiable_rooms_by_date_timerange_handler(date,start_time,end_time):
    cur = mysql.connection.cursor()
    query = """
        SELECT rooms.* 
        FROM rooms
        WHERE rooms.roomNo NOT IN (
            SELECT CourseBooking.roomNo
            FROM CourseBooking 
            WHERE  CourseBooking.Date = %s AND (CourseBooking.start_time BETWEEN %s AND %s OR CourseBooking.end_time BETWEEN %s AND %s)
        ) AND rooms.roomNo NOT IN (
            SELECT UserBooking.roomNo
            FROM UserBooking
            WHERE UserBooking.Date = %s AND (UserBooking.start_time BETWEEN %s AND %s OR UserBooking.end_time BETWEEN %s AND %s)
        )
    """

    response = cur.execute(query, (date, start_time, end_time, start_time, end_time, date, start_time, end_time, start_time, end_time,))
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
    query = "SELECT UserBooking.roomNo, date, CONCAT(start_Time), CONCAT(end_Time), userId, building.Name FROM UserBooking LEFT JOIN rooms ON rooms.roomNo = UserBooking.roomNo LEFT JOIN building ON rooms.buildingId = building.Id WHERE UserBooking.userId = %s"#Get all bookings where the user is the same as the given one
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
    return get_rooms_with_bookings_and_booker() 

def get_rooms_with_bookings_and_booker():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM rooms"#Get all rooms from room table and for each room show their bookings(with username from booking)
    cur.execute(query) 
    rooms = [] 
    for room in cur.fetchall(): 
        cur.execute("SELECT UserBooking.roomNo, UserBooking.date, CONCAT(UserBooking.start_time), CONCAT(UserBooking.end_time),  Users.firstName , Users.lastName FROM UserBooking INNER JOIN Users on UserBooking.userId = users.Id WHERE UserBooking.roomNo = %s",(room[0],)) 
        userBookingsWithNames= cur.fetchall()
        cur.execute("SELECT CourseBooking.roomNo, CourseBooking.date, CONCAT(CourseBooking.start_time), CONCAT(CourseBooking.end_time) , Course.name FROM CourseBooking INNER JOIN Course on CourseBooking.courseId = course.Id WHERE CourseBooking.roomNo = %s",(room[0],)) 
        courseBookingsWithNames = cur.fetchall()
        rooms.append(room + userBookingsWithNames + courseBookingsWithNames)
    cur.close()
    return jsonify(rooms), 200


# 11 get_rooms_with_number_of_bookings takes nothing 
# First get all rooms. For each room, do two different queries 
@app.route('/get_rooms_with_number_of_bookings', methods=['GET'])
def get_rooms_with_number_of_bookings_handler(): 
    return get_rooms_with_number_of_bookings() 
def get_rooms_with_number_of_bookings(): 
    cur = mysql.connection.cursor()
    query = "SELECT * FROM rooms"
    cur.execute(query)
    rooms = [] 
    for room in cur.fetchall(): 
        cur.execute("SELECT COUNT(*) FROM UserBooking WHERE roomNo = %s", (room[0],)) 
        numberOfUserBookings = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM CourseBooking WHERE roomNo = %s", (room[0],))  
        numberOfCourseBookings = cur.fetchone()[0]
        rooms.append(room + (numberOfUserBookings, numberOfCourseBookings))
    cur.close()
    return jsonify(rooms), 200 

# 12 get_rooms_with_number_of_bookings takes nothing 
# First get all rooms. For each room, do two different queries 
@app.route('/get_teachers_number_courses', methods=['GET'])
def get_teachers_number_courses_handler(): 
    return get_teachers_number_courses()   

def get_teachers_number_courses(): 
    cur = mysql.connection.cursor()
    query = "SELECT Teacher.userId, COUNT(course.userId) FROM Teacher LEFT JOIN course ON teacher.userId = course.userId GROUP BY teacher.userId ORDER BY COUNT(course.userId) DESC"
    cur.execute(query) 
    teachers = cur.fetchall()
    cur.close()
    return jsonify(teachers), 200


# 13 get_teachers_with_courses_and_course_locations takes nothing
@app.route('/get_teachers_with_courses_and_course_locations', methods=['GET'])
def get_teachers_with_courses_and_course_locations_handler(): 
    return get_teachers_with_courses_and_course_locations() 
def get_teachers_with_courses_and_course_locations(): 
    cur = mysql.connection.cursor()
    query = """SELECT Teacher.*, Course.*, CourseBooking.roomNo, building.Name
            FROM Teacher 
            LEFT JOIN Course ON Teacher.userId = Course.userId 
            LEFT JOIN CourseBooking ON Course.Id = CourseBooking.courseID
            LEFT JOIN rooms ON rooms.roomNo = CourseBooking.roomNo 
            LEFT JOIN building ON rooms.buildingId = building.Id; """
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
    query = "SELECT teacher.userId, WEEK(CourseBooking.Date), SUM(TIMEDIFF(CourseBooking.end_time, CourseBooking.start_time)) FROM Teacher LEFT JOIN Course ON Teacher.userId = Course.userId INNER JOIN CourseBooking ON Course.id = CourseBooking.courseId GROUP BY Teacher.userId, WEEK(CourseBooking.Date)"
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
    query = "SELECT Course.*, CONCAT(users.firstName, ' ', users.lastName), users.email FROM Course LEFT JOIN Users ON Course.userId = Users.Id INNER JOIN CourseBooking ON Course.id = CourseBooking.courseId WHERE DAYNAME(CourseBooking.Date) = 'Monday'"
    response = cur.execute(query)
    if response == 0:
        error_message = 'No teachers found'
        return jsonify({'error': error_message}), 404

    teachers = cur.fetchall()
    cur.close()
    return jsonify(teachers), 200


# 16 get_teachers_withaverage_numberstudents takes nothing, sorted by students
@app.route('/get_teachers_with_average_number_students', methods=['GET'])
def get_teachers_with_average_numberstudents_handler(): 
    return get_teachers_with_average_numberstudents()  

def get_teachers_with_average_numberstudents(): 
    cur = mysql.connection.cursor()
    query = "SELECT Course.userId, AVG(Course.studentCount) FROM Course ORDER BY AVG(Course.studentCount) DESC;"
    response = cur.execute(query)
    if response == 0:
        error_message = 'No teachers found'
        return jsonify({'error': error_message}), 404

    teachers = cur.fetchall()
    cur.close()
    return jsonify(teachers), 200 

if __name__ == '__main__':
    app.run(debug=True) 
