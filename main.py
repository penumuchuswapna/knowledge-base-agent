from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from api.drive_utils import search_drive_files
from api.jira_utils import search_jira_issues
from api.github_utils import search_github_repos
from api.gitlab_utils import search_gitlab_projects
from api.mistral_utils import generate_answer

app = FastAPI()

# Enable CORS so Streamlit can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Request & response models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    needs_review: bool = False

# New /query endpoint
@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    user_query = request.query
    print(f"Received query: {user_query}")

    # Dummy response logic
    answer = f"You asked: '{user_query}'. Here is a dummy answer for now."
    needs_review = "confidential" in user_query.lower()

    return QueryResponse(answer=answer, needs_review=needs_review)

@app.get("/search-drive/")
def search_drive(query: str = Query(...)):
    try:
        results = search_drive_files(query)
        return {"results": results}
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail="Google Drive credentials not found. Please set up credentials.json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-jira/")
def search_jira(query: str = Query(...)):
    try:
        results = search_jira_issues(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-github/")
def search_github(query: str = Query(...)):
    try:
        results = search_github_repos(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-gitlab/")
def search_gitlab(query: str = Query(...)):
    try:
        results = search_gitlab_projects(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate-answer/")
def get_ai_answer(query: str = Query(...), context: str = Query(...)):
    try:
        answer = generate_answer(query, context)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from api import query  # Assuming your router is in api/query.py

# app = FastAPI()

# # CORS for Streamlit
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Restrict to specific origin in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include the route
# app.include_router(query.router)
