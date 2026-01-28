"""File processing module for reading email content from various file formats."""

import logging
import os
from typing import Optional

from pypdf import PdfReader

logger = logging.getLogger(__name__)

# Constants
TEXT_FILE_EXTENSION = ".txt"
PDF_FILE_EXTENSION = ".pdf"
SUPPORTED_EXTENSIONS = {TEXT_FILE_EXTENSION, PDF_FILE_EXTENSION}
DEFAULT_ENCODING = "utf-8"


class FileProcessor:
    
    @staticmethod
    def read_text_file(file_path: str, encoding: str = DEFAULT_ENCODING) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Text file not found: {file_path}")
        
        try:
            logger.debug(f"Reading text file: {file_path}")
            with open(file_path, "r", encoding=encoding) as file:
                content = file.read()
            logger.debug(f"Successfully read {len(content)} characters from text file")
            return content
        except UnicodeDecodeError as e:
            error_msg = f"Encoding error reading text file {file_path}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except IOError as e:
            error_msg = f"IO error reading text file {file_path}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error reading text file {file_path}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    @staticmethod
    def read_pdf_file(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        try:
            logger.debug(f"Reading PDF file: {file_path}")
            text_content = []
            pdf_reader = PdfReader(file_path)
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                except Exception as e:
                    logger.warning(
                        f"Error extracting text from page {page_num}: {str(e)}"
                    )
            
            content = "\n".join(text_content)
            logger.debug(
                f"Successfully extracted {len(content)} characters from PDF "
                f"({len(pdf_reader.pages)} pages)"
            )
            return content
        except Exception as e:
            error_msg = f"Error reading PDF file {file_path}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    @staticmethod
    def _get_file_extension(file_path: str) -> str:
        return os.path.splitext(file_path)[1].lower()
    
    @staticmethod
    def process_file(file_path: str) -> str:
        if not file_path:
            raise ValueError("File path cannot be empty")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = FileProcessor._get_file_extension(file_path)
        
        if file_extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
            )
        
        logger.info(f"Processing file: {file_path} (type: {file_extension})")
        
        if file_extension == TEXT_FILE_EXTENSION:
            return FileProcessor.read_text_file(file_path)
        elif file_extension == PDF_FILE_EXTENSION:
            return FileProcessor.read_pdf_file(file_path)
        else:
            raise ValueError(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

