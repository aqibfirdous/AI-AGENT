from flask import jsonify
from app import app
from app.tasks import send_report


@app.route('/')
def home():
    return "Welcome! Use /trigger_report to trigger the report manually."

@app.route('/trigger_report')
def trigger_report():
    # Trigger the Celery task manually and get its ID.
    result = send_report.apply_async()
    return jsonify({"message": "Report task triggered!", "task_id": result.id})

if __name__ == '__main__':
    app.run(debug=True)
