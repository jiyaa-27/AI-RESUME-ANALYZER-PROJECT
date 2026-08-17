import pypdf

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text from a PDF file-like object using pypdf.
    
    Args:
        pdf_file: A file-like object or path to the PDF file.
        
    Returns:
        str: The extracted text.
        
    Raises:
        ValueError: If the file is empty, encrypted, or if text extraction fails.
    """
    try:
        reader = pypdf.PdfReader(pdf_file)
        
        # Check if the file is encrypted
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise ValueError("The PDF file is encrypted and password-protected. Please upload an unencrypted file.")
                
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        text = text.strip()
        if not text:
            raise ValueError("No text could be extracted from the PDF. It might be an image-only (scanned) document or empty.")
            
        return text
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"An error occurred while parsing the PDF: {str(e)}")
