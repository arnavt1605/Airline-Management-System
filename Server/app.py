from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import time
import logging
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




#Add passenger details
@app.route('/add_passenger', methods=['GET', 'POST'])
def add_passenger():
    """
    Allows a passenger to add their details.
    """
    if 'user_id' not in session or session['user_type'] != 'passenger':
        return redirect(url_for('login'))

    conn = None
    if request.method == 'POST':
        try:
            passenger_id = request.form.get('passenger_id')
            passenger_name = request.form.get('passenger_name')
            age = request.form.get('age')
            gender = request.form.get('gender')
            address = request.form.get('address')
            contact_number = request.form.get('contact_number')
            email = request.form.get('email')

            if not all([passenger_id, passenger_name, age, gender, address, contact_number, email]):
                flash("All fields are required.", "danger")
                return render_template('add_passenger.html')

            try:
                passenger_id = int(passenger_id)
                age = int(age)
            except ValueError:
                flash("Invalid data format. Passenger ID and Age must be numbers.", "danger")
                return render_template('add_passenger.html')

            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO Passengers (Passenger_ID, Passenger_Name, Age, Gender, Address, Contact_Number, Email) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (passenger_id, passenger_name, age, gender, address, contact_number, email))
                    conn.commit()
                    cursor.close()
                    flash("Passenger details added successfully!", "success")
                    return redirect(url_for('passenger_dashboard'))  # Redirect to dashboard
                except Exception as db_error:
                    conn.rollback()
                    logging.error(f"Database error: {db_error}")
                    flash(f"Database error: {db_error}", "danger")
                    return render_template('add_passenger.html')
            else:
                flash("Database connection error", "danger")
                return render_template('add_passenger.html')
        except Exception as e:
            logging.error(f"Error adding passenger: {e}")
            flash(f"An error occurred: {e}", "danger")
            return render_template('add_passenger.html')
        finally:
            if conn:
                conn.close()
    return render_template('add_passenger.html')




#View Available flights
@app.route('/passenger/flights')
def view_available_flights():
    if 'user_id' not in session or session['user_type'] != 'passenger':
        return redirect(url_for('login'))

    conn = get_db_connection()
    flights = []
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    f.Flight_ID,
                    a1.Airport_Name AS Departure_City,
                    a2.Airport_Name AS Arrival_City,
                    f.Departure_Time,
                    f.Arrival_Time,
                    at.Manufacturer AS Airline
                FROM Flight f
                JOIN Route r ON f.Route_ID = r.Route_ID
                JOIN Airport a1 ON r.Origin_Airport_Code = a1.Airport_Code
                JOIN Airport a2 ON r.Destination_Airport_Code = a2.Airport_Code
                JOIN Airplane_type at ON f.Airplane_ID = at.Airplane_ID
            """)
            flights = cursor.fetchall()
        except Exception as e:
            logging.error(f"Database error: {e}")
            flash(f"Error fetching flights: {e}", "danger")
            flights = []
        finally:
            cursor.close()
            conn.close()
    return render_template('view_available_flights.html', flights=flights)



def get_available_flights():
    """Helper function to get available flights from the database."""
    conn = get_db_connection()
    flights = []
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    f.Flight_ID,
                    a1.Airport_Name AS Departure_City,
                    a2.Airport_Name AS Arrival_City,
                    f.Departure_Time,
                    f.Arrival_Time,
                    apt.Airline_Name
                FROM Flight f
                JOIN Route r ON f.Route_ID = r.Route_ID
                JOIN Airport a1 ON r.Origin_Airport_Code = a1.Airport_Code
                JOIN Airport a2 ON r.Destination_Airport_Code = a2.Airport_Code
                JOIN Airplane_type apt ON f.Airplane_ID = apt.Airplane_ID
            """)
            flights = cursor.fetchall()
        except Exception as e:
            logging.error(f"Database error: {e}")
            flash(f"Error fetching flights: {e}", "danger")
            flights = []
        finally:
            cursor.close()
            conn.close()
    return flights



