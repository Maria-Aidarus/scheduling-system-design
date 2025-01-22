from flask import Blueprint, request, jsonify, render_template
from app.models import Tutor, Availability, Booking, Student, Notification
from datetime import datetime, timedelta
from app import db
import pytz

# Define the Blueprint
routes = Blueprint('routes', __name__)

# Home route
@routes.route("/")
def home():
    return render_template("index.html")

def convert_timezone(start_time, end_time, past_timezone, new_timezone):
    """
    Converts start and end times from one timezone to another.
    
    Parameters:
    - start_time (str): Start time in the format 'HH:MM:SS' or 'HH:MM'.
    - end_time (str): End time in the format 'HH:MM:SS' or 'HH:MM'.
    - past_timezone (str): Original timezone of the times.
    - new_timezone (str): Target timezone to convert the times to.
    
    Returns:
    - tuple: Converted start and end times as strings in the format 'HH:MM:SS'.
    """
    # Parse the input times
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M:%S")
    except ValueError:
        start_time_obj = datetime.strptime(start_time, "%H:%M")
    
    try:
        end_time_obj = datetime.strptime(end_time, "%H:%M:%S")
    except ValueError:
        end_time_obj = datetime.strptime(end_time, "%H:%M")
    
    # Define the timezones
    try:
        from_tz = pytz.timezone(past_timezone)
        to_tz = pytz.timezone(new_timezone)
    except pytz.UnknownTimeZoneError as e:
        raise ValueError(f"Invalid timezone: {str(e)}")
    
    # Localize the times in the original timezone
    now = datetime.now()  # Current date for localization
    start_time_localized = from_tz.localize(datetime.combine(now.date(), start_time_obj.time()))
    end_time_localized = from_tz.localize(datetime.combine(now.date(), end_time_obj.time()))
    
    # Convert to the target timezone
    start_time_converted = start_time_localized.astimezone(to_tz).strftime("%H:%M:%S")
    end_time_converted = end_time_localized.astimezone(to_tz).strftime("%H:%M:%S")
    
    return start_time_converted, end_time_converted

@routes.route("/availability/view", methods=["GET"])
def view_availability():
    # Get the selected timezone from the query parameter (default to UTC)
    selected_timezone = request.args.get("timezone", "UTC")

    # Fetch all unbooked availabilities and their associated tutors
    availabilities = db.session.query(Availability, Tutor).join(Tutor).filter(Availability.is_booked == False).all()

    # Process the availabilities and convert the times to the selected timezone
    converted_availabilities = []
    for availability, tutor in availabilities:
        start_time_converted, end_time_converted = convert_timezone(
            availability.start_time.strftime("%H:%M:%S"),
            availability.end_time.strftime("%H:%M:%S"),
            availability.time_zone,
            selected_timezone
        )
        converted_availabilities.append({
            "tutor": tutor,
            "availability": availability,
            "start_time_converted": start_time_converted,
            "end_time_converted": end_time_converted,
            "converted_timezone": selected_timezone
        })

    return render_template("view_availability.html", availabilities=converted_availabilities, timezone=selected_timezone)

@routes.route("/availability/add", methods=["GET", "POST"])
def add_availability():
    if request.method == "POST":
        try:
            tutor_id = request.form.get("tutor_id")
            date = request.form.get("date")
            start_time = request.form.get("start_time")
            end_time = request.form.get("end_time")
            time_zone = request.form.get("time_zone")
            recurrence = request.form.get("recurrence")
            occurrences = int(request.form.get("occurrences", 1))

            if not (tutor_id and date and start_time and end_time and time_zone):
                return render_template("add_availability.html", error="All fields are required!")

            tutor = Tutor.query.get(tutor_id)
            if not tutor:
                return render_template("add_availability.html", error="Tutor not found!")

            start_time_obj = datetime.strptime(start_time, "%H:%M").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M").time()

            if start_time_obj >= end_time_obj:
                return render_template("add_availability.html", error="Start time must be before end time!")

            # Handle recurrence logic
            base_date = datetime.strptime(date, "%Y-%m-%d").date()
            availabilities = []

            for i in range(occurrences):
                current_date = base_date
                if recurrence == "daily":
                    current_date = base_date + timedelta(days=i)
                elif recurrence == "weekly":
                    current_date = base_date + timedelta(weeks=i)

                # Check for conflicts
                existing_availabilities = Availability.query.filter_by(
                    tutor_id=tutor_id, date=current_date
                ).all()
                for availability in existing_availabilities:
                    if not (end_time_obj <= availability.start_time or start_time_obj >= availability.end_time):
                        return render_template(
                            "add_availability.html",
                            error=f"Conflict on {current_date}: {availability.start_time} - {availability.end_time}",
                        )

                # Create availability instance
                availabilities.append(
                    Availability(
                        tutor_id=tutor_id,
                        date=current_date,
                        start_time=start_time_obj,
                        end_time=end_time_obj,
                        time_zone=time_zone,
                    )
                )

            # Add all availabilities to the database
            db.session.add_all(availabilities)
            db.session.commit()

            return render_template("add_availability.html", message="Availabilities added successfully!")

        except Exception as e:
            return render_template("add_availability.html", error=f"An error occurred: {str(e)}")

    return render_template("add_availability.html")

