
# AI Campus Admin Agent – Setup Instructions

## 1. Clone the Repository
```bash
git clone <your-repo-url>
cd AI-Campus-Admin-Agent
```

## 2. Install Dependencies
```bash
poetry install
```

## 3. Configure Environment Variables
- Create a `.env` file in the project root.
- Add your database connection string and Gemini/OpenAI API key as given in .env.example:
	```
	DB_URL=your_database_url
	GEMINI_API_KEY=your_gemini_api_key
	```

## 4. Start the Database
- Make sure MongoDB is running and accessible.

## 5. Run the FastAPI Server
 - poetry run uvicorn backend.main:app --reload


## 7. Test Endpoints
- Use Postman or curl to test:
	- `/chat`
	- `/chat/stream`
	- `/students`
	- `/analytics`
	- `/optional/faq`

## Optional: Campus FAQ Tools

The agent supports different tools for:
- student data- list, add, updaate, delete
- analytics - show summary or analytics
- Event schedule

These can be accessed via chat endpoints by asking questions like:
- "add student with name, id, department, email."
- "delete student of following details"
- "Show me upcoming campus events."
- "show me summary of analytics"
