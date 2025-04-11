use airline_management;

-- Add a staff user
INSERT INTO Employee (Employee_Name, Email_Address, Airline, Contact_Number) VALUES
('Ravi Prakash', 'ravi@airindia.com', 'Air India', '123-456-7890');

-- Add a passenger
INSERT INTO Passengers (Passenger_Name, Email, Age, Gender, Address, Contact_Number) VALUES
('Arnav Tripathi', 'arnavtripathi@gmail.com', 30, 'Male', 'Plot 23, Mohan Bagh, Pune', '987-654-3210');

INSERT INTO Fare_Class (Class_Name, Description) VALUES
('Economy', 'Basic seating with standard amenities'),
('Business', 'More spacious seating, better meals, and priority boarding'),
('First Class', 'Luxury seating, premium service, and exclusive amenities');

-- First, make sure you have data in Airplane_type and Route
-- Example Airplane_type data (if you don't have it already):
INSERT INTO Airplane_type (Airplane_ID, Passenger_Capacity, Manufacturer) VALUES
('B737', 150, 'Boeing'),
('A320', 180, 'Airbus');

-- Example Route data (if you don't have it already):
INSERT INTO Route (Origin_Airport_Code, Destination_Airport_Code, Distance, Duration) VALUES
('JFK', 'LAX', 2475, '5h 30m'),
('LHR', 'CDG', 214, '1h 15m');

-- Now you can insert Flight data
INSERT INTO Flight (Flight_Number, Departure_Time, Arrival_Time, Flight_Date, Airplane_ID, Route_ID) VALUES
('AI123', '08:00:00', '13:00:00', '2025-04-05', 'B737', 1), -- Assuming Route_ID 1 and Airplane_ID 'B737' exist
('BA456', '10:00:00', '11:15:00', '2025-04-05', 'A320', 2); -- Assuming Route_ID 2 and Airplane_ID 'A320' exist