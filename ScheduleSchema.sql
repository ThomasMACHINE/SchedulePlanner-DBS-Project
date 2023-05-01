-- Table structure for table `course`
CREATE TABLE Course (
    id int(5) NOT NULL,
    name varchar(255) NOT NULL,
    studentCount int(11) DEFAULT NULL,
    userId int(11) NOT NULL,

    CONSTRAINT pk_Course 
    PRIMARY KEY (id)
);

-- Table structure for table `CourseBooking`
CREATE TABLE `CourseBooking` (
    roomNo varchar(4) NOT NULL,
    StartDate datetime NOT NULL,
    end_Time datetime NOT NULL,
    description varchar(255) DEFAULT NULL,
    courseId int(11) NOT NULL,

    CONSTRAINT pk_CourseBooking 
    PRIMARY KEY (roomNo, StartDate),

    CONSTRAINT fk_CourseBooking_courseId 
    FOREIGN KEY (courseId) 
    REFERENCES Course (id)
);

-- Table structure for table `Rooms`
CREATE TABLE `Rooms` (
    roomNo varchar(4) NOT NULL,
    type varchar(255) DEFAULT NULL,
    size int(11) NOT NULL,
    floorLevel int(11) DEFAULT NULL,

    CONSTRAINT pk_Rooms 
    PRIMARY KEY (roomNo)
);

-- Table structure for table `UserType`
CREATE TABLE UserType (
    UserType int(2) NOT NULL,
    viewAccess tinyint(1) DEFAULT NULL,
    bookingAccess tinyint(1) DEFAULT NULL,
    editAccess tinyint(1) DEFAULT NULL,
    contactAccess tinyint(1) DEFAULT NULL,

    CONSTRAINT pk_UserType 
    PRIMARY KEY (UserType)
);

-- Table structure for table `Users`
CREATE TABLE Users (
    Id int(11) NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255) NOT NULL,
    UserType int(11) DEFAULT NULL,
    StudentFlag tinyint(1) DEFAULT NULL,
    TeacherFlag tinyint(1) DEFAULT NULL,
    AdminFlag tinyint(1) DEFAULT NULL,
    Institute varchar(255) DEFAULT NULL,
    Phone int(11) DEFAULT NULL,
    Office varchar(5) DEFAULT NULL,
    Email varchar(255) DEFAULT NULL,
    Title varchar(255) DEFAULT NULL,
    Location varchar(255) DEFAULT NULL,

    CONSTRAINT pk_Users 
    PRIMARY KEY (Id),

    CONSTRAINT fk_UserType_userType
    FOREIGN KEY (UserType)
    REFERENCES userType (UserType)
);


-- Table structure for table `Schedules`
CREATE TABLE Schedules (
    id int(11) NOT NULL,
    userId int(11) DEFAULT NULL,

    CONSTRAINT pk_Schedules 
    PRIMARY KEY (id),

    CONSTRAINT fk_UserSchedule_userId
    FOREIGN KEY (userId)
    REFERENCES Users (id)
);

-- Table structure for table `SubSchedule`
CREATE TABLE SubSchedule (
    scheduleId int(11) NOT NULL,
    courseId int(11) NOT NULL,

    CONSTRAINT pk_SubSchedule 
    PRIMARY KEY (scheduleId, courseId),

    CONSTRAINT fk_SubSchedule_scheduleId 
    FOREIGN KEY (scheduleId) 
    REFERENCES Schedules (id),

    CONSTRAINT fk_SubSchedule_courseId 
    FOREIGN KEY (courseId) 
    REFERENCES Course (id)
);

-- Table structure for table `UserBooking`
CREATE TABLE UserBooking (
    roomNo varchar(4) NOT NULL,
    StartDate datetime NOT NULL,
    end_Time datetime NOT NULL,
    description varchar(255) DEFAULT NULL,
    userId int(11) NOT NULL,

    CONSTRAINT pk_UserBooking 
    PRIMARY KEY (roomNo, StartDate),

    CONSTRAINT fk_UserBooking_userId 
    FOREIGN KEY (userId) 
    REFERENCES Users (Id),

    CONSTRAINT fk_UserBooking_roomNo 
    FOREIGN KEY (roomNo) 
    REFERENCES Rooms (roomNo)
);