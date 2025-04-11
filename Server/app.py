from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "AIRLINE@#$567"  #Sessions Key

# Database Connection
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Arnav@sql123",
    "database": "airline_management"
}

# Function to connect to the database
def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None
    
#@app.route('/')
#def hi():
 #   return "Welcome"

#Checking whether Database is connected or not
#@app.route('/', methods=['GET', 'POST'])
@app.route('/test_db_connection')
def test_db_connection():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # A simple test query
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return "Database connection successful! Result: " + str(result)
    else:
        return "Database connection error"



#Login route
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error variable
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Email, Password, User_Type FROM UserCredentials WHERE Email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                stored_email, stored_password, user_type = user  # Unpack the tuple

                if stored_password == password: 
                    session['user_id'] = stored_email
                    session['user_type'] = user_type

                    if user_type == 'passenger':
                        return redirect(url_for('passenger_dashboard'))
                    elif user_type == 'staff':
                        return redirect(url_for('staff_dashboard'))
                    else:
                        error = 'Invalid user type.'
                else:
                    error = 'Invalid email or password.'
            else:
                error = 'Invalid email or password.'

    return render_template('login.html', error=error)

#Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles user signup."""

    if request.method == 'POST':
        email = request.form.get('email')  
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        # 1. Input Validation 
        if not email or not password or not user_type:
            return render_template('signup.html', error="All fields are required.")

        if user_type not in ('passenger', 'staff'):
            return render_template('signup.html', error="Invalid user type.")


        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # 2. Execute the Query
                cursor.execute("INSERT INTO UserCredentials (Email, Password, User_Type) VALUES (%s, %s, %s)",
                               (email, password, user_type))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('login'))  # Successful signup

            except mysql.connector.Error as e:
                conn.rollback()
                cursor.close()
                print(f"Signup error: {e}")
                return render_template('signup.html', error=f"Signup failed: {e}")  # Database error
            finally:
                # Ensure connection is closed even if no exception
                if conn.is_connected():
                    conn.close()

        else:
            return render_template('signup.html', error="Database connection failed.")  # No connection

    return render_template('signup.html')  # Handle GET requests

#Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('login'))

#Staff Dashboard
@app.route('/staff_dashboard')
def staff_dashboard():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    return render_template('staff_dashboard.html')


#Passenger Dashboard
@app.route('/passenger_dashboard')
def passenger_dashboard():
    if session.get('user_type') != 'passenger':
        return redirect(url_for('login'))
    return render_template('passenger_dashboard.html')

#View Available flights
@app.route('/passenger/flights')
def view_available_flights():
    if 'user_id' not in session or session['user_type'] != 'passenger':
        return redirect(url_for('login')) # Redirect if not logged in as passenger

    conn = get_db_connection()
    flights = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Flight") # Fetch all rows from the Flight table
        flights = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('view_available_flights.html', flights=flights)

# Update Flight Status
@app.route('/update_flight_status', methods=['GET', 'POST'])
def update_flight_status():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        status = request.form['status']
        delay_reason = request.form['delay_reason']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Flight_Status SET Status = %s, Delay_Reason = %s WHERE Flight_ID = %s",
                (status, delay_reason, flight_id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('staff_dashboard'))
        else:
            return "Database connection error"
    return render_template('update_flight_status.html')


# Update Airfare
@app.route('/update_airfare', methods=['GET', 'POST'])
def update_airfare():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        fare_id = request.form['fare_id']
        base_amount = request.form['base_amount']
        discount = request.form['discount']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE AirFare SET Base_Amount = %s, Discount = %s WHERE Fare_ID = %s",
                (base_amount, discount, fare_id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('staff_dashboard'))
        else:
            return "Database connection error"
    return render_template('update_airfare.html')


