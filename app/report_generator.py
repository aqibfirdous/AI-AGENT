import datetime
from email.mime.application import MIMEApplication
import requests
import smtplib
from collections import Counter, defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF
from app.config import Config
import os
from dotenv import load_dotenv
import logging

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("report.log"),
        logging.StreamHandler()
    ]
)

def fetch_analytics_data():
    try:
        headers = {
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        response = requests.get(Config.API_ENDPOINT, timeout=10, headers=headers)
        response.raise_for_status()
        logging.info("Fetched analytics data")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching analytics data: {e}")
        return None

def generate_report():
    """
    Generates a comprehensive text report based on the API response.
    """
    now = datetime.datetime.now()
    raw_data = fetch_analytics_data()

    if raw_data and raw_data.get("success"):
        data = raw_data.get("data", [])
        total_in_response = len(data)

        # Task Status Counts
        statuses = [item.get("activity_status", "Unknown") for item in data]
        status_counts = Counter(statuses)

        # Involved Colleges & Tasks per College
        colleges = set()
        tasks_per_college = defaultdict(int)
        for item in data:
            college = item.get("college", "Unknown")
            colleges.add(college)
            tasks_per_college[college] += 1

        # Tasks per User
        tasks_per_user = defaultdict(int)
        for item in data:
            user_email = item.get("email", "Unknown")
            tasks_per_user[user_email] += 1

        # Building Report
        report_lines = [
            f"Report Generated at: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total records in API response: {total_in_response}",
            "",
            "Task Status Counts:"
        ]
        for status, count in status_counts.items():
            report_lines.append(f"  - {status}: {count}")
        report_lines.append("")

        report_lines.append("Involved Colleges:")
        for college in sorted(colleges):
            report_lines.append(f"  - {college}")
        report_lines.append("")

        report_lines.append("Tasks per College:")
        for college, count in tasks_per_college.items():
            report_lines.append(f"  - {college}: {count}")
        report_lines.append("")

        report_lines.append("Tasks per User (by email):")
        for i, (user, count) in enumerate(tasks_per_user.items(), start=1):
            report_lines.append(f"  {i}. {user}: {count}")
        report_lines.append("")

        overall_total = raw_data.get("total", "N/A")
        report_lines.append("Overall Total Tasks (from API 'total' field): " + str(overall_total))

        report = "\n".join(report_lines)
        logging.info("Report generated successfully.")
    else:
        report = (
            f"Report Generated at: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "Error: Unable to fetch or parse analytics data from the API."
        )
        logging.warning("Report generation failed due to API issues.")

    logging.debug("Report Contents:\n" + report)
    return report

def send_report_via_email(report):
    logging.info("Preparing to send email with report...")
    sender_email = "aqibfirdous93@gmail.com"

    # Load environment variables
    load_dotenv("C:\\Users\\aqibf\\PycharmProjects\\startupworld\\app\\.env")
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender_password:
        logging.error("EMAIL_APP_PASSWORD not loaded from environment.")
        return

    recipient_emails = [
        "avi@blueplanetsolutions.com",
        "rakesh@blueplanetsolutions.com",
        "prashanthatekar5585@gmail.com",
        "prashanth@blueplanetinfosolutions.com",
        "aqibfirdous6@gmail.com"
    ]

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    subject = f"Daily Task Analytics Report - {current_date}"
    body_text = """Hi,

Please find attached the report for today.

Best regards,
Aqib Firdous"""

    # Save report as .txt
    text_filename = "generated_report.txt"
    try:
        with open(text_filename, "w") as f:
            f.write(report)
        logging.info("Saved text version of the report.")
    except Exception as e:
        logging.error(f"Failed to save text file: {e}")

    # Generate PDF
    pdf_filename = "generated_report.pdf"
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=10)
        for line in report.split("\n"):
            pdf.cell(0, 10, txt=line, ln=True)
        pdf.output(pdf_filename)
        logging.info("PDF report generated.")
    except Exception as e:
        logging.error(f"Failed to generate PDF: {e}")
        return

    # Compose Email with Report Attachment
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(recipient_emails)
    message["Subject"] = subject
    message.attach(MIMEText(body_text, "plain"))

    try:
        with open(pdf_filename, "rb") as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
            pdf_attachment.add_header("Content-Disposition", "attachment", filename=pdf_filename)
            message.attach(pdf_attachment)
    except Exception as e:
        logging.error(f"Failed to attach PDF to email: {e}")
        return

    # Send Email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_emails, message.as_string())
        logging.info("Email with PDF report sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def get_pending_or_in_progress_users(data):
    """
    Returns a dictionary mapping each user (by email) to a list of their tasks that are pending or in progress.
    """
    user_tasks = defaultdict(list)
    for item in data:
        status = item.get("activity_status", "").lower()
        if status in ["pending", "in progress"]:
            # You can add additional details like task title or deadline if available.
            task_title = item.get("title", "Unnamed Task")
            user = item.get("email", "Unknown")
            user_tasks[user].append((status, task_title))
    return user_tasks

def send_reminder_emails(user_tasks):
    """
    Sends a personalized reminder email to each user with tasks that are either pending or in progress.
    """
    sender_email = "aqibfirdous93@gmail.com"
    load_dotenv("C:\\Users\\aqibf\\PycharmProjects\\startupworld\\app\\.env")
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender_password:
        logging.error("EMAIL_APP_PASSWORD not loaded from environment.")
        return

    for user_email, tasks in user_tasks.items():
        subject = "Reminder: Pending / In Progress Tasks - Action Required by EOD"
        # Create a task list string showing each task and its status.
        task_list = "\n".join([f"- {title} ({status.capitalize()})" for status, title in tasks])
        body_text = f"""Hi,

You currently have the following tasks marked as pending or in progress:

{task_list}

Please ensure these tasks are completed and submitted by the end of the day.

Best regards,
Task Management Bot
"""
        # Compose the email for the user.
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = user_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, user_email, msg.as_string())
            logging.info(f"Reminder email sent to {user_email}")
        except Exception as e:
            logging.error(f"Failed to send reminder email to {user_email}: {e}")

if __name__ == "__main__":
    # Generate and send the overall report email.
    report = generate_report()
    send_report_via_email(report)

    # Fetch analytics data to get pending/in-progress tasks
    raw_data = fetch_analytics_data()
    if raw_data and raw_data.get("success"):
        data = raw_data.get("data", [])
        user_tasks = get_pending_or_in_progress_users(data)
        if user_tasks:
            send_reminder_emails(user_tasks)
        else:
            logging.info("No pending or in-progress tasks found. No reminder emails sent.")
    else:
        logging.error("Failed to fetch analytics data for reminders.")

