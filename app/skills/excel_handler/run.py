"""
Excel Handler Skill
Enhanced Excel processing with read, write, analyze, and multi-sheet support.
"""
import pandas as pd
import os
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)


def execute(input_data: dict) -> dict:
    """
    Executes Excel operations.
    
    Input:
    {
        "operation": "read_sheet" | "write_sheet" | "analyze" | "list_sheets",
        "file_path": "/path/to/file.xlsx",
        "sheet_name": "Sheet1" (optional),
        "data": [...] (for write_sheet),
        "columns": ["col1", "col2"] (optional, for read_sheet)
    }
    """
    operation = input_data.get("operation")
    file_path = input_data.get("file_path")
    sheet_name = input_data.get("sheet_name", 0)
    data = input_data.get("data")
    columns = input_data.get("columns")

    if not file_path:
        return {"status": "error", "error": "No file_path provided"}

    try:
        if operation == "read_sheet":
            return _read_sheet(file_path, sheet_name, columns)
        elif operation == "write_sheet":
            return _write_sheet(file_path, data, sheet_name)
        elif operation == "analyze":
            return _analyze_data(file_path, sheet_name)
        elif operation == "list_sheets":
            return _list_sheets(file_path)
        else:
            return {
                "status": "error", 
                "error": f"Unknown operation: {operation}. Supported: read_sheet, write_sheet, analyze, list_sheets"
            }
    except Exception as e:
        logger.exception(f"Excel operation failed: {operation}")
        return {"status": "error", "error": str(e)}


def _read_sheet(file_path: str, sheet_name: Union[str, int], columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """Read Excel sheet and return as list of dicts."""
    if not os.path.exists(file_path):
        return {"status": "error", "error": f"File not found: {file_path}"}
    
    try:
        # Read Excel
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Filter columns if specified
        if columns:
            available_cols = [c for c in columns if c in df.columns]
            if available_cols:
                df = df[available_cols]
        
        # Handle NaN and convert dates
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S').fillna('')
        
        df = df.fillna('')
        
        return {
            "status": "success",
            "data": df.to_dict(orient='records'),
            "row_count": len(df),
            "columns": list(df.columns)
        }
    except Exception as e:
        logger.error(f"Error reading Excel: {e}")
        return {"status": "error", "error": f"Read error: {e}"}


def _write_sheet(file_path: str, data: Union[List[Dict], List[List]], sheet_name: Union[str, int]) -> Dict[str, Any]:
    """Write data to Excel file."""
    if not data:
        return {"status": "error", "error": "No data provided for writing"}
    
    try:
        # Create directory if needed
        out_dir = os.path.dirname(file_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        df = pd.DataFrame(data)
        
        # Convert sheet_name to string if it's 0 (default)
        if sheet_name == 0:
            sheet_name = "Sheet1"
            
        df.to_excel(file_path, index=False, sheet_name=sheet_name)
        
        return {
            "status": "success", 
            "message": f"Successfully written {len(df)} rows to {os.path.basename(file_path)}",
            "file_path": os.path.abspath(file_path),
            "row_count": len(df),
            "columns": list(df.columns)
        }
    except Exception as e:
        logger.error(f"Error writing Excel: {e}")
        return {"status": "error", "error": f"Write error: {e}"}


def _analyze_data(file_path: str, sheet_name: Union[str, int]) -> Dict[str, Any]:
    """Analyze Excel data and return statistics."""
    if not os.path.exists(file_path):
        return {"status": "error", "error": f"File not found: {file_path}"}
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Basic statistics
        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": []
        }
        
        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null_count": int(df[col].notna().sum()),
                "null_count": int(df[col].isna().sum())
            }
            
            # Add numeric statistics
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info.update({
                    "min": float(df[col].min()) if pd.notna(df[col].min()) else None,
                    "max": float(df[col].max()) if pd.notna(df[col].max()) else None,
                    "mean": float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                    "sum": float(df[col].sum()) if pd.notna(df[col].sum()) else None
                })
            elif pd.api.types.is_string_dtype(df[col]):
                col_info["unique_count"] = int(df[col].nunique())
                # Sample values
                samples = df[col].dropna().head(5).tolist()
                col_info["sample_values"] = samples
            
            stats["columns"].append(col_info)
        
        return {
            "status": "success",
            "analysis": stats
        }
    except Exception as e:
        logger.error(f"Error analyzing Excel: {e}")
        return {"status": "error", "error": f"Analyze error: {e}"}


def _list_sheets(file_path: str) -> Dict[str, Any]:
    """List all sheets in an Excel file."""
    if not os.path.exists(file_path):
        return {"status": "error", "error": f"File not found: {file_path}"}
    
    try:
        xl = pd.ExcelFile(file_path)
        sheets_info = []
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet_name)
            sheets_info.append({
                "name": sheet_name,
                "row_count": len(df),
                "column_count": len(df.columns)
            })
        
        return {
            "status": "success",
            "sheets": sheets_info,
            "sheet_count": len(sheets_info)
        }
    except Exception as e:
        logger.error(f"Error listing sheets: {e}")
        return {"status": "error", "error": f"List sheets error: {e}"}
