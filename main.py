import requests
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel, EmailStr
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import uvicorn
from io import BytesIO  # Add this import

from dotenv import load_dotenv  # Add this import

# Load environment variables
load_dotenv()  # Add this line at the top of your code


# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1:1.5b"

# Email Configuration
EMAIL_CONFIG = {
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 587,
    "SENDER_EMAIL": os.getenv("SENDER_EMAIL", "my-email@gmail.com"),
    "SENDER_PASSWORD": os.getenv("SENDER_PASSWORD", "my-app-password")
}

app = FastAPI()

class PDFProcessor:
    @staticmethod
    def extract_text(pdf_file: bytes) -> str:
        """Extract text from PDF using OCR if needed"""
        try:
            # Create BytesIO object from bytes
            pdf_stream = BytesIO(pdf_file)
            
            # Use BytesIO object with PdfReader
            pdf = PdfReader(pdf_stream)
            text = "".join([page.extract_text() for page in pdf.pages if page.extract_text()])

            # Use OCR if no text is extracted
            if not text.strip():
                # Create new BytesIO object for pdf2image
                pdf_stream_ocr = BytesIO(pdf_file)
                images = convert_from_bytes(pdf_stream_ocr.getvalue())
                text = "".join([pytesseract.image_to_string(image) for image in images])

            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

class BloodTestAnalysis:
    @staticmethod
    def analyze_report(report_text: str) -> dict:
        """Send blood test text to Ollama LLM for analysis"""
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": f"Analyze this blood test report and summarize abnormalities:\n\n{report_text}",
                "stream": False
            },
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to process report with Ollama")

        result = response.json().get("response", "No response from AI")
        return {"analysis": result}

class EmailService:
    @staticmethod
    def send_email(to_email: str, analysis_results: dict):
        """Send analysis results via email"""
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['SENDER_EMAIL']
        msg['To'] = to_email
        msg['Subject'] = "Your Blood Test Analysis Results"

        body = f"""
        Dear User,

        Here is your blood test analysis:

        {analysis_results['analysis']}

        Best regards,
        Your Health Analysis Team
        """
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['SENDER_PASSWORD'])
                server.send_message(msg)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@app.post("/analyze-blood-test")
async def analyze_blood_test(
    email: str = Form(...),
    pdf_file: UploadFile = File(...)
):
    """API Endpoint: Analyze blood test and send results via email"""
    try:
        if not pdf_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

        # Read and process PDF
        pdf_content = await pdf_file.read()
        pdf_text = PDFProcessor.extract_text(pdf_content)

        # Analyze report
        analysis_results = BloodTestAnalysis.analyze_report(pdf_text)

        # Send email
        EmailService.send_email(email, analysis_results)

        return {"status": "success", "message": "Analysis completed and sent to your email", "results": analysis_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)