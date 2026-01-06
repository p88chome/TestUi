import os
import pypdf
import pdfplumber
import logging

def execute(input_data: dict) -> dict:
    """
    Executes PDF operations.
    Input:
    {
        "operation": "extract_text" | "get_metadata" | "merge",
        "files": ["/path/to/a.pdf", ...],
        "output_path": "/path/to/merged.pdf" (optional)
    }
    """
    operation = input_data.get("operation")
    files = input_data.get("files", [])
    output_path = input_data.get("output_path", "merged_output.pdf")

    if not files:
        return {"error": "No files provided"}
    
    # Ensure files exist and are absolute paths
    for f in files:
        if not os.path.exists(f):
            return {"error": f"File not found: {f}"}

    try:
        if operation == "extract_text":
            return _extract_text(files)
        elif operation == "get_metadata":
            return _get_metadata(files)
        elif operation == "merge":
            return _merge_pdfs(files, output_path)
        else:
            return {"error": f"Unknown operation: {operation}"}
    except Exception as e:
        return {"error": str(e)}

def _extract_text(files):
    results = {}
    for file_path in files:
        text_content = ""
        try:
            # pdfplumber is often better for layout preservation
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            results[file_path] = text_content
        except Exception as e:
             results[file_path] = f"Error extracting text: {e}"
    return results

def _get_metadata(files):
    results = {}
    for file_path in files:
        try:
            reader = pypdf.PdfReader(file_path)
            meta = reader.metadata
            info = {
                "pages": len(reader.pages),
                "title": meta.title if meta else None,
                "author": meta.author if meta else None,
                "producer": meta.producer if meta else None
            }
            results[file_path] = info
        except Exception as e:
            results[file_path] = f"Error reading metadata: {e}"
    return results

def _merge_pdfs(files, output_path):
    merger = pypdf.PdfWriter()
    
    for file_path in files:
        merger.append(file_path)
    
    # Ensure directory exists for output
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)

    merger.write(output_path)
    merger.close()
    
    return {
        "status": "success", 
        "message": f"Merged {len(files)} files to {output_path}",
        "output_path": output_path
    }