# Flight Booking
@app.route('/book_flight', methods=['GET', 'POST'])
def book_flight():
    if session.get('user_type') != 'passenger':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    error = None
    flights = []
    fare_classes = []

    try:
        # Fetch available flights with origin and destination
        cursor.execute("""
            SELECT f.Flight_ID, r.Origin_Airport_Code, r.Destination_Airport_Code, f.Departure_Time
            FROM Flight f
            JOIN Route r ON f.Route_ID = r.Route_ID
        """)
        flights = cursor.fetchall()

        # Fetch available fare classes
        cursor.execute("SELECT Class_ID, Class_Name, Description FROM Fare_Class")
        fare_classes = cursor.fetchall()

    except Exception as e:
        error = f"Error fetching data: {e}"

    if request.method == 'POST':
        flight_id = request.form.get('flight_id')
        class_id = request.form.get('class_id')
        seat_number = request.form.get('seat_number')
        passenger_id = session['user_id']

        if not all([flight_id, class_id, seat_number]):
            error = "Please select a flight, class, and seat number."
        else:
            try:
                # Get the maximum capacity for the selected flight
                cursor.execute("""
                    SELECT ap.Passenger_Capacity
                    FROM Flight f
                    JOIN Airplane ap ON f.Airplane_ID = ap.Airplane_ID
                    WHERE f.Flight_ID = %s
                """, (flight_id,))
                capacity_result = cursor.fetchone()

                # Count existing bookings for this flight
                cursor.execute("SELECT COUNT(*) FROM Booking WHERE Flight_ID = %s", (flight_id,))
                booking_count_result = cursor.fetchone()

                if capacity_result and booking_count_result:
                    max_capacity = capacity_result[0]
                    current_bookings = booking_count_result[0]

                    if current_bookings >= max_capacity:
                        error = f"Flight ID {flight_id} is fully booked. No seats remaining."
                    else:
                        # Check if the selected seat is already booked for this flight and class
                        cursor.execute("""
                            SELECT Booking_ID FROM Booking
                            WHERE Flight_ID = %s AND Seat_Number = %s AND Class_ID = %s
                        """, (flight_id, seat_number, class_id))
                        existing_booking = cursor.fetchone()

                        if existing_booking:
                            error = f"Seat number {seat_number} in class {class_id} is already booked on Flight ID {flight_id}."
                        else:
                            # Create a transaction
                            cursor.execute(
                                "INSERT INTO Transactions (Booking_Date, Payment_Method, Payment_Status, Amount, Passenger_ID) VALUES (CURDATE(), 'Not Applicable', 'Pending', 0, %s)",
                                (passenger_id,))
                            transaction_id = cursor.lastrowid

                            # Fetch booking details for display
                            cursor.execute(
                                "SELECT f.Flight_Number, f.Departure_Time, f.Arrival_Time, f.Flight_Date, fc.Class_Name, p.Passenger_Name, af.Base_Amount + af.Tax_Amount - af.Discount AS Total_Amount "
                                "FROM Flight f "
                                "JOIN Fare_Class fc ON %s = fc.Class_ID "
                                "JOIN Passengers p ON %s = p.Passenger_ID "
                                "JOIN AirFare af ON f.Flight_ID = af.Flight_ID AND fc.Class_ID = af.Class_ID "
                                "WHERE f.Flight_ID = %s",
                                (class_id, passenger_id, flight_id)
                            )
                            booking_details = cursor.fetchone()

                            if booking_details:
                                # Insert the booking
                                cursor.execute(
                                    "INSERT INTO Booking (Booking_Status, Seat_Number, Class_ID, Transaction_ID, Flight_ID, Passenger_ID) VALUES ('Confirmed', %s, %s, %s, %s, %s)",
                                    (seat_number, class_id, transaction_id, flight_id, passenger_id)
                                )
                                conn.commit()
                                cursor.close()
                                conn.close()
                                return render_template('booking_confirmation.html',
                                                       passenger_name=booking_details[5],
                                                       flight_number=booking_details[0],
                                                       departure_time=booking_details[1],
                                                       arrival_time=booking_details[2],
                                                       flight_date=booking_details[3],
                                                       class_name=booking_details[4],
                                                       seat_number=seat_number,
                                                       total_amount=booking_details[6],
                                                       flight_id=flight_id,
                                                       class_id=class_id,
                                                       transaction_id=transaction_id)
                            else:
                                error = "Error fetching booking details."
                else:
                    error = "Error retrieving flight capacity or booking count."

            except Exception as e:
                conn.rollback()
                error = f"Error during booking process: {e}"
            finally:
                cursor.close()
                conn.close()

    return render_template('book_flight.html', flights=flights, fare_classes=fare_classes, error=error)

