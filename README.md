## Project Description
Python Flask API used to retrieve MLB player statistics to help analyze if players are eligible to be kept.

This API supports the following UI project for uploading the transaction spreadsheet: https://github.com/rroethle7474/JCLKeepersUI

## Technologies
- Python 3.8+
- Flask framework
- Flask-CORS for cross-origin requests
- MLB-StatsAPI for retrieving player data
- Pytesseract and PIL for image processing/OCR
- Pinecone for vector database operations

 - NOTE: TRANSFORMERS LIBRARY FOR THE PINECONE SERVICE NEEDS TO HAVE A NUMPY VERSION LESS THAN 2 (3/24/25)
 https://stackoverflow.com/questions/78863932/runtimeerror-numpy-is-not-available-transformers

## How to Run
1. Make sure you have Python 3.8+ installed on your system
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install Tesseract OCR on your system:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Mac: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

4. Run the application with:
   ```
   python app.py
   ```
5. Access the API at http://127.0.0.1:5000

API Endpoints:
- GET http://127.0.0.1:5000/api/player - Player-related endpoints
- GET http://127.0.0.1:5000/api/gameday - Gameday-related endpoints
- GET http://127.0.0.1:5000/api/team - Team-related endpoints
- GET http://127.0.0.1:5000/api/document - Document-related endpoints

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
  - The `/api/player` endpoints handle player-related operations
  - It determines if a player is eligible to be kept based on specific criteria:
    - Pitchers: Must have pitched at least 50 innings
    - Hitters: Must have at least 130 at-bats
  
- **Upload Endpoint**:
  - The `/api/document` endpoints process image files using OCR (Optical Character Recognition) to extract text.
  - It uses Pytesseract and PIL to process the uploaded images.
  
- **Error Handling**:
  - The API returns appropriate HTTP error codes and messages when issues occur.
  
- **Development Tips**:
  - The application runs in debug mode by default during development for auto-reloading.
  - CORS is enabled for all routes to allow cross-origin requests.
  - When working with the MLB-StatsAPI, review their documentation for additional query parameters.

