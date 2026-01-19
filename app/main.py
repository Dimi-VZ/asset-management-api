from fastapi import FastAPI
from app.api.routes import assets, auth
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Asset Management API",
    description="API for managing company digital assets",
    version="0.1.0"
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(assets.router)


@app.get("/")
def root():
    return {"message": "Asset Management API", "version": "0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/test-email")
def test_email(
    to_email: str,
    subject: str = "Test Email from Asset Management API",
    body: str = "This is a test email to verify SMTP configuration."
):
    from app.services.email import send_email
    
    success = send_email(to_email=to_email, subject=subject, body=body)
    
    if success:
        return {
            "status": "success",
            "message": f"Test email sent successfully to {to_email}"
        }
    else:
        return {
            "status": "error",
            "message": "Failed to send email. Check SMTP configuration."
        }
