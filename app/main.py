from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Projet DevOps API")

tasks: list[dict] = []
next_id = 1


class TaskCreate(BaseModel):
    title: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return tasks


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    global next_id
    new_task = {"id": next_id, "title": task.title}
    tasks.append(new_task)
    next_id += 1
    return new_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            tasks.remove(t)
            return
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/")
def root():
    return {"message": "API DevOps déployée automatiquement"}
