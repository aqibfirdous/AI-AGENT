from app import celery
from app.report_generator import generate_report, send_report_via_email
import logging

# Setup logging right here
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("report.log"),
        logging.StreamHandler()
    ]
)

@celery.task(name='app.tasks.send_report')
def send_report():
    logging.info("🚀 Task started")
    try:
        report = generate_report()
        logging.info("📝 Report generated")
        send_report_via_email(report)
        logging.info("📧 Email sent function completed")
    except Exception as e:
        logging.error(f"❌ Error in task: {e}")
