from distutils.util import execute
from typing import Counter, Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
import requests
import json

models.Base.metadata.create_all(bind=engine)

response_users = requests.get('https://jsonplaceholder.typicode.com/users')
response_posts = requests.get('https://jsonplaceholder.typicode.com/posts')

app = FastAPI()

while True:

    try: 
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='awdrg153', cursor_factory=RealDictCursor)

        cursor = conn.cursor() #aby sa dali pouzivat SQL prikazy
        print("Database connection was succesfull!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)


@app.get("/")
def root():
    return {"message": "Welcome"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    UserID = new_post.userid

    for Couneter in range (len(response_users.json())):
        UserID_fetch = response_users.json()[Couneter]['id']
        if UserID == UserID_fetch:
            break

    if UserID != UserID_fetch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {UserID} was not found")

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@app.get("/posts/id/{id}", response_model=schemas.Post)
def get_posts(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    
    if not post:
        
        for Couneter in range (len(response_posts.json())):
            PostID_fetch = response_posts.json()[Couneter]['id']
            
            if id == PostID_fetch:
                #cursor.execute("""INSERT INTO posts (userId,id,title,body) VALUES (%s, %s, %s) RETURNING * """, response_posts.json()[Couneter]['id'])
                #Post_fetch = response_posts.json()[Couneter]
                raise HTTPException(status_code=status.HTTP_302_FOUND, detail=f"post with id: {id} was found with external API")
                
        # data = json.loads(response_posts.text)[Couneter]
        # print(response_posts.userId)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    return post


@app.get("/posts/userid/{userid}", response_model=List[schemas.Post])
def get_posts(userid: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.userid == userid).all()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {userid} was not found")

    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    
    deleted_post_id = db.query(models.Post).filter(models.Post.id == id)
    if deleted_post_id.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    deleted_post_id.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post )
def update_post(id: int, updated_post:schemas.PostCreate, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()