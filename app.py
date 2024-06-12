import http.server
import socketserver
import json

PORT = 8000

class PubSubSystem:
    def __init__(self):
        self.topics = {}

    def subscribe(self, topic_id, subscriber_id):
        if topic_id not in self.topics:
            self.topics[topic_id] = set()
        self.topics[topic_id].add(subscriber_id)
        return f'Subscriber {subscriber_id} subscribed to topic {topic_id}'

    def notify(self, topic_id):
        if topic_id in self.topics:
            subscribers = self.topics[topic_id]
            notifications = [f'Notifying subscriber {subscriber} about topic {topic_id}' for subscriber in subscribers]
            return notifications
        else:
            return f'Topic {topic_id} does not exist'

    def unsubscribe(self, topic_id, subscriber_id):
        if topic_id in self.topics and subscriber_id in self.topics[topic_id]:
            self.topics[topic_id].remove(subscriber_id)
            if not self.topics[topic_id]:
                del self.topics[topic_id]
            return f'Subscriber {subscriber_id} unsubscribed from topic {topic_id}'
        else:
            return f'Subscriber {subscriber_id} is not subscribed to topic {topic_id}'

pubsub_system = PubSubSystem()

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        if self.path == '/subscribe':
            topic_id = data['topicId']
            subscriber_id = data['subscriberId']
            response = pubsub_system.subscribe(topic_id, subscriber_id)
        elif self.path == '/unsubscribe':
            topic_id = data['topicId']
            subscriber_id = data['subscriberId']
            response = pubsub_system.unsubscribe(topic_id, subscriber_id)
        else:
            response = 'Invalid endpoint'

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"message": response}).encode('utf-8'))

    def do_GET(self):
        path_components = self.path.split('/')
        if len(path_components) >= 3 and path_components[1] == 'notify':
            topic_id = path_components[2]
            response = pubsub_system.notify(topic_id)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"notifications": response}).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Invalid endpoint"}).encode('utf-8'))

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
