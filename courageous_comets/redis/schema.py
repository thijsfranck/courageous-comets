from courageous_comets import settings

MESSAGE_SCHEMA = {
    "index": {
        "name": "message_idx",
        "prefix": f"{settings.REDIS_KEYS_PREFIX}:messages",
    },
    "fields": [
        {"name": "user_id", "type": "tag"},
        {"name": "message_id", "type": "tag"},
        {"name": "channel_id", "type": "tag"},
        {"name": "guild_id", "type": "tag"},
        {"name": "timestamp", "type": "numeric", "attrs": {"sortable": True}},
        {"name": "sentiment_neg", "type": "numeric", "attrs": {"sortable": True}},
        {"name": "sentiment_neu", "type": "numeric", "attrs": {"sortable": True}},
        {"name": "sentiment_pos", "type": "numeric", "attrs": {"sortable": True}},
        {"name": "sentiment_compound", "type": "numeric", "attrs": {"sortable": True}},
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
    ],
}
