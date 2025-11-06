import re
from typing import Dict, List
import PyPDF2
import docx
from pathlib import Path

class DocumentParser:
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise ValueError(f"Failed to parse TXT: {str(e)}")
    
    @staticmethod
    def parse_document(file_path: str) -> str:
        """Parse document based on extension"""
        extension = Path(file_path).suffix.lower()
        
        if extension == '.pdf':
            return DocumentParser.extract_text_from_pdf(file_path)
        elif extension == '.docx':
            return DocumentParser.extract_text_from_docx(file_path)
        elif extension == '.txt':
            return DocumentParser.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    @staticmethod
    def extract_skills(text: str, skill_keywords: List[str]) -> List[str]:
        """Extract skills from text based on keyword list"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return found_skills
    
    @staticmethod
    def extract_email(text: str) -> str:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "Not found"
    
    @staticmethod
    def extract_phone(text: str) -> str:
        """Extract phone number from text"""
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else "Not found"
    
    @staticmethod
    def estimate_experience_years(text: str) -> int:
        """Estimate years of experience from resume text"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0

parser = DocumentParser()
