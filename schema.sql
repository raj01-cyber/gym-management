DROP DATABASE IF EXISTS SmartGymDB;
CREATE DATABASE SmartGymDB;
USE SmartGymDB;

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(64) NOT NULL,
    Role ENUM('Admin', 'Trainer') NOT NULL,
    INDEX idx_user (Username)
);

CREATE TABLE Membership_Plans (
    PlanID INT AUTO_INCREMENT PRIMARY KEY,
    PlanName VARCHAR(50) NOT NULL UNIQUE,
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
    PlanID INT NOT NULL,
    Status ENUM('Active', 'Expired', 'Cancelled') DEFAULT 'Active',
    FOREIGN KEY (PlanID) REFERENCES Membership_Plans(PlanID) ON DELETE RESTRICT,
    INDEX idx_member_email (Email)
) AUTO_INCREMENT = 2001;

CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    MemberID INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentDate DATE NOT NULL,
    PaymentMethod VARCHAR(50) NOT NULL,
    CoveredMonth VARCHAR(20) NOT NULL,
    BillingPeriod VARCHAR(30) NOT NULL, 
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID) ON DELETE RESTRICT
);

INSERT INTO Membership_Plans (PlanName, Cost, DurationDays) VALUES 
('Basic Monthly', 50.00, 30), 
('Premium Monthly', 80.00, 30), 
('Annual Pass', 500.00, 365);

CREATE TABLE Classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    ClassName VARCHAR(50) NOT NULL,
    ScheduleTime DATETIME NOT NULL,
    Capacity INT NOT NULL
);

CREATE TABLE Class_Bookings (
    BookingID INT AUTO_INCREMENT PRIMARY KEY,
    ClassID INT NOT NULL,
    MemberID INT NOT NULL,
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID) ON DELETE CASCADE,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID) ON DELETE CASCADE
);

CREATE TABLE Attendance (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    MemberID INT NOT NULL,
    CheckInTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID) ON DELETE CASCADE
);

INSERT INTO Classes (ClassName, ScheduleTime, Capacity) VALUES 
('Morning Yoga', '2026-05-25 08:00:00', 15), 
('HIIT Extreme', '2026-05-25 17:30:00', 20),
('Powerlifting 101', '2026-05-26 18:00:00', 10);