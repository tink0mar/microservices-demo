import pika
import json
from threading import Thread
from database.database import consumer_db_session  # SQLModel session
from database.models import (
    Apartment,
    Booking,
    BookingUpdate,
)  # SQLModel models


def handle_event(body):
    """
    Process the message and update the database using SQLModel.
    """
    event = json.loads(body)
    try:
        with consumer_db_session() as session:
            if event["event"] == "apartment_added":
                apartment = Apartment(**event["data"])
                session.add(apartment)
                session.commit()
                print(
                    f"Apartment {event['data']['id']} added to the database.",
                    flush=True,
                )

            elif event["event"] == "apartment_removed":
                apartment_id = event["data"]["id"]
                apartment = session.get(Apartment, apartment_id)
                if apartment:
                    session.delete(apartment)
                    session.commit()
                    print(
                        f"Apartment {apartment_id} removed from the database.",
                        flush=True,
                    )
                else:
                    print(f"Apartment {apartment_id} not found.", flush=True)

            elif event["event"] == "booking_added":
                booking = Booking(**event["data"])
                session.add(booking)
                session.commit()
                print(f"Booking created: {event['data']['id']}", flush=True)

            elif event["event"] == "booking_removed":
                booking_id = event["data"]["id"]
                booking = session.get(Booking, booking_id)
                if booking:
                    session.delete(booking)
                    session.commit()
                    print(f"Booking {booking_id} cancelled.", flush=True)
                else:
                    print(f"Booking {booking_id} not found.", flush=True)

            elif event["event"] == "booking_changed":
                booking_id = event["data"]["id"]
                booking_db = session.get(Booking, booking_id)
                if booking_db:

                    booking = BookingUpdate(
                        start_date=event["data"]["start_date"],
                        end_date=event["data"]["end_date"],
                    )

                    booking_data = booking.model_dump(exclude_unset=True)
                    booking_db.sqlmodel_update(booking_data)
                    session.commit()
                    session.refresh(booking_db)

                else:
                    print(f"Booking {booking_id} not found.", flush=True)
    except Exception as e:
        print(f"Error handling event: {str(e)}", flush=True)


def on_message(ch, method, properties, body):
    """
    RabbitMQ callback function. Spawns a new thread to process each message.
    """
    print(
        f"Received message from {method.routing_key}: {body.decode('utf-8')}",
        flush=True,
    )
    thread = Thread(target=handle_event, args=(body,), daemon=True)
    thread.start()


def start_consumer():
    """
    Start the RabbitMQ consumer to listen for events.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    # apartments events
    channel.exchange_declare(
        exchange="apartment_events", exchange_type="fanout"
    )
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange="apartment_events", queue=queue_name)
    channel.basic_consume(
        queue=queue_name, on_message_callback=on_message, auto_ack=True
    )

    # booking events
    channel.exchange_declare(exchange="booking_events", exchange_type="fanout")
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange="booking_events", queue=queue_name)
    channel.basic_consume(
        queue=queue_name, on_message_callback=on_message, auto_ack=True
    )

    print("RabbitMQ Consumer waiting for messages...", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()
