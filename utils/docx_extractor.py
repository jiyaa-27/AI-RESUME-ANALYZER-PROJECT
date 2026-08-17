import docx

def extract_text_from_docx(docx_file) -> str:
    """
    Extracts text from a DOCX file-like object using python-docx.
    
    Args:
        docx_file: A file-like object or path to the DOCX file.
        
    Returns:
        str: The extracted text.
        
    Raises:
        ValueError: If the file is not a valid DOCX file or extraction fails.
    """
    try:
        doc = docx.Document(docx_file)
        text = []
        
        # Extract text from paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text.strip())
                
        # Extract text from tables to ensure no content is missed
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text.append(" ".join(row_text))
                    
        full_text = "\n".join(text).strip()
        
        if not full_text:
            raise ValueError("No readable text could be extracted from the DOCX file. The file might be empty.")
            
        return full_text
    except Exception as e:
        # Detect if it's an older .doc file (which fails ZIP parsing)
        error_msg = str(e)
        if "PackageNotFoundError" in error_msg or "BadZipFile" in error_msg:
            raise ValueError(
                "Unsupported file format. Older Word documents (.doc) are not supported. "
                "Please save/convert your document to .docx or .pdf format and try again."
            )
        raise ValueError(f"An error occurred while parsing the DOCX document: {error_msg}")
