## Project Description
Python Fast API used to retrieve MLB player statistics to help analyze if players are eligible to be kept.

This API supports the following UI project for uploading the transaction spreadsheet: https://github.com/rroethle7474/JCLKeepersUI

## Technologies
- Python 3.8+
- FastAPI framework
- Uvicorn server
- MLB-StatsAPI for retrieving player data
- Pytesseract and PIL for image processing/OCR
- CORS middleware for cross-origin requests
- Pydantic for data validation

## How to Run
1. Make sure you have Python 3.8+ installed on your system
2. Install required dependencies:
   ```
   pip install fastapi uvicorn pydantic MLB-StatsAPI pillow pytesseract
   ```
3. Install Tesseract OCR on your system:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Mac: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

4. Run the application with:
   ```
   uvicorn main:app --reload
   ```
5. Access the API at http://127.0.0.1:8000

API Endpoints:
- GET http://127.0.0.1:8000/playerdata/?name=[Player Name] - Get player statistics
- POST http://127.0.0.1:8000/upload - Upload images for OCR processing

## Future Work
This API will be used together with Pinecone to retrieve data efficiently for further player analysis for Prop Betting Sites.

## Environment Variables
- No specific environment variables are currently required for basic functionality. (PINECONE variables will be used for future use)
- For production deployment, consider configuring:
  - `PORT`: The port on which the API should run
  - `HOST`: The host address to bind the server to
  - `TESSERACT_CMD`: Path to Tesseract OCR executable if it's not in system PATH

## Support Details for Developers
- **Player Data Endpoint**: 
  - The `/playerdata/` endpoint accepts a player name parameter and an optional position parameter.
  - It determines if a player is eligible to be kept based on specific criteria:
    - Pitchers: Must have pitched at least 50 innings
    - Hitters: Must have at least 130 at-bats
  
- **Upload Endpoint**:
  - The `/upload` endpoint processes image files using OCR (Optical Character Recognition) to extract text.
  - It uses Pytesseract and PIL to process the uploaded images.
  
- **Error Handling**:
  - The API returns appropriate HTTP error codes and messages when issues occur.
  
- **Development Tips**:
  - Use the debug mode with `--reload` flag during development for auto-reloading.
  - For local testing, ensure CORS is properly configured if accessing from a different domain.
  - When working with the MLB-StatsAPI, review their documentation for additional query parameters.

