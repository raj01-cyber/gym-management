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
);

CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    MemberID INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentDate DATE NOT NULL,
    PaymentMethod VARCHAR(50) NOT NULL,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID) ON DELETE RESTRICT
);

INSERT INTO Membership_Plans (PlanName, Cost, DurationDays) VALUES 
('Basic Monthly', 50.00, 30), 
('Premium Monthly', 80.00, 30), 
('Annual Pass', 500.00, 365);