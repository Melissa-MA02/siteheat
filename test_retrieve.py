"""Check what the Knowledge Base returns before wiring it into the agent."""
import boto3

KB_ID = "FLE31I76SM"
client = boto3.client("bedrock-agent-runtime", region_name="ap-southeast-2")

QUERIES = [
    "is there a maximum temperature where workers must stop work",
    "what are the symptoms of heat stroke",
    "how can I reduce heat risk for outdoor workers",
]

for q in QUERIES:
    print(f"\n=== {q} ===")
    r = client.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": q},
        retrievalConfiguration={"managedSearchConfiguration": {"numberOfResults": 3}}
    )
    for i, hit in enumerate(r["retrievalResults"], 1):
        src = hit["location"]["s3Location"]["uri"].split("/")[-1]  # filename only
        text = hit["content"]["text"].replace("\n", " ")[:600]
        print(f"{i}. [{hit['score']:.3f}] {src}\n   {text}...")