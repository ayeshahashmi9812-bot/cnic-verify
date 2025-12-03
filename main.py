from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import easyocr
import re
import uvicorn

app = FastAPI(title="CNIC Verification API")

# CORS enabling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OCR model loading
reader = easyocr.Reader(['en'])

def extract_cnic_from_image(image_bytes):
    """Image se CNIC number extract karo"""
    try:
        # OCR perform 
        results = reader.readtext(image_bytes, detail=1)
        all_text = ' '.join([result[1] for result in results])
        print(f"Extracted Text: {all_text}")
        
        # Finding CNIC number
        cnic_match = re.search(r'\d{5}-\d{7}-\d{1}', all_text)
        if cnic_match:
            return cnic_match.group(0)
        return None
    except Exception as e:
        print(f" OCR Error: {e}")
        return None

@app.get("/")
async def root():
    return {"message": "CNIC Verification API - Front Image Only"}

@app.post("/verify/cnic")
async def verify_cnic(
    cnic_number: str = Form(..., description="CNIC number to verify"),
    front_image: UploadFile = File(..., description="Front side of CNIC")
):
    try:
        print(f" Verifying CNIC: {cnic_number}")
        
        # Reading image
        image_bytes = await front_image.read()
        
        # Extracting cnic from image
        extracted_cnic = extract_cnic_from_image(image_bytes)
        
        # Verification logic
        if not extracted_cnic:
            return {
                "verified": False,
                "confidence": 0.0,
                "reason": "CNIC number not found in image"
            }
        
        # Match Checking
        verified = extracted_cnic == cnic_number
        confidence = 0.95 if verified else 0.0
        
        # Response
        result = {
            "verified": verified,
            "confidence": confidence,
            "extracted_cnic": extracted_cnic,
            "input_cnic": cnic_number,
            "reason": "Verification successful" if verified else "CNIC mismatch"
        }
        
        print(f" Result: {result}")
        return result
        
    except Exception as e:
        return {
            "verified": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print("CNIC Verification Server Starting...")
    uvicorn.run(app, host="0.0.0.0", port=8000)