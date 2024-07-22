from courageous_comets import settings

MESSAGE_SCHEMA = {
    "index": {
        "name": "message_idx",
        "prefix": settings.REDIS_KEYS_PREFIX,
        "storage_type": "json",
    },
    "fields": [
        {"name": "content", "type": "text"},
        {"name": "user_id", "type": "tag"},
        {"name": "message_id", "type": "tag"},
        {"name": "channel_id", "type": "tag"},
        {"name": "guild_id", "type": "tag"},
        {"name": "timestamp", "type": "numeric", "attrs": {"sortable": True}},
        {
            "name": "embedding",
            "type": "vector",
            "attrs": {
                "dims": 384,
                "distance_metric": "cosine",
                "algorithm": "hnsw",
                "datatype": "float32",
            },
        },
        {"name": "neu", "type": "numeric", "path": "$.sentiment.neu"},
        {"name": "neg", "type": "numeric", "path": "$.sentiment.neg"},
        {"name": "pos", "type": "numeric", "path": "$.sentiment.pos"},
        {"name": "compound", "type": "numeric", "path": "$.sentiment.compound"},
    ],
}