# Update Flight Status
@app.route('/update_flight_status', methods=['GET', 'POST'])
def update_flight_status():
    """Allows staff to update flight status."""
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        return render_template('update_flight_status.html')

    cursor = conn.cursor()
    if request.method == 'POST':
        try:
            status_id = request.form.get('status_id')
            flight_id = request.form.get('flight_id')
            status = request.form.get('status')
            delay_reason = request.form.get('delay_reason')

            if not all([status_id, flight_id, status]):
                flash("Status ID, Flight ID, and Status are required.", "danger")
                return render_template('update_flight_status.html')

            # Insert or Update
            cursor.execute(
                """
                INSERT INTO Flight_Status (Status_ID, Flight_ID, Status, Delay_Reason) 
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                Flight_ID = %s, Status = %s, Delay_Reason = %s
                """,
                (status_id, flight_id, status, delay_reason, flight_id, status, delay_reason)
            )
            conn.commit()
            flash("Flight status updated successfully!", "success")
            cursor.close()
            conn.close()
            return redirect(url_for('update_flight_status'))

        except mysql.connector.Error as e:
            conn.rollback()
            logging.error(f"Database error updating flight status: {e}")
            flash(f"Database error: {e}", "danger")
            cursor.close()
            conn.close()
            return render_template('update_flight_status.html')
        finally:
            if conn:
                conn.close()
    else:
        return render_template('update_flight_status.html')
    



