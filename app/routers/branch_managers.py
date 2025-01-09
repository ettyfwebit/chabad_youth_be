from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, request_models, response_models, database
from app.routers.login_users import hash_password

router = APIRouter(prefix="/branch_managers", tags=["branch_managers"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/", response_model=list[response_models.BranchManagerWithLoginUser])
def get_all_branch_managers_with_login_users(db: Session = Depends(get_db)):
    result = []

    # שליפת כל המנהלי סניפים
    branch_managers = db.query(db_models.BranchManager).all()

    for branch_manager in branch_managers:
        # שליפת משתמש הקשור לכל מנהל סניף
        login_user = db.query(db_models.LoginUser).filter(
            db_models.LoginUser.login_user_id == branch_manager.login_user_id
        ).first()

        if login_user:
            # המרת הנתונים למודלים של Pydantic
            result.append(
                response_models.BranchManagerWithLoginUser(
                    branch_manager=response_models.BranchManager.from_orm(branch_manager),
                    login_user=response_models.LoginUser.from_orm(login_user),
                )
            )

    return result
@router.get("/getAll", response_model=list[response_models.BranchManager])
def get_all_branch_managers_with_login_users(db: Session = Depends(get_db)):
   return db.query(db_models.BranchManager).all()

@router.get("/{branch_manager_id}", response_model=response_models.BranchManager)
def get_branch_manager(branch_manager_id: int, db: Session = Depends(get_db)):
    # שליפת פרטי מנהל הסניף
    branch_manager = db.query(db_models.BranchManager).filter(db_models.BranchManager.branch_manager_id == branch_manager_id).first()
    if not branch_manager:
        raise HTTPException(status_code=404, detail="Branch manager not found")
    return branch_manager


@router.post("/", response_model=response_models.BranchManagerWithLoginUser)
def add_branch_manager(
    branch_manager_data: request_models.BranchManagerCreate,
    db: Session = Depends(get_db)
):
    print(branch_manager_data)
    try:
        password_hash = hash_password(branch_manager_data.login_user.password)  # יצירת ה-password_hash

        login_user = db_models.LoginUser(
            user_name=branch_manager_data.login_user.user_name,
            chat_id="",
            email=branch_manager_data.login_user.email,
            phone=branch_manager_data.login_user.phone,
            password_hash=password_hash,  # שמירת ה-password_hash
            role_id=2  # role_id תמיד 2
        )
        
        # שמירת המשתמש החדש בבסיס הנתונים
        db.add(login_user)
        db.commit()
        db.refresh(login_user)

        # יצירת אובייקט BranchManager חדש
        branch_manager = db_models.BranchManager(
            login_user_id=login_user.login_user_id,
            branch_id=branch_manager_data.branch_manager.branch_id,
            additional_info=""
        )

        # שמירת מנהל הסניף החדש בבסיס הנתונים
        db.add(branch_manager)
        db.commit()
        db.refresh(branch_manager)

        return response_models.BranchManagerWithLoginUser(
            branch_manager=response_models.BranchManager.from_orm(branch_manager),
            login_user=response_models.LoginUser.from_orm(login_user)
        )

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error: " + str(e.orig))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="An error occurred: " + str(e))

@router.put("/{branch_manager_id}", response_model=response_models.BranchManagerWithLoginUser)
def update_branch_manager(
    branch_manager_id: int,
    branch_manager_data: request_models.BranchManagerUpdate,
    db: Session = Depends(get_db)
):
    print("user_name")
    # שליפת מנהל הסניף
    branch_manager = db.query(db_models.BranchManager).filter(
        db_models.BranchManager.branch_manager_id == branch_manager_id
    ).first()

    if not branch_manager:
        raise HTTPException(status_code=404, detail="Branch manager not found")

    # עדכון פרטי המשתמש
    login_user = db.query(db_models.LoginUser).filter(
        db_models.LoginUser.login_user_id == branch_manager.login_user_id
    ).first()

    if not login_user:
        raise HTTPException(status_code=404, detail="Login user not found")

    login_user.email = branch_manager_data.login_user.email
    login_user.phone = branch_manager_data.login_user.phone
    print("user name",branch_manager_data.login_user.user_name)
    login_user.user_name=branch_manager_data.login_user.user_name
    # עדכון פרטי מנהל הסניף
    branch_manager.branch_id = branch_manager_data.branch_manager.branch_id

    db.commit()
    db.refresh(branch_manager)
    db.refresh(login_user)

    return response_models.BranchManagerWithLoginUser(
        branch_manager=response_models.BranchManager.from_orm(branch_manager),
        login_user=response_models.LoginUser.from_orm(login_user)
    )

