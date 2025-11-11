import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import ContactMessage

app = FastAPI(title="Agency API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Agency backend running"}

# Contact form endpoint - stores in MongoDB
@app.post("/api/contact")
def submit_contact(payload: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", payload)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple products/templates showcase endpoint (static for now)
class TemplateItem(BaseModel):
    title: str
    description: str
    image: str
    url: str

@app.get("/api/templates", response_model=List[TemplateItem])
def get_templates():
    return [
        TemplateItem(
            title="Minimal Chic",
            description="Clean, conversion-focused fashion template with fast performance.",
            image="https://images.unsplash.com/photo-1520975922284-9bcd8f589a03?q=80&w=1200&auto=format&fit=crop",
            url="#minimal"
        ),
        TemplateItem(
            title="Tech Pulse",
            description="Sleek electronics layout with bold hero and product grids.",
            image="https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop",
            url="#tech"
        ),
        TemplateItem(
            title="Beauty Glow",
            description="Glassmorphic beauty brand design with soft gradients.",
            image="https://images.unsplash.com/photo-1505575972945-2307cba3f9c8?q=80&w=1200&auto=format&fit=crop",
            url="#beauty"
        ),
    ]

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
