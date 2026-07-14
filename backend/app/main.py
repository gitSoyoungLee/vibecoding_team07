# from fastapi import FastAPI
# from app.db.init_db import init_db

# app = FastAPI()

# @app.on_event("startup")
# def startup():
#     init_db()

from fastapi import FastAPI, Depends
from typing import List
from sqlalchemy.orm import Session
from backend.db.session import engine, get_db
from backend.db import models
from backend.app import schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Locations API")

@app.get("/locations", response_model=List[schemas.LocationOut])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_locations(db, skip=skip, limit=limit)