from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List
from notes_api.config import config
from notes_api.database import db_manager
from notes_api.models import Note, NoteCreate, NoteUpdate
import uvicorn

app = FastAPI(title="LilAPI 2")

# CORS for allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Notes API. Visit /docs for Swagger UI."}

# JWT setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock user DB with env-based credentials
fake_users_db = {
    config.TEST_USER: {
        "username": config.TEST_USER,
        "hashed_password": pwd_context.hash(config.TEST_PASSWORD),
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.on_event("startup")
async def startup():
    await db_manager.connect()

@app.on_event("shutdown")
async def shutdown():
    await db_manager.disconnect()

@app.get("/notes", response_model=List[Note])
async def get_notes(current_user: dict = Depends(get_current_user)):
    notes = await db_manager.get_notes()
    return notes

@app.post("/notes", response_model=Note)
async def create_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    note_id = await db_manager.create_note(note.dict())
    return await db_manager.get_note(note_id)

@app.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: int, current_user: dict = Depends(get_current_user)):
    note = await db_manager.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=Note)
async def update_note(
    note_id: int, note: NoteUpdate, current_user: dict = Depends(get_current_user)
):
    note_data = {k: v for k, v in note.dict().items() if v is not None}
    if not note_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    updated_note = await db_manager.update_note(note_id, note_data)
    if updated_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int, current_user: dict = Depends(get_current_user)):
    await db_manager.delete_note(note_id)
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
