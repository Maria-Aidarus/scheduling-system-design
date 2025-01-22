# Collaborative Scheduling System

This project is a collaborative scheduling system that allows tutors to manage their availability and students to book time slots with them. The system is designed with functionality for time zone conversion, conflict management, notifications, and comprehensive CRUD operations for tutors, students, bookings, and availability.

 

## Features

### Tutor Availability Management
- Tutors can set recurring or one-time availability.
- Availability includes time slots with support for time zones.
- Prevents overlapping or double-booked slots.

### Student Booking
- Students can view tutor availability by subject and book time slots.
- Automatically converts tutor availability to the student's time zone.

### Conflict Management
- Ensures no overlapping bookings or conflicting availability slots.

### Notifications
- Logs and sends notifications for booking confirmations and availability updates.

### Comprehensive CRUD Operations
The project supports all CRUD operations for:
1. **Tutors**
2. **Students**
3. **Bookings**
4. **Availability**


## Technologies Used

- **Backend Framework:** Flask
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Time Zone Management:** `pytz`
- **Frontend Templates:** Jinja2 (HTML/CSS)
- **Testing:** Manual end-to-end testing using local server.



## API Overview

This project includes a set of RESTful APIs to manage the system. These APIs cover the following operations:

- **Booking APIs:** Create, update, delete, and fetch bookings for students and tutors.
- **Availability APIs:** Add, update, delete, and view tutor availability with recurrence options (daily/weekly).
- **Student and Tutor APIs:** Manage student and tutor profiles with full CRUD support.
- **Notification API:** Log or send notifications for system events.

For a detailed list of endpoints, request formats, and responses, please refer to the API documentation in the root folder. 



## Schema Design

The database schema includes the following tables:

1. **Tutors:** Stores information about tutors, including their name, email, and subjects.
2. **Students:** Stores information about students, including their name, email, and preferred time zone.
3. **Availability:** Tracks tutor availability, including time slots, time zones, and booking statuses.
4. **Bookings:** Stores booking information, linking students and tutors, with time slot details.
5. **Notifications:** Logs notifications for system events such as bookings and availability updates.

The schema is designed to support one-to-many relationships:
- A **tutor** can have multiple availabilities and bookings.
- A **student** can book multiple slots with tutors.


## How to Run the Project

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd collaborative-scheduling-system
   ```
3. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up the PostgreSQL database and update the configuration in `app/__init__.py`.
6. Run the Flask server:
   ```bash
   flask run
   ```
7. Access the application in your browser at `http://localhost:5000`.


## Collaboration and Task Division

This project was collaboratively developed with the following task distribution:

1. **Schema Design:** We have met together in order to discuss the design in-person.
2. **API Design:** We have met together in order to discuss the API design, however, we split the listing between each other. 
3. **Implementation:** We have worked together and implemented 3 API's each. 
4. **Deployment and Testing:** We both independently configured the Flask server, integrated PostgreSQL, and performed manual end-to-end testing.
5. **Presentation:** We both have contributed to creating the video demonstration.


## Video Presentation

The video presentation includes:
1. An overview of the database schema and its design rationale.
2. A demonstration of the system's features, including tutor availability management, student bookings, and notifications.
3. A walkthrough of the collaborative process and task division.
