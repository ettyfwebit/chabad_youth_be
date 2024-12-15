import base64
from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, response_models, database

router = APIRouter(prefix="/children", tags=["children"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[response_models.Child])
def get_children(db: Session = Depends(get_db)):
    return db.query(db_models.Child).all()

@router.get("/getChildrenByBranch", response_model=list[response_models.Child])
def get_children(user_id: int,db: Session = Depends(get_db)):
    branch_manager=db.query(db_models.BranchManager).filter(db_models.BranchManager.login_user_id==user_id).first()
    return db.query(db_models.Child).filter(db_models.Child.branch_manager_id == branch_manager.branch_manager_id).all()

@router.get("/getChildrenByParent", response_model=list[response_models.Child])
def get_children(user_id: int,db: Session = Depends(get_db)):
    parent=db.query(db_models.Parent).filter(db_models.Parent.login_user_id==user_id).first()
    children= db.query(db_models.Child).filter(db_models.Child.parent_id == parent.parent_id).all()
    for child in children:
        if child.image:
         child.image = base64.b64encode(child.image).decode('utf-8')  # Convert
    return children
@router.post("/addNewChild", response_model=response_models.Child)
def create_child(child_data: dict, db: Session = Depends(get_db)):
    
        # פיצול הכתובת
        address = child_data.get("address", {})
        city = address.get("city", "")
        street = address.get("street", "")
        house_number = address.get("houseNumber", "")

        # המרה של ערכים לשדות מתאימים
        health_issue = child_data.get("has_health_issue") == "yes"
        parental_approval = child_data.get("parental_approval") == "yes"

        # חיפוש מזהים עבור branch, class, shirt
        branch_id = (
            db.query(db_models.Branch.branch_id)
            .filter(db_models.Branch.branch_name == child_data.get("branch_name"))
            .scalar()
        )
        branch_manager_id = (
          db.query(db_models.BranchManager.branch_manager_id)  # שמים כאן את הטבלה המתאימה
         .filter(db_models.BranchManager.branch_id == branch_id)
         .scalar()  # מקבלים את ה-branch_manager_id
)
        class_id = (
            db.query(db_models.Class.class_id)
            .filter(db_models.Class.class_name == child_data.get("class"))
            .scalar()
        )
        shirt_id = (
            db.query(db_models.ShirtSize.shirt_size_id)
            .filter(db_models.ShirtSize.shirt_size == child_data.get("shirt_size"))
            .scalar()
        )
        parent_id=(
            db.query(db_models.Parent.parent_id)
            .filter(db_models.Parent.login_user_id==child_data.get("parent_id"))
            .scalar()
        )

        # יצירת אובייקט חדש של ילד
        new_child = db_models.Child(
            parent_id=parent_id,
            first_name=child_data.get("first_name"),
            last_name=child_data.get("last_name"),
            nickname=child_data.get("nickname"),
            date_of_birth=child_data.get("date_of_birth"),
            id_number=child_data.get("id_number"),
            school_name=child_data.get("school_name"),
            city=city,
            street=street,
            house_number=house_number,
            parent_email=child_data.get("parent_email"),
            mother_name=child_data.get("mother_name"),
            mother_phone=child_data.get("mother_phone"),
            father_name=child_data.get("father_name"),
            father_phone=child_data.get("father_phone"),
            branch_id=branch_id,
            class_id=class_id,
            shirt_size_id=shirt_id,
            branch_manager_id=branch_manager_id,
            phone=child_data.get("phone"),
            health_issue=health_issue,
            approval_received=parental_approval,
            image=base64.b64decode(child_data.get("image").split(",")[1]) if child_data.get("image") else None,
        )

        # שמירה במסד
        db.add(new_child)
        db.commit()
        db.refresh(new_child)
        if new_child.image:
          new_child.image = base64.b64encode(new_child.image).decode('utf-8')  # Convert
        return new_child
@router.put("/updateChild", response_model=response_models.Child)
def update_child(child_data: dict, db: Session = Depends(get_db)):
    
        # חיפוש הילד במאגר
        child = db.query(db_models.Child).filter(db_models.Child.child_id == child_data.get("child_id")).first()

        if not child:
            raise HTTPException(status_code=404, detail="Child not found")
        print("Received data:", child_data)
        child_data.pop('image',None)
        # עדכון שדות הילד
        for field, value in child_data.items():
            if hasattr(child, field) and value is not None:
                print(value)
                setattr(child, field, value)

        # שמירת העדכונים
        db.commit()
        db.refresh(child)

        if child.image:
            child.image = base64.b64encode(child.image).decode("utf-8")  # המרה אם התמונה קיימת

        return child
    # except Exception as e:
    #     db.rollback()
    #     raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


    # except IntegrityError:
    #     db.rollback()
    #     raise HTTPException(status_code=400, detail="Child already exists or invalid data")
    # except Exception as e:
    #     db.rollback()
    #     raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
