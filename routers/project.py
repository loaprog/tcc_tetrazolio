from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.project import Project, ProjectCreate, ProjectUpdate
from models.user import User
from configs.config import static_files, templates

project = APIRouter(prefix="/projects", tags=["projects"])



@project.post("/create_project/")
async def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    if not project_data.user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    user = db.query(User).filter(User.id_user == project_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuário com id {project_data.user_id} não encontrado")

    try:
        new_project = Project(
            name=project_data.name,
            companies=project_data.companies,
            crop_type=project_data.crop_type,
            cultivar=project_data.cultivar,
            description=project_data.description,
            start_date=project_data.start_date,
            user_id=project_data.user_id,
            status=project_data.status or "active",
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return {"message": "Projeto criado com sucesso!", "project_id": new_project.id_project}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar projeto: {str(e)}")




@project.get("/get_projects/{user_id}")
async def get_projects(user_id: int, db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.user_id == user_id).all()
    return projects




@project.get("/get_project_by_id/{project_id}/{user_id}")
async def get_project_by_id(project_id: int, user_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id_project == project_id, Project.user_id == user_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail=f"Projeto com id {project_id} não encontrado para o usuário com id {user_id}")
    
    return project




@project.get("/update_project/{project_id, user_id}")
async def update_project(project_id: int, user_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    project_to_update = db.query(Project).filter(Project.id_project == project_id, Project.user_id == user_id).first()
    
    if not project_to_update:
        raise HTTPException(status_code=404, detail=f"Projeto com id {project_id} não encontrado para o usuário com id {user_id}")
    
    try:
        for key, value in project.dict().items():
            setattr(project_to_update, key, value)
        db.commit()
        db.refresh(project_to_update)
        return {"message": "Projeto atualizado com sucesso!", "project_id": project_to_update.id_project}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar projeto: {str(e)}")
    



@project.delete("/delete_project/{project_id, user_id}")
async def delete_project(project_id: int, user_id: int, db: Session = Depends(get_db)):
    project_to_delete = db.query(Project).filter(Project.id_project == project_id, Project.user_id == user_id).first()
    if not project_to_delete:
        raise HTTPException(status_code=404, detail=f"Projeto com id {project_id} não encontrado para o usuário com id {user_id}")
    
    try:
        db.delete(project_to_delete)
        db.commit()
        return {"message": "Projeto deletado com sucesso!", "project_id": project_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar projeto: {str(e)}")