# View Booked Flights
@app.route('/my_bookings')
def my_bookings():
    if session.get('user_type') != 'passenger':
        return redirect(url_for('login'))
    passenger_id = session['user_id']
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT b.*, f.Flight_Number, f.Flight_Date, r.Origin_Airport_Code, r.Destination_Airport_Code FROM Booking b JOIN Flight f ON b.Flight_ID = f.Flight_ID JOIN Route r ON f.Route_ID = r.Route_ID WHERE b.Passenger_ID = %s",
            (passenger_id,))
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('my_bookings.html', bookings=bookings)
    else:
        return "Database connection error"
    
# Booking Confirmation
@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    flight_id = request.form['flight_id']
    class_id = request.form['class_id']
    seat_number = request.form['seat_number']
    transaction_id = request.form['transaction_id']
    passenger_id = session['user_id']

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()

        # Create the booking
        cursor.execute(
            "INSERT INTO Booking (Booking_Status, Seat_Number, Class_ID, Transaction_ID, Flight_ID, Passenger_ID) VALUES ('Confirmed', %s, %s, %s, %s, %s)",
            (seat_number, class_id, transaction_id, flight_id, passenger_id))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('passenger_dashboard'))
    else:
        return "Database connection error"



# Cancel Flight
@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    if session.get('user_type') != 'passenger':
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Booking SET Booking_Status = 'Cancelled' WHERE Booking_ID = %s",
                       (booking_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('my_bookings'))
    else:
        return "Database connection error"
    

# Flight Status Check
@app.route('/flight_status', methods=['GET', 'POST'])
def flight_status():
    if session.get('user_type') != 'passenger':
        return redirect(url_for('login'))
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT fs.*, f.Flight_Number FROM Flight_Status fs JOIN Flight f ON fs.Flight_ID = f.Flight_ID WHERE f.Flight_Number = %s",
                (flight_number,))
            status = cursor.fetchone()
            if status:
                # Convert the result to a dictionary for easier handling in the template
                status = {
                    'Flight_Number': status[1],
                    'Status': status[2],
                    'Status_Update_Time': status[3],
                    'Delay_Reason': status[4]
                }
            cursor.close()
            conn.close()
            return render_template('flight_status_result.html', status=status)
        else:
            return "Database connection error"
    return render_template('flight_status.html')


# Employee Information for Grievances
@app.route('/employee_info_passenger')
def employee_info_passenger():
    if session.get('user_type') != 'passenger':
        return redirect(url_for('login'))

    conn = get_db_connection()
    employees = []
    error = None

    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT e.Employee_ID, e.Employee_Name, a.Airport_Name, e.Contact_Number, e.Email_Address "
                           "FROM Employee e LEFT JOIN Airport a ON e.Airport_Code = a.Airport_Code")
            employees = cursor.fetchall()
        except Exception as e:
            error = f"Error fetching employee info: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template('employee_info.html', employees=employees, error=error)




#Update Airplane type
@app.route('/update_airplane_type', methods=['GET', 'POST'])
def update_airplane_type():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        airplane_id = request.form['airplane_id']
        passenger_capacity = request.form['passenger_capacity']
        manufacturer = request.form['manufacturer']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Airplane_type SET Passenger_Capacity = %s, Manufacturer = %s WHERE Airplane_ID = %s",
                (passenger_capacity, manufacturer, airplane_id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('staff_dashboard'))
        else:
            return "Database connection error"
    return render_template('update_airplane_type.html')


