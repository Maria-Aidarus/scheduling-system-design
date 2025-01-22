from app import app, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create all tables defined in models.py
        print("Tables created successfully.")
        print("Template folder:", app.template_folder)
    app.run(debug=True)
