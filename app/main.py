from fastapi import FastAPI

app = FastAPI(title="Projet DevOps API")


@app.get("/health")
def health():
    return {"status": "ok"}
