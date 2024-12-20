from fastapi import FastAPI
from contextlib import asynccontextmanager
from threading import Thread
from consumer import start_consumer
from routers.bookings import router as bookings_router
from initialization import initialize_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context for the FastAPI app to manage RabbitMQ consumer.
    """
    # Initialize the database
    from database.database import init_db
    init_db()

    initialize_data()

    # Start RabbitMQ consumer in a separate thread
    thread = Thread(target=start_consumer, daemon=True)  # Daemonize thread
    thread.start()
    print("RabbitMQ Consumer started.", flush=True)

    try:
        yield  # Important: Separates startup and shutdown
    finally:
        print("Stopping RabbitMQ Consumer...", flush=True)
        thread.join(timeout=5)  # Ensure thread finishes gracefully (optional)

app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
