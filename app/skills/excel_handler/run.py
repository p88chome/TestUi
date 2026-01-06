import pandas as pd
import os

def execute(input_data: dict) -> dict:
    """
    Executes Excel operations.
    """
    operation = input_data.get("operation")
    file_path = input_data.get("file_path")
    sheet_name = input_data.get("sheet_name", 0) # Default to first sheet index for read, "Sheet1" for write usually handled by pandas default
    data = input_data.get("data")

    if not file_path:
        return {"error": "No file_path provided"}

    try:
        if operation == "read_sheet":
            return _read_sheet(file_path, sheet_name)
        elif operation == "write_sheet":
            return _write_sheet(file_path, data, sheet_name)
        else:
            return {"error": f"Unknown operation: {operation}"}
    except Exception as e:
        return {"error": str(e)}

def _read_sheet(file_path, sheet_name):
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        # Read Excel
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        # Convert to list of dicts (records) for JSON serialization
        # fillna('') is important because JSON doesn't handle NaN well
        return df.fillna('').to_dict(orient='records')
    except Exception as e:
        return {"error": f"Pandas read error: {e}"}

def _write_sheet(file_path, data, sheet_name):
    if not data:
        return {"error": "No data provided for writing"}
    
    try:
        # Create directory if needed
        out_dir = os.path.dirname(file_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        df = pd.DataFrame(data)
        
        # If sheet_name is 0 (default from input get), make it explicit string if writing
        if sheet_name == 0: 
            sheet_name = "Sheet1"
            
        df.to_excel(file_path, index=False, sheet_name=sheet_name)
        return {"status": "success", "message": f"Written {len(df)} rows to {file_path}"}
    except Exception as e:
        return {"error": f"Pandas write error: {e}"}
