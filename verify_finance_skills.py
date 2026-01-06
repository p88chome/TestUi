import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

# Try importing dependencies
try:
    import pandas
    import openpyxl
    import docx
    from app.skills.excel_handler.run import execute as execute_excel
    from app.skills.docx_writer.run import execute as execute_word
except ImportError as e:
    print(f"Dependency missing: {e}")
    sys.exit(1)

def verify():
    print("=== Verifying Finance & Legal Skills ===")
    
    # --- Test 1: Excel Handler ---
    excel_file = "test_finance.xlsx"
    print(f"\n[Excel] Creating {excel_file}...")
    
    data = [
        {"Account": "Revenue", "Amount": 100000},
        {"Account": "COGS", "Amount": 40000},
        {"Account": "Net Income", "Amount": 60000}
    ]
    
    try:
        # Write
        res_write = execute_excel({"operation": "write_sheet", "file_path": os.path.abspath(excel_file), "data": data})
        print(f"Write Result: {res_write}")
        
        # Read
        print("[Excel] Reading back...")
        res_read = execute_excel({"operation": "read_sheet", "file_path": os.path.abspath(excel_file)})
        # res_read should be list of dicts
        print(f"Read Result: {res_read}")
        
        if len(res_read) == 3 and res_read[0]['Account'] == "Revenue":
            print("PASS: Excel Read/Write successful.")
        else:
            print("FAIL: Excel content mismatch.")
            
    except Exception as e:
         print(f"FAIL: Excel operation error: {e}")

    # --- Test 2: Word Writer ---
    docx_file = "test_audit_report.docx"
    print(f"\n[Word] Creating {docx_file}...")
    
    content = [
        "# Audit Report 2024",
        "We have audited the accompanying financial statements...",
        "## Opinion",
        "In our opinion, the financial statements present fairly..."
    ]
    
    try:
        # Create Report
        res_create = execute_word({"operation": "create_report", "output_path": os.path.abspath(docx_file), "content": content})
        print(f"Create Result: {res_create}")
        
        if os.path.exists(docx_file):
             print("PASS: Word document created.")
        else:
             print("FAIL: Word document not found.")
             
        # Append Table
        print("[Word] Appending table...")
        headers = ["Item", "Status"]
        rows = [["Cash", "Verified"], ["Inventory", "Verified"]]
        
        res_append = execute_word({"operation": "append_table", "output_path": os.path.abspath(docx_file), "headers": headers, "rows": rows})
        print(f"Append Result: {res_append}")
        
    except Exception as e:
        print(f"FAIL: Word operation error: {e}")

    # Cleanup
    if os.path.exists(excel_file): os.remove(excel_file)
    if os.path.exists(docx_file): os.remove(docx_file)

if __name__ == "__main__":
    verify()
