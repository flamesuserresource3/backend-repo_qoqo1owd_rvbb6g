import os
import smtplib
from email.message import EmailMessage
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from database import create_document

app = FastAPI(title="Ananda Fadhilah Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: Optional[str] = Field(None, max_length=150)
    message: str = Field(..., min_length=10, max_length=5000)


@app.get("/")
def read_root():
    return {"message": "Portfolio backend running"}


@app.post("/contact")
def submit_contact(payload: ContactRequest):
    # Store message in database
    try:
        doc_id = create_document("contactmessage", payload.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)[:200]}")

    # Try to send email if SMTP is configured
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    to_email = os.getenv("TO_EMAIL") or os.getenv("OWNER_EMAIL")

    sent = False
    send_error = None
    if smtp_host and smtp_user and smtp_pass and to_email:
        try:
            msg = EmailMessage()
            msg["Subject"] = payload.subject or f"New Portfolio Inquiry from {payload.name}"
            msg["From"] = smtp_user
            msg["To"] = to_email
            msg.set_content(
                f"Name: {payload.name}\n"
                f"Email: {payload.email}\n"
                f"Subject: {payload.subject or 'N/A'}\n\n"
                f"Message:\n{payload.message}\n\n"
                f"Document ID: {doc_id}\n"
            )

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                sent = True
        except Exception as e:
            send_error = str(e)

    return {
        "ok": True,
        "stored_id": doc_id,
        "email_sent": sent,
        "note": None if sent else (
            "Email not sent (SMTP not configured)" if not send_error and not sent else f"Email send failed: {send_error}"
        ),
    }


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
