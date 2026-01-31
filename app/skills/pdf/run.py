"""
PDF Manager Skill
Enhanced PDF processing with text extraction, table extraction, metadata, merge, and split.
"""
import os
import logging
from typing import Dict, List, Any, Union

import pypdf
import pdfplumber

logger = logging.getLogger(__name__)


def execute(input_data: dict) -> dict:
    """
    Executes PDF operations.
    
    Input:
    {
        "operation": "extract_text" | "extract_tables" | "get_metadata" | "merge" | "split",
        "files": ["/path/to/a.pdf", ...],
        "output_path": "/path/to/output" (optional),
        "pages": "1-5" or [1, 3, 5] (optional, for split)
    }
    """
    operation = input_data.get("operation")
    files = input_data.get("files", [])
    output_path = input_data.get("output_path", "merged_output.pdf")
    pages = input_data.get("pages")

    # Validate files
    if not files:
        return {"status": "error", "error": "No files provided"}
    
    # Ensure files is a list
    if isinstance(files, str):
        files = [files]
    
    # Validate file existence
    for f in files:
        if not os.path.exists(f):
            return {"status": "error", "error": f"File not found: {f}"}

    try:
        if operation == "extract_text":
            return _extract_text(files)
        elif operation == "extract_tables":
            return _extract_tables(files)
        elif operation == "get_metadata":
            return _get_metadata(files)
        elif operation == "merge":
            return _merge_pdfs(files, output_path)
        elif operation == "split":
            return _split_pdf(files[0], output_path, pages)
        else:
            return {"status": "error", "error": f"Unknown operation: {operation}. Supported: extract_text, extract_tables, get_metadata, merge, split"}
    except Exception as e:
        logger.exception(f"PDF operation failed: {operation}")
        return {"status": "error", "error": str(e)}


def _extract_text(files: List[str]) -> Dict[str, Any]:
    """Extract text from PDF files using pdfplumber for better layout preservation."""
    results = {}
    for file_path in files:
        text_content = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_content += f"--- Page {i} ---\n{page_text}\n\n"
            results[os.path.basename(file_path)] = {
                "status": "success",
                "text": text_content,
                "char_count": len(text_content)
            }
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            results[os.path.basename(file_path)] = {
                "status": "error", 
                "error": f"Error extracting text: {e}"
            }
    return {"status": "success", "results": results}


def _extract_tables(files: List[str]) -> Dict[str, Any]:
    """Extract tables from PDF files using pdfplumber."""
    results = {}
    for file_path in files:
        try:
            all_tables = []
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    for j, table in enumerate(tables, 1):
                        if table and len(table) > 0:
                            # Convert table to dict format with headers
                            if len(table) > 1:
                                headers = table[0] if table[0] else [f"col_{k}" for k in range(len(table[1]))]
                                rows = table[1:]
                                all_tables.append({
                                    "page": i,
                                    "table_index": j,
                                    "headers": headers,
                                    "data": rows,
                                    "row_count": len(rows)
                                })
            results[os.path.basename(file_path)] = {
                "status": "success",
                "tables": all_tables,
                "table_count": len(all_tables)
            }
        except Exception as e:
            logger.error(f"Error extracting tables from {file_path}: {e}")
            results[os.path.basename(file_path)] = {
                "status": "error",
                "error": f"Error extracting tables: {e}"
            }
    return {"status": "success", "results": results}


def _get_metadata(files: List[str]) -> Dict[str, Any]:
    """Get metadata from PDF files using pypdf."""
    results = {}
    for file_path in files:
        try:
            reader = pypdf.PdfReader(file_path)
            meta = reader.metadata
            info = {
                "status": "success",
                "pages": len(reader.pages),
                "title": meta.title if meta else None,
                "author": meta.author if meta else None,
                "subject": meta.subject if meta else None,
                "creator": meta.creator if meta else None,
                "producer": meta.producer if meta else None,
                "creation_date": str(meta.creation_date) if meta and meta.creation_date else None,
            }
            results[os.path.basename(file_path)] = info
        except Exception as e:
            logger.error(f"Error reading metadata from {file_path}: {e}")
            results[os.path.basename(file_path)] = {
                "status": "error",
                "error": f"Error reading metadata: {e}"
            }
    return {"status": "success", "results": results}


def _merge_pdfs(files: List[str], output_path: str) -> Dict[str, Any]:
    """Merge multiple PDF files into one."""
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
        "message": f"Successfully merged {len(files)} files",
        "output_path": os.path.abspath(output_path),
        "merged_count": len(files)
    }


def _split_pdf(file_path: str, output_path: str, pages: Union[str, List[int], None]) -> Dict[str, Any]:
    """Split PDF into separate pages or specified page ranges."""
    reader = pypdf.PdfReader(file_path)
    total_pages = len(reader.pages)
    
    # Parse pages parameter
    if pages is None:
        page_list = list(range(total_pages))
    elif isinstance(pages, str):
        # Parse range like "1-5" or "1,3,5"
        page_list = []
        for part in pages.split(","):
            if "-" in part:
                start, end = part.split("-")
                page_list.extend(range(int(start) - 1, int(end)))
            else:
                page_list.append(int(part) - 1)
    else:
        page_list = [p - 1 for p in pages]  # Convert to 0-indexed
    
    # Ensure output directory exists
    if not output_path:
        output_path = os.path.dirname(file_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_files = []
    
    for page_num in page_list:
        if 0 <= page_num < total_pages:
            writer = pypdf.PdfWriter()
            writer.add_page(reader.pages[page_num])
            
            output_file = os.path.join(output_path, f"{base_name}_page_{page_num + 1}.pdf")
            writer.write(output_file)
            writer.close()
            output_files.append(output_file)
    
    return {
        "status": "success",
        "message": f"Successfully split into {len(output_files)} files",
        "output_files": output_files,
        "total_pages": total_pages
    }
