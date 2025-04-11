-- Create database
CREATE DATABASE airline_management;
USE airline_management;

-- Create Airplane_type table
CREATE TABLE Airplane_type (
    Airplane_ID VARCHAR(10) PRIMARY KEY,
    Passenger_Capacity INT NOT NULL,
    Weight FLOAT NOT NULL,
    Manufacturer VARCHAR(50) NOT NULL
);

-- Create Airport table
CREATE TABLE Airport (
    Airport_Code VARCHAR(5) PRIMARY KEY,
    Airport_Name VARCHAR(100) NOT NULL,
    City VARCHAR(50) NOT NULL,
    Country VARCHAR(50) NOT NULL,
    State VARCHAR(50)
);

-- Create Route table
CREATE TABLE Route (
    Route_ID INT PRIMARY KEY,
    Origin_Airport_Code VARCHAR(5) NOT NULL,
    Destination_Airport_Code VARCHAR(5) NOT NULL,
    Distance FLOAT NOT NULL,
    Duration TIME NOT NULL,
    FOREIGN KEY (Origin_Airport_Code) REFERENCES Airport(Airport_Code),
    FOREIGN KEY (Destination_Airport_Code) REFERENCES Airport(Airport_Code)
);

-- Create Flight table
CREATE TABLE Flight (
    Flight_ID VARCHAR(15) PRIMARY KEY,                
    Flight_Number VARCHAR(10) NOT NULL,
    Departure_Time TIME NOT NULL,
    Arrival_Time TIME NOT NULL,
    Flight_Date DATE NOT NULL,
    Airplane_ID VARCHAR(10) NOT NULL,
    Route_ID INT NOT NULL,
    FOREIGN KEY (Airplane_ID) REFERENCES Airplane_type(Airplane_ID),
    FOREIGN KEY (Route_ID) REFERENCES Route(Route_ID)
);

-- Create Flight_Status table
CREATE TABLE Flight_Status (
    Status_ID INT AUTO_INCREMENT PRIMARY KEY,
    Flight_ID VARCHAR(15) NOT NULL,              --
    Status VARCHAR(20) NOT NULL,
    Status_Update_Time DATETIME NOT NULL,
    Delay_Reason VARCHAR(200),
    FOREIGN KEY (Flight_ID) REFERENCES Flight(Flight_ID)
);

-- Create Employee table
CREATE TABLE Employee (
    Employee_ID INT AUTO_INCREMENT PRIMARY KEY,
    Employee_Name VARCHAR(100) NOT NULL,
    Airport_Code VARCHAR(5) NOT NULL,  --
    Contact_Number VARCHAR(15) NOT NULL,
    Email_Address VARCHAR(100) NOT NULL,
    FOREIGN KEY (Airport_Code) REFERENCES Airport(Airport_Code)
);

-- Create Passengers table
CREATE TABLE Passengers (
    Passenger_ID INT AUTO_INCREMENT PRIMARY KEY,
    Passenger_Name VARCHAR(100) NOT NULL,
    Age INT NOT NULL,
    Gender VARCHAR(10) NOT NULL,
    Address VARCHAR(200) NOT NULL,
    Contact_Number VARCHAR(15) NOT NULL,
    Email VARCHAR(100) NOT NULL
);

-- Create Fare_Class table
CREATE TABLE Fare_Class (
    Class_ID INT AUTO_INCREMENT PRIMARY KEY,
    Class_Name VARCHAR(20) NOT NULL,
    Description VARCHAR(200)
);

-- Create AirFare table
CREATE TABLE AirFare (
    Fare_ID INT AUTO_INCREMENT PRIMARY KEY,
    Base_Amount DECIMAL(10, 2) NOT NULL,
    Tax_Amount DECIMAL(10, 2) NOT NULL,
    Discount DECIMAL(10, 2) DEFAULT 0,
    Flight_ID VARCHAR(15) NOT NULL,         --
    Class_ID INT NOT NULL,
    FOREIGN KEY (Flight_ID) REFERENCES Flight(Flight_ID),
    FOREIGN KEY (Class_ID) REFERENCES Fare_Class(Class_ID)
);

-- Create Transactions table
CREATE TABLE Transactions (
    Transaction_ID INT AUTO_INCREMENT PRIMARY KEY,
    Booking_Date DATETIME NOT NULL,
    Payment_Method VARCHAR(50) NOT NULL,
    Payment_Status VARCHAR(20) NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Passenger_ID INT NOT NULL,
    FOREIGN KEY (Passenger_ID) REFERENCES Passengers(Passenger_ID)
);

-- Create Booking table
CREATE TABLE Booking (
    Booking_ID INT AUTO_INCREMENT PRIMARY KEY,
    Booking_Status VARCHAR(20) NOT NULL,
    Seat_Number VARCHAR(5) NOT NULL,
    Class_ID INT NOT NULL,
    Transaction_ID INT NOT NULL,
    Flight_ID VARCHAR(15) NOT NULL,    --
    Passenger_ID INT NOT NULL,
    FOREIGN KEY (Class_ID) REFERENCES Fare_Class(Class_ID),
    FOREIGN KEY (Transaction_ID) REFERENCES Transactions(Transaction_ID),
    FOREIGN KEY (Flight_ID) REFERENCES Flight(Flight_ID),
    FOREIGN KEY (Passenger_ID) REFERENCES Passengers(Passenger_ID)
);

CREATE TABLE UserCredentials (
    Email VARCHAR(255) PRIMARY KEY,
    Password VARCHAR(255) NOT NULL,
    User_Type VARCHAR(50) NOT NULL
);