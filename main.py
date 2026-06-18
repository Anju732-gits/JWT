from fastapi import FastAPI
from auth import create_token, get_current_user, hash_password, verify_password
from model import LoginUser, RegisterUser, CategoryCreate, TaskCreate, TaskUpdate
#from fastapi.security import OAuth2PasswordRequest, Oauth2PasswordBearer
from fastapi.exceptions import HTTPException
from fastapi import Depends
from database import supabase

app = FastAPI()

@app.get("/")

def home():
    return {"message": "Welcome to the JWT Project!"}

@app.post("/register")
def register(user: RegisterUser):
    existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)       #hashing the password before storing it in the database
    new_user = supabase.table("users").insert({
        "email": user.email, 
        "password": hashed_password,
        "name": user.name
    }).execute()

    return {"message": "User registered successfully",
            "user_id": new_user.data[0]}

@app.post("/login")
def login(user: LoginUser):
    res = supabase.table("users").select("*").eq("email", user.email).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    db_user = res.data[0]
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    token = create_token({"user_id": db_user["id"]})     #creating the token during login
    return {"message": "Login successful", "token": token}

@app.post("/categories")
def create_category(category: CategoryCreate, user_id: str = Depends(get_current_user)):
    res = supabase.table("categories").insert({
        "name": category.name,
        "user_id": user_id
    }).execute()
    return {"message": "Category created successfully", "category_id": res.data[0]}

@app.post("/tasks")
def create_task(task: TaskCreate, user_id: str = Depends(get_current_user)):
    res = supabase.table("tasks").insert({
        "title": task.title,
        "description": task.description,
        "category_id": task.category_id,
        "user_id": user_id
    }).execute()
    return {"message": "Task created successfully", "task_id": res.data[0]}

@app.get("/categories")
def get_categories(user_id: str = Depends(get_current_user)):
    res = supabase.table("categories").select("*").eq("user_id", user_id).execute()
    return {"categories": res.data}

@app.get("/tasks")
def get_tasks(user_id: str = Depends(get_current_user)):
    res = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    return {"tasks": res.data}

@app.get("/get_tasks/{task_id}")
def get_task(task_id: str, user_id: str = Depends(get_current_user)):
    res = supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task": res.data[0]}

@app.delete("/delete_task/{task_id}")
def delete_task(task_id: str, user_id: str = Depends(get_current_user)):
    res = supabase.table("tasks").delete().eq("id", task_id).eq("user_id", user_id).execute()
    if res.count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}