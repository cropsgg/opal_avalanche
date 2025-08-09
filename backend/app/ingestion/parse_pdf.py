from __future__ import annotations

from typing import List, Dict, Any
from io import BytesIO
import re
from pypdf import PdfReader
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


def extract_text_pages(pdf_bytes: bytes) -> List[str]:
    """Legacy function - extract text by pages"""
    reader = PdfReader(BytesIO(pdf_bytes))
    pages: List[str] = []
    for p in reader.pages:
        pages.append(p.extract_text() or "")
    return pages


def has_text_layer(pdf_bytes: bytes) -> bool:
    """Check if PDF has extractable text layer"""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        for page in reader.pages[:3]:  # Check first 3 pages
            text = page.extract_text().strip()
            if len(text) > 50:  # If we get substantial text, assume text layer exists
                return True
        return False
    except Exception:
        return False


def extract_text_with_paras(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """Extract text and segment into paragraphs with metadata"""
    
    # Use pdfminer for better text extraction
    output_string = BytesIO()
    with BytesIO(pdf_bytes) as input_file:
        extract_text_to_fp(input_file, output_string, 
                          laparams=LAParams(word_margin=0.1, char_margin=2.0),
                          output_type='text', codec=None)
    
    full_text = output_string.getvalue().decode('utf-8')
    
    # Segment into paragraphs
    paragraphs = []
    para_id = 1
    current_page = 1
    
    # Split by double newlines first, then clean up
    raw_paras = re.split(r'\n\s*\n', full_text)
    
    for raw_para in raw_paras:
        # Clean up the paragraph
        para_text = re.sub(r'\s+', ' ', raw_para.strip())
        
        if len(para_text) < 20:  # Skip very short paragraphs
            continue
            
        # Detect numbered paragraphs (common in legal documents)
        numbered_match = re.match(r'^(\d+\.?\s*)', para_text)
        
        # Estimate page breaks based on form feeds or page numbers
        if '\f' in raw_para or re.search(r'Page\s+\d+', para_text):
            current_page += 1
            
        paragraphs.append({
            "para_id": para_id,
            "text": para_text,
            "page": current_page,
            "is_numbered": bool(numbered_match),
            "number": numbered_match.group(1).strip() if numbered_match else None,
            "word_count": len(para_text.split()),
            "char_count": len(para_text)
        })
        
        para_id += 1
    
    return paragraphs


def extract_headings(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """Extract potential headings based on formatting patterns"""
    paragraphs = extract_text_with_paras(pdf_bytes)
    headings = []
    
    for para in paragraphs:
        text = para["text"]
        
        # Heuristics for headings in legal documents
        is_heading = False
        heading_type = None
        
        # All caps short lines
        if text.isupper() and len(text.split()) < 10:
            is_heading = True
            heading_type = "section"
            
        # Roman numerals
        if re.match(r'^[IVX]+\.?\s+', text):
            is_heading = True
            heading_type = "chapter"
            
        # "CHAPTER", "SECTION", "PART" keywords
        if re.match(r'^(CHAPTER|SECTION|PART|ARTICLE)\s+', text, re.IGNORECASE):
            is_heading = True
            heading_type = "major_section"
            
        if is_heading:
            headings.append({
                "para_id": para["para_id"],
                "text": text,
                "type": heading_type,
                "page": para["page"]
            })
    
    return headings


