CREATE DATABASE IF NOT EXISTS SmartGymDB;
USE SmartGymDB;

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role ENUM('Admin', 'Trainer') NOT NULL
);

CREATE TABLE Membership_Plans (
    PlanID INT AUTO_INCREMENT PRIMARY KEY,
    PlanName VARCHAR(50) NOT NULL,
    Cost DECIMAL(10, 2) NOT NULL,
    DurationDays INT NOT NULL
);

CREATE TABLE Members (
    MemberID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(15) NOT NULL,
    JoinDate DATE NOT NULL,
    PlanID INT,
    Status ENUM('Active', 'Expired', 'Cancelled') DEFAULT 'Active',
    FOREIGN KEY (PlanID) REFERENCES Membership_Plans(PlanID) ON DELETE SET NULL
);

CREATE TABLE Trainers (
    TrainerID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Specialization VARCHAR(100),
    Phone VARCHAR(15) NOT NULL
);

CREATE TABLE Classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    ClassName VARCHAR(100) NOT NULL,
    TrainerID INT,
    ScheduleTime DATETIME NOT NULL,
    Capacity INT NOT NULL,
    CurrentEnrolled INT DEFAULT 0,
    FOREIGN KEY (TrainerID) REFERENCES Trainers(TrainerID) ON DELETE SET NULL
);

CREATE TABLE Class_Bookings (
    BookingID INT AUTO_INCREMENT PRIMARY KEY,
    MemberID INT NOT NULL,
    ClassID INT NOT NULL,
    BookingDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID) ON DELETE CASCADE,
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID) ON DELETE CASCADE
);

CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    MemberID INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentDate DATE NOT NULL,
    PaymentMethod VARCHAR(50),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID) ON DELETE CASCADE
);

CREATE TABLE Attendance (
    AttendanceID INT AUTO_INCREMENT PRIMARY KEY,
    MemberID INT NOT NULL,
    CheckInTime DATETIME NOT NULL,
    CheckOutTime DATETIME,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID) ON DELETE CASCADE
);

INSERT INTO Users (Username, PasswordHash, Role) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Admin');

INSERT INTO Membership_Plans (PlanName, Cost, DurationDays) VALUES 
('Basic Monthly', 50.00, 30),
('Premium Monthly', 80.00, 30),
('Annual Pass', 500.00, 365);