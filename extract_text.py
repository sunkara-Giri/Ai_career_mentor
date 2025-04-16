import sys
import json
from docx import Document
import PyPDF2
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_from_docx(file_path: str) -> str:
    """Extract text from a Word document."""
    try:
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '\n'.join(text)
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise

def extract_from_pdf(file_path: str) -> str:
    """Extract text from a PDF document."""
    try:
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_text(file_path: str) -> Dict[str, Any]:
    """Extract text from a document based on its file extension."""
    try:
        if file_path.lower().endswith('.docx'):
            text = extract_from_docx(file_path)
        elif file_path.lower().endswith('.pdf'):
            text = extract_from_pdf(file_path)
        else:
            raise ValueError("Unsupported file type. Only PDF and Word documents are supported.")
        
        return {
            'success': True,
            'text': text
        }
    except Exception as e:
        logger.error(f"Error in text extraction: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({
            'success': False,
            'error': 'Please provide a file path as an argument.'
        }))
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = extract_text(file_path)
    print(json.dumps(result)) 