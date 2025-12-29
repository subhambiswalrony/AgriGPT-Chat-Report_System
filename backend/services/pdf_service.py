from weasyprint import HTML
import uuid
import os

def generate_report_pdf(report: dict) -> str:
    os.makedirs("static/reports", exist_ok=True)

    filename = f"{report['crop']}_{uuid.uuid4().hex}.pdf"
    path = f"static/reports/{filename}"

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: DejaVu Sans, sans-serif;
                line-height: 1.6;
            }}
            h1 {{ color: green; }}
            h2 {{ margin-top: 20px; }}
        </style>
    </head>
    <body>

    <h1>{report['crop']} – Farming Report</h1>
    <p><b>Region:</b> {report['region']}</p>

    <h2>🌱 Sowing Advice</h2>
    <ul>{"".join(f"<li>{x}</li>" for x in report['sowingAdvice'])}</ul>

    <h2>🧪 Fertilizer Plan</h2>
    <ul>{"".join(f"<li>{x}</li>" for x in report['fertilizerPlan'])}</ul>

    <h2>🌦 Weather Tips</h2>
    <ul>{"".join(f"<li>{x}</li>" for x in report['weatherTips'])}</ul>

    <h2>📅 Farming Calendar</h2>
    <ul>{"".join(f"<li>{x}</li>" for x in report['calendar'])}</ul>

    </body>
    </html>
    """

    HTML(string=html).write_pdf(path)
    return path
