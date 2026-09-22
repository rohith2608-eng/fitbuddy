from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from app.database import save_user, save_plan, update_plan, get_original_plan, get_user, SessionLocal
from app.database import User, WorkoutPlan
from app.schemas import UserInput, FeedbackRequest
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: int = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):
    try:
        user_data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )
        
        # Save user to DB
        save_user(
            user_id=user_data.user_id,
            name=user_data.username,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity
        )
        
        # Call Gemini Pro for workout plan
        workout_plan = generate_workout_gemini({
            "goal": user_data.goal,
            "intensity": user_data.intensity
        })
        
        # Save plan to DB
        save_plan(user_id=user_data.user_id, plan=workout_plan)
        
        # Call Gemini Flash for nutrition tip
        nutrition_tip = generate_nutrition_tip_with_flash(user_data.goal)
        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "username": user_data.username,
            "user_id": user_data.user_id,
            "age": user_data.age,
            "weight": user_data.weight,
            "goal": user_data.goal,
            "intensity": user_data.intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: int = Form(...),
    feedback: str = Form(...)
):
    try:
        original = get_original_plan(user_id)
        if not original:
            return templates.TemplateResponse("result.html", {
                "request": request,
                "error": "Original plan not found for this user."
            })
            
        updated = update_workout_plan(original, feedback)
        update_plan(user_id, updated)
        
        # Re-fetch user details to render on the result page
        user = get_user(user_id)
        if not user:
            raise Exception("User not found")
            
        return templates.TemplateResponse("result.html", {
            "request": request,
            "username": user.name,
            "user_id": user.id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": updated,
            "nutrition_tip": "Your plan has been updated! Keep up the good work.",
            "feedback_success": True
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    db = SessionLocal()
    users = db.query(User).all()
    
    user_data = []
    for user in users:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user.id).first()
        user_data.append({
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "original_plan": plan.original_plan if plan else "N/A",
            "updated_plan": plan.updated_plan if plan and plan.updated_plan else "Not updated"
        })
    db.close()
    return templates.TemplateResponse("all_users.html", {
        "request": request,
        "users": user_data
    })
