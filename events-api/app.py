import os, json, threading
from flask import Flask, request, jsonify
from redis import Redis
import pika
from dotenv import load_dotenv
load_dotenv()

app    = Flask(__name__)
cache  = Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
EVENTS_KEY = "critical:events"     # lista no Redis

def cache_events(events):
    cache.set(EVENTS_KEY, json.dumps(events), ex=3600)

def load_events():
    raw = cache.get(EVENTS_KEY)
    return json.loads(raw) if raw else []

events = load_events()

@app.post('/event')
def add_event():
    evt = request.json
    events.append(evt)
    cache_events(events)
    return { "msg": "Evento registrado" }, 201

@app.get('/events')
def list_events():
    return jsonify(events)

# ---------- RabbitMQ consumer (fila enviada pelo serviço PHP) -------------
def consume_rabbit():
    params = pika.URLParameters(os.getenv("RABBIT_URL"))
    conn   = pika.BlockingConnection(params)
    ch     = conn.channel()
    ch.queue_declare(queue=os.getenv("QUEUE"), durable=True)

    def callback(ch, method, properties, body):
        evt = { "source": "php", "msg": body.decode(), "type": "logistica" }
        events.append(evt)
        cache_events(events)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=os.getenv("QUEUE"), on_message_callback=callback)
    print(" [*] Aguardando mensagens RabbitMQ…")
    ch.start_consuming()

threading.Thread(target=consume_rabbit, daemon=True).start()

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT")), debug=True)
