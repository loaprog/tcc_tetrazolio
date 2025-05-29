from fastapi import FastAPI
import uvicorn
from routers.project import project
from routers.analise import analise
from database.db import SessionLocal  # sua sessão
from models.user import User
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from configs.config import static_files, templates

app = FastAPI()


app.include_router(project)
app.include_router(analise)

app.mount("/static", static_files, name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Altere para os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/login/", response_class="HTMLResponse")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
         
@app.get("/", response_class="HTMLResponse")
async def homepage(request: Request):
    return templates.TemplateResponse("inicio.html", {"request": request})

@app.get("/analise/{project_id}/{user_id}", response_class="HTMLResponse")
async def analise(request: Request):
    return templates.TemplateResponse("analise.html", {"request": request})


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # Faz um select simples na tabela users
        user = db.query(User).first()
        if user:
            print(f"Usuário encontrado: {user.name} ({user.email})")
        else:
            print("Nenhum usuário encontrado na tabela users.")
    except Exception as e:
        print(f"Erro ao consultar usuários: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level='info', reload=True)