#Update Route 
@app.route('/update_route', methods=['GET', 'POST'])
def update_route():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        route_id = request.form['route_id']
        origin_airport_code = request.form['origin_airport_code']
        destination_airport_code = request.form['destination_airport_code']
        distance = request.form['distance']
        duration = request.form['duration']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Route SET Origin_Airport_Code = %s, Destination_Airport_Code = %s, Distance = %s, Duration = %s WHERE Route_ID = %s",
                (origin_airport_code, destination_airport_code, distance, duration, route_id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('staff_dashboard'))
        else:
            return "Database connection error"
    return render_template('update_route.html')



#Update Employee Route  OR MANAGE EMPLOYEE
@app.route('/manage_employee')
def manage_employee():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))

    conn = get_db_connection()
    employees = []
    airports = []
    error = request.args.get('error')  # Get error from redirect
    success_message = request.args.get('success_message') # Get success message from redirect

    if conn:
        cursor = conn.cursor()
        try:
            # Fetch all employees to display
            cursor.execute("SELECT e.Employee_ID, e.Employee_Name, a.Airport_Name, e.Contact_Number, e.Email_Address "
                           "FROM Employee e LEFT JOIN Airport a ON e.Airport_Code = a.Airport_Code")
            employees = cursor.fetchall()

            # Fetch all airports for the add employee form
            cursor.execute("SELECT Airport_Code, Airport_Name FROM Airport")
            airports = cursor.fetchall()

        except Exception as e:
            error = f"Error fetching data: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template('manage_employee.html', employees=employees, airports=airports, error=error, success_message=success_message)

@app.route('/manage_employee_action', methods=['POST'])
def manage_employee_action():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))

    conn = get_db_connection()
    error = None
    success_message = None

    if conn:
        cursor = conn.cursor()
        try:
            action = request.form.get('action')

            if action == 'add':
                name = request.form.get('employee_name')
                airport_code = request.form.get('airport_code')
                contact = request.form.get('contact_number')
                email = request.form.get('email_address')

                if all([name, airport_code, contact, email]):
                    cursor.execute("INSERT INTO Employee (Employee_Name, Airport_Code, Contact_Number, Email_Address) VALUES (%s, %s, %s, %s)",
                                   (name, airport_code, contact, email))
                    conn.commit()
                    success_message = f"Employee '{name}' added successfully."
                else:
                    error = "Please fill in all fields to add a new employee."

            elif action == 'delete':
                employee_id_to_delete = request.form.get('delete_employee_id')
                if employee_id_to_delete:
                    cursor.execute("DELETE FROM Employee WHERE Employee_ID = %s", (employee_id_to_delete,))
                    conn.commit()
                    success_message = f"Employee with ID {employee_id_to_delete} deleted successfully."
                else:
                    error = "Please select an employee to delete."

        except Exception as e:
            conn.rollback()
            error = f"Error: {e}"
        finally:
            cursor.close()
            conn.close()

    # Redirect back to the manage_employee page to see the updated list and messages
    return redirect(url_for('manage_employee', error=error, success_message=success_message))












#Add a flight
@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        flight_date = request.form['flight_date']
        airplane_id = request.form['airplane_id']
        route_id = request.form['route_id']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Flight (Flight_Number, Departure_Time, Arrival_Time, Flight_Date, Airplane_ID, Route_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                (flight_number, departure_time, arrival_time, flight_date, airplane_id, route_id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('staff_dashboard'))
        else:
            return "Database connection error"
    return render_template('add_flight.html')


#Remove Flight
@app.route('/remove_flight', methods=['GET', 'POST'])
def remove_flight():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Flight WHERE Flight_ID = %s", (flight_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('staff_dashboard'))
        else:
            return "Database connection error"
    return render_template('remove_flight.html')












if __name__ == '__main__':
    app.run(debug=True)  