import os
import sys

# Add project root to path so we can import app
sys.path.append(os.getcwd())

# Try importing dependencies to check if they are installed
try:
    from reportlab.pdfgen import canvas
    from app.skills.pdf.run import execute
except ImportError as e:
    print(f"Dependency missing: {e}")
    sys.exit(1)

def create_dummy_pdf(filename, text="Hello, World!"):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, text)
    c.save()

def verify():
    test_pdf = "test_skill.pdf"
    pdf2 = "test_skill_2.pdf"
    merged_pdf = "merged_result.pdf"

    # 1. Create a dummy PDF
    try:
        print(f"Creating {test_pdf}...")
        create_dummy_pdf(test_pdf, "Verification Content")
        if not os.path.exists(test_pdf):
             print("Failed to create PDF.")
             return

        # 2. Test Extract Text
        print("Testing extract_text...")
        try:
             res_text = execute({"operation": "extract_text", "files": [os.path.abspath(test_pdf)]})
             print(f"Extract Result: {res_text}")
             # Check if text is somewhere in the values
             found = False
             for val in res_text.values():
                 if "Verification Content" in str(val):
                     found = True
                     break
             
             if found:
                 print("PASS: Text extracted successfully.")
             else:
                 print("FAIL: Text extraction failed.")
        except Exception as e:
             print(f"FAIL: extract_text raised exception: {e}")

        # 3. Test Metadata
        print("Testing get_metadata...")
        try:
             res_meta = execute({"operation": "get_metadata", "files": [os.path.abspath(test_pdf)]})
             print(f"Metadata Result: {res_meta}")
             found = False
             # Check if we got metadata for our file
             for k in res_meta.keys():
                  if test_pdf in k:
                       found = True
             
             if found:
                  print("PASS: Metadata read successfully.")
             else:
                  print("FAIL: Metadata reading failed.")
        except Exception as e:
             print(f"FAIL: get_metadata raised exception: {e}")
             
        # 4. Test Merge (needs a second PDF)
        create_dummy_pdf(pdf2, "Page 2 Content")
        
        print("Testing merge...")
        try:
             res_merge = execute({
                 "operation": "merge", 
                 "files": [os.path.abspath(test_pdf), os.path.abspath(pdf2)],
                 "output_path": os.path.abspath(merged_pdf)
             })
             print(f"Merge Result: {res_merge}")
             if os.path.exists(merged_pdf):
                  print("PASS: Merged file created.")
             else:
                  print("FAIL: Merged file not created.")
        except Exception as e:
             print(f"FAIL: merge raised exception: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_pdf): os.remove(test_pdf)
        if os.path.exists(pdf2): os.remove(pdf2)
        if os.path.exists(merged_pdf): os.remove(merged_pdf)

if __name__ == "__main__":
    verify()
