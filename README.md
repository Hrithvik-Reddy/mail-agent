Blood Test Mail agent

Overview
The Blood Test Analysis API is a FastAPI application designed to analyze blood test reports in PDF format. It extracts text from the PDF, analyzes it using a language model (Ollama), and sends the analysis results via email. This project utilizes various libraries such as PyPDF2 for PDF processing, pytesseract for Optical Character Recognition (OCR), and smtplib for sending emails.

Features
PDF Upload: Accepts blood test reports in PDF format.

Text Extraction: Extracts text from PDFs using OCR if necessary.

AI Analysis: Sends extracted text to an AI model for analysis and summarization of abnormalities.

Email Notifications: Sends the analysis results directly to the user's email.

Technologies Used
FastAPI: A modern web framework for building APIs with Python.

PyPDF2: A library for reading PDF files.

pytesseract: An OCR tool for extracting text from images.

pdf2image: Converts PDF pages to images for OCR processing.

smtplib: A built-in Python library for sending emails.

dotenv: Loads environment variables from a .env file.