#Process payment
@app.route('/process_payment', methods=['GET', 'POST'])
def process_payment():
    """Processes the payment for a booking."""
    if 'booking_details' not in session:
        return redirect(url_for('passenger_dashboard'))  # Redirect if no booking details

    booking_details = session['booking_details']
    fare_details = session['fare_details']
    conn = None
    if request.method == 'POST':
        try:
            payment_method = request.form.get('payment_method')
            payment_status = request.form.get('payment_status')

            if not all([payment_method, payment_status]):
                flash("All payment fields are required", "danger")
                return render_template('process_payment.html', booking_details=booking_details)

            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                booking_date = datetime.now()
                # 1. Insert into Transactions
                cursor.execute(
                    "INSERT INTO Transactions (Transaction_ID, Booking_Date, Payment_Method, Payment_Status, Amount, Passenger_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                    (booking_details['transaction_id'], booking_date, payment_method, payment_status, booking_details['amount'], booking_details['passenger_id']))
                try:
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    flash(f"Transaction Error: {e}", "danger")
                    return render_template('process_payment.html', booking_details=booking_details)

                # 2. Insert into Booking
                cursor.execute(
                    "INSERT INTO Booking (Booking_Status, Seat_Number, Class_ID, Transaction_ID, Flight_ID, Passenger_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                    (booking_details['booking_status'], booking_details['seat_number'], booking_details['class_id'], booking_details['transaction_id'], booking_details['flight_id'], booking_details['passenger_id']))
                try:
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    flash(f"Booking Error: {e}", "danger")
                    return render_template('process_payment.html', booking_details=booking_details)
                cursor.close()
                conn.close()
                del session['booking_details']  # Clear booking details from session
                del session['fare_details']
                flash("Booking and payment successful!", "success")
                return redirect(url_for('passenger_dashboard'))
            else:
                flash("Database connection error", "danger")
                return render_template('process_payment.html', booking_details=booking_details)
        except Exception as e:
            logging.error(f"Error processing payment: {e}")
            flash(f"An error occurred: {e}", "danger")
            return render_template('process_payment.html', booking_details=booking_details)
        finally:
            if conn:
                conn.close()

    return render_template('process_payment.html', booking_details=booking_details,fare_details = fare_details)






# Update Airfare
@app.route('/update_airfare', methods=['GET', 'POST'])
def update_airfare():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            fare_id = request.form.get('fare_id')
            base_amount = request.form.get('base_amount')
            tax_amount = request.form.get('tax_amount')
            discount = request.form.get('discount')
            flight_id = request.form.get('flight_id')
            class_id = request.form.get('class_id')

            if not all([fare_id, base_amount, tax_amount, flight_id, class_id]):
                flash("All required fields must be filled.", "danger")
                return render_template('update_airfare.html')

            try:
                base_amount = float(base_amount)
                tax_amount = float(tax_amount)
                discount = float(discount) if discount else 0.00
                class_id = int(class_id)
            except ValueError:
                flash("Invalid data format for amount or class ID.", "danger")
                return render_template('update_airfare.html')

            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO AirFare (Fare_ID, Base_Amount, Tax_Amount, Discount, Flight_ID, Class_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                    (fare_id, base_amount, tax_amount, discount, flight_id, class_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                flash("Airfare information added successfully!", "success")
                return redirect(url_for('staff_dashboard'))
            else:
                flash("Database connection error.", "danger")
                return render_template('update_airfare.html')

        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Error updating airfare: {e}")
            flash(f"An error occurred: {e}", "danger")
            return render_template('update_airfare.html')

    return render_template('update_airfare.html')


#View Fare Classes
@app.route('/view_classes')
def view_classes():
    if session.get('user_type') == 'passenger':
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Class_ID, Class_Name, Description FROM Fare_Class")  # Updated SQL query
            fare_classes = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('view_classes.html', fare_classes=fare_classes)
        else:
            return "Database connection error"
    else:
        return redirect(url_for('login'))



# Flight Booking
@app.route('/book_flight', methods=['GET', 'POST'])
def book_flight():
    """
    Allows a passenger to book a flight, including seat selection and booking details.
    """
    if 'user_id' not in session or session['user_type'] != 'passenger':
        return redirect(url_for('login'))

    conn = None
    if request.method == 'POST':
        try:
            flight_id = request.form.get('flight_id')
            passenger_id = request.form.get('passenger_id')  # Get passenger_id from form
            class_id = request.form.get('class_id')
            seat_number = request.form.get('seat_number')
            booking_status = request.form.get('booking_status')
            transaction_id = request.form.get('transaction_id') #get transaction id

            if not all([flight_id, passenger_id, class_id, seat_number, booking_status, transaction_id]):
                flash("All booking fields are required", "danger")
                return render_template('book_flight.html')

            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()

                # 1. Get fare details (Base_Amount, Tax_Amount, Discount)
                cursor.execute(
                    "SELECT Base_Amount, Tax_Amount, Discount FROM AirFare WHERE Flight_ID = %s AND Class_ID = %s",
                    (flight_id, class_id))
                fare_data = cursor.fetchone()
                if not fare_data:
                    flash("Fare information not found for the selected flight and class.", "danger")
                    return render_template('book_flight.html')

                base_amount = fare_data[0]
                tax_amount = fare_data[1]
                discount_percentage = fare_data[2]

                # 2. Calculate the transaction amount
                amount = base_amount + tax_amount - (base_amount * discount_percentage / 100)

                # Store booking details and calculated amount in session for the payment page
                session['booking_details'] = {
                    'flight_id': flight_id,
                    'passenger_id': passenger_id,
                    'class_id': class_id,
                    'seat_number': seat_number,
                    'booking_status': booking_status,
                    'amount': amount,  # Store the calculated amount
                    'transaction_id': transaction_id, #store transaction id
                }
                session['fare_details'] = {
                    'base_amount':base_amount,
                    'tax_amount':tax_amount,
                    'discount_percentage':discount_percentage
                }

                conn.close()
                return redirect(url_for('process_payment'))  # Redirect to payment processing

            else:
                flash("Database connection error", "danger")
                return render_template('book_flight.html')
        except Exception as e:
            logging.error(f"Error booking flight: {e}")
            flash(f"An error occurred: {e}", "danger")
            return render_template('book_flight.html')
        finally:
            if conn:
                conn.close()
    else:
        return render_template('book_flight.html')



#Cancel booking
@app.route('/cancel_booking', methods=['GET', 'POST'])
def cancel_booking():
    if 'user_id' not in session or session.get('user_type') != 'passenger':
        flash("You must be logged in as a passenger to cancel a booking.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if request.method == 'POST':
            booking_id = request.form.get('booking_id')  # Get booking_id from the form

            if not booking_id:
                flash("Please enter the Booking ID.", "danger")
                return render_template('cancel_booking.html')  # Show the form again

            # Perform the cancellation in the database
            cursor.execute("UPDATE Booking SET Status = 'Cancelled' WHERE Booking_ID = %s AND Passenger_ID = %s",
                           (booking_id, session['user_id']))
            conn.commit()

            if cursor.rowcount > 0:
                flash("Your booking has been successfully cancelled.", "success")
            else:
                flash("Booking not found or you are not authorized to cancel it.", "danger")

            return redirect(url_for('passenger_dashboard'))

        else:  # GET request - Show the form to enter booking ID
            return render_template('cancel_booking.html')

    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('passenger_dashboard'))

    finally:
        cursor.close()
        conn.close()


# View Booked Flights
@app.route('/view_bookings')
def view_bookings():
    """Displays the passenger's bookings."""
    if 'user_id' not in session or session['user_type'] != 'passenger':
        return redirect(url_for('login'))
    passenger_id = session['user_id']
    conn = get_db_connection()
    bookings = []
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    b.Booking_ID,
                    f.Flight_ID,  -- Changed from f.Flight_Number to f.Flight_ID
                    a1.Airport_Name AS Departure_City,
                    a2.Airport_Name AS Arrival_City,
                    f.Departure_Time,
                    f.Arrival_Time,
                    b.Seat_Number,
                    fc.Class_Name,
                    t.Payment_Status
                FROM Booking b
                JOIN Flight f ON b.Flight_ID = f.Flight_ID
                JOIN Route r ON f.Route_ID = r.Route_ID
                JOIN Airport a1 ON r.Origin_Airport_Code = a1.Airport_Code
                JOIN Airport a2 ON r.Destination_Airport_Code = a2.Airport_Code
                JOIN Fare_Class fc ON b.Class_ID = fc.Class_ID
                JOIN Transactions t ON b.Transaction_ID = t.Transaction_ID
                WHERE b.Passenger_ID = %s
                """, (passenger_id,))
            bookings = cursor.fetchall()
        except Exception as e:
            logging.error(f"Database error: {e}")
            flash(f"Error fetching bookings: {e}", "danger")
            bookings = []
        finally:
            cursor.close()
            conn.close()
    return render_template('view_bookings.html', bookings=bookings)
    
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




# Flight Status Check
@app.route('/flight_status_result', methods=['GET', 'POST'])
def flight_status_result():
    """Displays the status of a flight based on the Flight ID entered by the passenger."""
    if 'user_id' not in session or session['user_type'] != 'passenger':
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        return render_template('flight_status_result.html', flight_status=None)

    cursor = conn.cursor()
    if request.method == 'POST':
        flight_id = request.form.get('flight_id')
        if not flight_id:
            flash("Please enter a Flight ID.", "danger")
            cursor.close()
            conn.close()
            return render_template('flight_status_result.html', flight_status=None)

        try:
            #  Get the status and delay reason
            cursor.execute("""
                SELECT
                    fs.Status,
                    fs.Delay_Reason
                FROM Flight_Status fs
                WHERE fs.Flight_ID = %s
                """, (flight_id,))
            flight_status = cursor.fetchone()  # Fetch one

            cursor.close()
            conn.close()
            if not flight_status:
                flash("Flight not found or status not available.", "info")
                return render_template('flight_status_result.html', flight_status=None)
            else:
                return render_template('flight_status_result.html', flight_status=flight_status)

        except Exception as e:
            logging.error(f"Error fetching flight status: {e}")
            flash(f"An error occurred: {e}", "danger")
            cursor.close()
            conn.close()
            return render_template('flight_status_result.html', flight_status=None)
    else:
        return render_template('flight_status_result.html', flight_status=None)
    




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




@app.route('/update_airplane_type', methods=['GET', 'POST'])  # Keep the same route name for simplicity
def update_airplane_type():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Get data from the form
            airplane_id = request.form.get('airplane_id')
            passenger_capacity = request.form.get('passenger_capacity')
            weight = request.form.get('weight')
            manufacturer = request.form.get('manufacturer')

            # Basic Validation (Add more as needed!)
            if not all([airplane_id, passenger_capacity, weight, manufacturer]):
                flash("All fields are required.", "danger")
                return render_template('update_airplane_type.html')

            # Convert passenger_capacity and weight to integers (if needed)
            try:
                passenger_capacity = int(passenger_capacity)
                weight = float(weight)  # Or int, depending on your table definition
            except ValueError:
                flash("Passenger Capacity and Weight must be numeric.", "danger")
                return render_template('update_airplane_type.html')

            # Database interaction (INSERT instead of UPDATE)
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Airplane_type (Airplane_ID, Passenger_Capacity, Weight, Manufacturer) VALUES (%s, %s, %s, %s)",
                    (airplane_id, passenger_capacity, weight, manufacturer)
                )
                conn.commit()
                cursor.close()
                conn.close()
                flash("Airplane type added successfully!", "success")
                return redirect(url_for('staff_dashboard'))  # Or wherever you want to redirect
            else:
                flash("Database connection error", "danger")
                return render_template('update_airplane_type.html')

        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Error adding airplane type: {e}")
            flash(f"An error occurred: {e}", "danger")
            return render_template('update_airplane_type.html')

    return render_template('update_airplane_type.html')




#Update Route 
@app.route('/update_route', methods=['GET', 'POST'])
def update_route():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    conn = None  
    if request.method == 'POST':
        try:
            route_id = request.form.get('route_id')
            origin_airport_code = request.form.get('origin_airport_code')
            destination_airport_code = request.form.get('destination_airport_code')
            distance = request.form.get('distance')
            duration_str = request.form.get('duration')

            if not all([route_id, origin_airport_code, destination_airport_code, distance, duration_str]):
                flash("All fields are required.", "danger")
                return render_template('update_route.html')

            try:
                route_id = int(route_id)
                distance = float(distance)
                duration = time.fromisoformat(duration_str)
            except ValueError:
                flash("Invalid data format.  Route ID and Distance must be numbers, Duration must be in HH:MM:SS or HH:MM format", "danger")
                return render_template('update_route.html')

            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO Route (Route_ID, Origin_Airport_Code, Destination_Airport_Code, Distance, Duration) VALUES (%s, %s, %s, %s, %s)",
                        (route_id, origin_airport_code, destination_airport_code, distance, duration))
                    conn.commit()
                    cursor.close()
                    flash("Route information updated successfully!", "success")
                    return redirect(url_for('staff_dashboard'))
                except Exception as db_error:
                    conn.rollback()
                    logging.error(f"Database error: {db_error}")
                    flash(f"Database error: {db_error}", "danger")
                    return render_template('update_route.html')
            else:
                flash("Database connection error", "danger")
                return render_template('update_route.html')

        except Exception as e:
            logging.error(f"Error updating route: {e}")
            flash(f"An error occurred: {e}", "danger")
            return render_template('update_route.html')
        finally:  # Ensure connection is closed
            if conn:
                conn.close()

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
        flight_id = request.form['flight_id']  # Get Flight_ID from form
        flight_number = request.form['flight_number']
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        flight_date = request.form['flight_date']
        airplane_id = request.form['airplane_id']
        route_id = request.form['route_id']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Flight (Flight_ID, Flight_Number, Departure_Time, Arrival_Time, Flight_Date, Airplane_ID, Route_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (flight_id, flight_number, departure_time, arrival_time, flight_date, airplane_id, route_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('staff_dashboard'))

            except Exception as e:
                conn.rollback()  # Crucial!
                print(f"Database Error: {e}")  # Log properly!
                return f"Database error: {e}"  # Simple error - improve!

        else:
            return "Database connection error"

    return render_template('add_flight.html')




#Remove Flight
@app.route('/remove_flight', methods=['GET', 'POST'])
def remove_flight():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    conn = None
    if request.method == 'POST':
        flight_id = request.form.get('flight_id')
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Flight WHERE Flight_ID = %s", (flight_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    flash("Flight removed successfully", "success")
                else:
                    flash("Flight not found", "info")
                cursor.close()
                return redirect(url_for('staff_dashboard'))
            else:
                flash("Database connection error", "danger")
                return render_template('remove_flight.html')
        except Exception as e:
            logging.error(f"Error removing flight: {e}")
            flash(f"An error occurred: {e}", "danger")
            return render_template('remove_flight.html')
        finally:
            if conn:
                conn.close()
    return render_template('remove_flight.html')













if __name__ == '__main__':
    app.run(debug=True)  