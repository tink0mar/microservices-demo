from fastapi import FastAPI
from database.database import init_db
from routers.apartements import (
    router as apartments_router,
)  # Corrected the import

app = FastAPI()

# Initialize the database
init_db()


# Include routers
app.include_router(
    apartments_router, prefix="/apartments", tags=["Apartments"]
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
