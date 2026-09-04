import os,json, io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from minio import Minio
from utils.calcu import calculate_stuff
from datetime import datetime, timedelta
from database import Audit, sessionLocal
from llama_cpp import Llama
from dotenv import load_dotenv
load_dotenv()
minio_client = Minio(os.getenv("MINIO_URL"), access_key=os.getenv("MINIO_ACCESS"), secret_key=os.getenv("MINIO_SECRET"), secure=False)
bucket = "audit-reports"
pdf_buffer = io.BytesIO()
doc = SimpleDocTemplate(pdf_buffer,pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40, title="Monthly Audit Report")
llm = Llama(model_path="./Phi-3-mini-4k-instruct-q4.gguf", n_ctx=2048, n_threads=4)
db=sessionLocal()
start = datetime.utcnow()
end_time = start +timedelta(months=1)
data = db.query(Audit).filter(Audit.timestamp>=start, Audit.timestamp<=end_time).all()
if not data:
    raise ValueError("no data found for given time period")
net, other = calculate_stuff(data)
prompt = f"""
You are generating a monthly merchant risk report.
Reporting period:
Start- {start}
End- {end_time}
The following statistics were computed deterministically
from the audit database:
{net}, {other}
Write a concise executive summary.
Rules:
- Do not invent statistics.
- Do not modify numerical values.
- Do not claim causation unless supported by the data.
- Clearly distinguish observations from recommendations.
"""
output = llm(prompt, max_tokens=150, temperature=0.4)
styles = getSampleStyleSheet()
story = []
story.append(Paragraph("Incident Data", styles['Title']))
story.append(Spacer(1, 12))
story.append(Paragraph(f"Data Compiled On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
story.append(Spacer(1, 20))
table_content = [["Event ID", "Entity", "Event", "Payload", "Action", "Prediction score", "Linking Inference", "Timestamp"]]
for row in data:
    table_content.append([row.event_id, row.entity, row.event, row.payload, row.action, row.pred, row.res, row.timestamp])
report_table = Table(table_content, colWidths=[150, 150, 120])
report_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F7FAFC")),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#EDF2F7")]),
]))
story.append(report_table)
doc.build(story)
pdf_buffer.seek(0)
file_length = pdf_buffer.getbuffer().nbytes
try:
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    minio_client.put_object(bucket_name=bucket, object_name=filename, data=pdf_buffer, length=file_length, content_type="application/pdf")
except Exception:
    pass #for now
finally:
    pdf_buffer.close()
