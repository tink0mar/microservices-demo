import pika
import json
from threading import Thread
from database.models import Apartment, Booking
from database.database import (
    consumer_db_session,
)  # Now using the SQLModel session


def process_message(body):
    """
    Process a message received from RabbitMQ and update the local database.
    """
    try:
        event = json.loads(body)
        with consumer_db_session() as session:
            if event["event"] == "apartment_added":
                # Add apartment to the database

                apartment = Apartment(**event["data"])
                session.add(apartment)
                session.commit()
                print(
                    f"Apartment {event['data']['id']} added to the database.",
                    flush=True,
                )
            elif event["event"] == "apartment_removed":
                # Remove apartment from the database
                apartment = session.get(Apartment, event["data"]["id"])
                if apartment:
                    session.delete(apartment)
                    session.commit()
                    print(
                        f"Apartment {event['data']['id']} removed from the database.",
                        flush=True,
                    )
                else:
                    print(
                        f"Apartment {event['data']['id']} not found.",
                        flush=True,
                    )
    except Exception as e:
        print(f"Error processing message: {e}", flush=True)


def on_message(ch, method, properties, body):
    """
    RabbitMQ callback function. Spawns a new thread to process each message.
    """
    print(f"Received message: {body}", flush=True)

    thread = Thread(target=process_message, args=(body,), daemon=True)
    thread.start()


def start_consumer():
    """
    Start RabbitMQ consumer in a blocking fashion, using threads for processing.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange="apartment_events", exchange_type="fanout"
    )

    result = channel.queue_declare(queue="", exclusive=True)

    queue_name = result.method.queue

    channel.queue_bind(exchange="apartment_events", queue=queue_name)

    print("RabbitMQ Consumer waiting for messages...", flush=True)

    # Set up the consumer
    channel.basic_consume(
        queue=queue_name, on_message_callback=on_message, auto_ack=True
    )

    channel.start_consuming()
