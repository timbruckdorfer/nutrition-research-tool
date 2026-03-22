"""
PDF Text Extraction Tool

This tool converts PDF files to text. It's the foundation for all other tools
since they need the paper text to analyze.

Why pymupdf (fitz)?
- Fast C-based library
- Handles multi-column layouts (common in scientific papers)
- Preserves text structure better than alternatives

OCR Support:
- Automatically detects image-based/scanned PDFs
- Falls back to OCR (Optical Character Recognition) when needed
- Uses Tesseract for text extraction from images
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class PDFExtractor:
    """Handles PDF text extraction with error handling and validation."""
    
    def __init__(self):
        """Initialize the PDF extractor."""
        self.ocr_threshold = 200  # If text < 200 chars, try OCR
        
    def _extract_with_ocr(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF using OCR (for scanned/image-based PDFs).
        
        This is slower but works with PDFs that contain only images.
        Requires Tesseract and Poppler system binaries.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with OCR-extracted text and metadata
        """
        if not OCR_AVAILABLE:
            return {
                "success": False,
                "error": "OCR is not available (pytesseract/pdf2image not installed). "
                         "This PDF appears to be scanned/image-based and cannot be processed without OCR.",
                "text": "",
                "page_count": 0,
                "method": "OCR"
            }

        try:
            # Convert PDF pages to images
            # DPI 300 is a good balance between quality and speed
            images = convert_from_path(pdf_path, dpi=300)
            
            full_text = ""
            page_count = len(images)
            
            for page_num, image in enumerate(images, start=1):
                # Extract text from image using Tesseract OCR
                page_text = pytesseract.image_to_string(image, lang='eng')
                
                # Add page separator
                full_text += f"\n--- Page {page_num} (OCR) ---\n"
                full_text += page_text
            
            return {
                "success": True,
                "text": full_text,
                "page_count": page_count,
                "method": "OCR",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"OCR extraction failed: {str(e)}",
                "text": "",
                "page_count": 0,
                "method": "OCR"
            }
    
    def extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Absolute or relative path to the PDF file
            
        Returns:
            Dictionary containing:
                - text: Full extracted text
                - page_count: Number of pages
                - file_name: Name of the PDF file
                - success: Boolean indicating success
                - error: Error message if failed
                
        Raises:
            FileNotFoundError: If PDF doesn't exist
            Exception: If PDF is corrupted or can't be read
        """
        try:
            # Convert to Path object for better path handling
            pdf_file = Path(pdf_path)
            
            # Validate file exists
            if not pdf_file.exists():
                return {
                    "success": False,
                    "error": f"PDF file not found: {pdf_path}",
                    "text": "",
                    "page_count": 0,
                    "file_name": pdf_file.name
                }
            
            # Validate it's a PDF
            if pdf_file.suffix.lower() != '.pdf':
                return {
                    "success": False,
                    "error": f"File is not a PDF: {pdf_path}",
                    "text": "",
                    "page_count": 0,
                    "file_name": pdf_file.name
                }
            
            # Open PDF and extract text
            doc = fitz.open(pdf_path)
            
            # Extract text from all pages
            full_text = ""
            for page_num, page in enumerate(doc, start=1):
                # Extract text while preserving layout
                page_text = page.get_text("text")
                
                # Add page separator for context
                full_text += f"\n--- Page {page_num} ---\n"
                full_text += page_text
            
            page_count = len(doc)
            doc.close()
            
            # Check if we got meaningful text
            text_length = len(full_text.strip())
            
            # If text is too short, PDF might be image-based - try OCR
            if text_length < self.ocr_threshold:
                print(f"⚠️  Text extraction yielded only {text_length} characters.")
                print(f"   Attempting OCR (this may take 10-30 seconds per page)...")
                
                ocr_result = self._extract_with_ocr(pdf_path)
                
                if ocr_result["success"]:
                    # OCR succeeded, return OCR text
                    return {
                        "success": True,
                        "text": ocr_result["text"],
                        "page_count": ocr_result["page_count"],
                        "file_name": pdf_file.name,
                        "method": "OCR",
                        "error": None
                    }
                else:
                    # Both methods failed
                    return {
                        "success": False,
                        "error": f"PDF appears to be empty. Normal extraction: {text_length} chars. OCR also failed: {ocr_result.get('error')}",
                        "text": "",
                        "page_count": page_count,
                        "file_name": pdf_file.name
                    }
            
            # Normal text extraction was successful
            return {
                "success": True,
                "text": full_text,
                "page_count": page_count,
                "file_name": pdf_file.name,
                "method": "direct",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract text: {str(e)}",
                "text": "",
                "page_count": 0,
                "file_name": Path(pdf_path).name if pdf_path else "unknown"
            }
    
    def get_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata (author, title, creation date from PDF properties).
        
        Note: This is separate from extracting paper metadata from content.
        PDF metadata is often incomplete or incorrect, so we rely on LLM extraction.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF properties
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            
            return {
                "success": True,
                "pdf_title": metadata.get("title", ""),
                "pdf_author": metadata.get("author", ""),
                "pdf_subject": metadata.get("subject", ""),
                "pdf_creator": metadata.get("creator", ""),
                "pdf_producer": metadata.get("producer", ""),
                "pdf_creation_date": metadata.get("creationDate", ""),
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract metadata: {str(e)}"
            }


# Create a singleton instance that will be used by the MCP server
pdf_extractor = PDFExtractor()
