from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.llm import generate_llm_response

app = FastAPI(title="Production AI QA API")

# Initialize Prometheus Metrics
Instrumentator().instrument(app).expose(app)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    tokens_used: int
    latency_seconds: float

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Simplified auth for demo
    if form_data.username == "admin" and form_data.password == "password":
        token = create_access_token(data={"sub": form_data.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, username: str = Depends(get_current_user)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
        
    answer, tokens, latency = await generate_llm_response(request.question)
    return ChatResponse(answer=answer, tokens_used=tokens, latency_seconds=latency)