## Retrieve a tutor’s availability
@routes.route("/availability/<int:tutor_id>", methods=["GET"])
def get_availability(tutor_id):
    # Check if the tutor exists
    tutor = Tutor.query.get(tutor_id)
    if not tutor:
        return jsonify({"error": "Tutor not found"}), 404

    # Retrieve all availability records for the tutor
    availabilities = Availability.query.filter_by(tutor_id=tutor_id).order_by(Availability.date, Availability.start_time).all()

    # Render the HTML template with the tutor's information and availability
    return render_template(
        "tutor_availability.html",
        tutor=tutor,
        availabilities=availabilities
    )

@routes.route("/book-slot", methods=["GET", "POST"])
def book_slot():
    if request.method == "POST":
        # Handle the form submission
        student_id = request.form.get("student_id")
        tutor_id = request.form.get("tutor_id")
        date = request.form.get("date")
        start_time = request.form.get("start_time").strip()
        end_time = request.form.get("end_time").strip()
        time_zone = request.form.get("time_zone")

        # Validate student and tutor
        student = Student.query.get(student_id)
        tutor = Tutor.query.get(tutor_id)

        if not student:
            return render_template("book_slot.html", error="Student not found!")
        if not tutor:
            return render_template("book_slot.html", error="Tutor not found!")

        try:
            # Remove seconds if they exist
            start_time = ":".join(start_time.split(":")[:2])
            end_time = ":".join(end_time.split(":")[:2])

            booking_time = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        except ValueError as e:
            return render_template("book_slot.html", error=f"Invalid time format: {str(e)}")

        # Check for slot conflicts
        existing_booking = Booking.query.filter_by(
            tutor_id=tutor_id,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            start_time=datetime.strptime(start_time, "%H:%M").time(),
            end_time=datetime.strptime(end_time, "%H:%M").time()
        ).first()

        if existing_booking:
            return render_template("book_slot.html", error="Slot already booked!")

        # Find the availability record and mark it as booked
        availability = Availability.query.filter_by(
            tutor_id=tutor_id,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            start_time=datetime.strptime(start_time, "%H:%M").time(),
            end_time=datetime.strptime(end_time, "%H:%M").time(),
            is_booked=False
        ).first()

        if not availability:
            return render_template("book_slot.html", error="No available slot found!")

        availability.is_booked = True

        # Add new booking
        booking = Booking(
            student_id=student_id,
            tutor_id=tutor_id,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            start_time=datetime.strptime(start_time, "%H:%M").time(),
            end_time=datetime.strptime(end_time, "%H:%M").time(),
            time_zone=time_zone,
            booking_time=booking_time
        )
        db.session.add(booking)
        db.session.commit()

        # Render the form again with a success message
        return render_template("book_slot.html", message="Booking confirmed!")

    # Render the booking form on GET requests with prefilled fields
    tutor_id = request.args.get("tutor_id")
    date = request.args.get("date")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    time_zone = request.args.get("time_zone")

    return render_template(
        "book_slot.html",
        tutor_id=tutor_id,
        date=date,
        start_time=start_time,
        end_time=end_time,
        time_zone=time_zone
    )

@routes.route("/student-bookings/<int:student_id>", methods=["GET"])
def get_student_bookings(student_id):
    # Validate Student
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    # Fetch all bookings for the student, joined with the Tutor table
    bookings = db.session.query(Booking, Tutor).join(Tutor, Booking.tutor_id == Tutor.id).filter(Booking.student_id == student_id).all()

    # Format bookings data
    formatted_bookings = [{
        "tutor_name": tutor.name,
        "date": booking.date.strftime("%Y-%m-%d"),
        "start_time": booking.start_time.strftime("%H:%M"),
        "end_time": booking.end_time.strftime("%H:%M"),
        "status": booking.status
    } for booking, tutor in bookings]

    return render_template("student_bookings.html", bookings=formatted_bookings, student=student)

@routes.route("/tutor-bookings/<int:tutor_id>", methods=["GET"])
def get_tutor_bookings(tutor_id):
    # Validate Tutor
    tutor = Tutor.query.get(tutor_id)
    if not tutor:
        return jsonify({"error": "Tutor not found"}), 404

    # Fetch all bookings for the tutor, joined with the Student table
    bookings = db.session.query(Booking, Student).join(Student, Booking.student_id == Student.id).filter(Booking.tutor_id == tutor_id).all()

    # Format bookings data
    formatted_bookings = [{
        "student_name": student.name,
        "date": booking.date.strftime("%Y-%m-%d"),
        "start_time": booking.start_time.strftime("%H:%M"),
        "end_time": booking.end_time.strftime("%H:%M"),
        "status": booking.status
    } for booking, student in bookings]

    return render_template("tutor_bookings.html", bookings=formatted_bookings)

# Log or send notifications for updates
@routes.route("/notifications", methods=["POST"])
def notifications():
    data = request.json
    # Log or process the notification here (e.g., send an email or log to a database)
    # For simplicity, we’ll just return a success response.
    return jsonify({"message": "Notification sent successfully"})
