# Airline Management System

## Introduction

The Airline Management System is a web application designed to manage airline operations, including flight booking, status updates, and route management. It provides functionalities for both passengers and staff to streamline processes and improve efficiency.

## Features

* **Passenger:**

    * Flight Booking: Search for flights, select seats, and book tickets.
    * View Bookings: Manage and view existing flight bookings.
    * Check Flight Status: Check the current status of a flight (e.g., on-time, delayed, cancelled).
* **Staff:**

    * Manage Flights: Add, update, and remove flight schedules.
    * Manage Routes: Define and manage flight routes (origin and destination).
    * Update Flight Status: Update flight status and provide delay reasons.

## Technologies Used

* **Backend:** Python with Flask framework
    * Flask is a lightweight and flexible web framework for building web applications.
* **Database:** MySQL
    * MySQL is a relational database management system (RDBMS) used to store and manage the application's data.
* **Frontend:** HTML, CSS, Bootstrap
    * HTML is used for structuring the web pages.
    * CSS is used for styling the web pages.
    * Bootstrap is a CSS framework for creating responsive and visually appealing user interfaces.

## Database Schema

The system uses a MySQL database with the following tables:

* **Airplane\_type**:
    * Stores airplane type information
* **Airport**:
    * Stores airport details
* **Route**:
    * Stores flight route information
* **Flight**:
    * Stores flight details
* **Flight\_Status**:
    * Stores the status of a flight
* **Employee**:
    * Stores employee information
* **Passengers**:
    * Stores passenger information
* **Fare\_Class**:
    * Stores fare class information
* **AirFare**:
    * Stores airfare details
* **Transactions**:
     * Stores transaction details
* **Booking**:
    * Stores booking information
* **UserCredentials**:
    * Stores user credentials
        

## Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/your_username/your_repository_name.git](https://github.com/your_username/your_repository_name.git)
    cd your_repository_name
    ```

    * Replace `your_username` and `your_repository_name` with your actual GitHub username and repository name.
2.  **Set up a virtual environment (recommended):**

    * A virtual environment isolates project dependencies, preventing conflicts with other Python projects.

    ```bash
    python -m venv venv
    ```

    * Activate the virtual environment:
        * On Linux/macOS:

            ```bash
            source venv/bin/activate
            ```
        * On Windows:

            ```bash
            venv\Scripts\activate
            ```
3.  **Install packages:**

    * Install the required Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

    * This command installs all the packages listed in the `requirements.txt` file. This file should be included in the project repository and list dependencies like Flask and any database connectors.
4.  **Set up the MySQL database:**

    * Install MySQL server on your system.
    * Create a database for the project (e.g., `airline_management`):

        ```sql
        CREATE DATABASE airline_management;
        ```
    * Use a tool like `mysql` command-line client or a GUI tool like phpMyAdmin to create the database.
    * Create the tables defined in the [Database Schema](#database-schema) section. You can either execute SQL queries directly or import a SQL dump file if provided.
    * Ensure that the MySQL server is running and accessible.
5.  **Configure database connection:**

    * Open the `app.py` file.
    * Locate the database connection configuration section.
    * Update the `host`, `user`, `password`, and `database` values with your MySQL database credentials. For example:

        ```python
        conn = mysql.connector.connect(
            host="your_host",  # e.g., "localhost"
            user="your_user",  # e.g., "root"
            password="your_password",  # e.g., "your_password"
            database="airline_management"
        )
        ```
    * Set the `secret_key` in `app.py`. This key is used for session management and should be a long, random string:

        ```python
        app.secret_key = "your_secret_key"  # Replace with a strong, random string
        ```
6.  **Run the application:**

    ```bash
    python app.py
    ```

    * This command starts the Flask development server. The application will typically be accessible at `http://localhost:5000`.

## Usage

* **Access the application:** Open your web browser and navigate to `http://localhost:5000` (or the address where your application is running).
* **Login:**
    * The application provides separate login interfaces for passengers and staff.
    * Use the credentials created in the `UserCredentials` table to log in.
* **Passenger Dashboard:**
    * After logging in, passengers can access their dashboard to:
        * Search for and book flights.
        * View and manage their existing bookings.
        * Check the status of their flights.
* **Staff Dashboard:**
    * Staff users can access their dashboard to:
        * Manage flight schedules (add, update, remove).
        * Manage flight routes.
        * Update the status of flights.


## Thank you!
