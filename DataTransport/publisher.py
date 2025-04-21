from google.cloud import pubsub_v1
import json

# TODO(developer)
project_id = "cs510-data-engineering-labs"
topic_id = "my-topic"

publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

with open("./bcsample.json", "r") as f:
    file = json.load(f)

count: int = 0

for n in file:
    data_str = (
        "Trip NO: " + str(file[0]['EVENT_NO_TRIP'])
    )
    # Data must be a bytestring
    data = data_str.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data)
    count += 1
    #print(future.result())

print(f"Published {count} messages to {topic_path}.")