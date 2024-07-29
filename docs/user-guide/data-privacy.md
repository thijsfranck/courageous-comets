# Data Privacy

From the moment the bot is added to the server, it scans all messages sent by users to gather the data necessary
for responding to interactions.

While raw messages are not stored, the bot processes messages to identify keywords. The identified keywords, along
with their count and byte representation, are stored in the database. Additionally, the Discord IDs for the message,
user, channel, and server are recorded.

For displaying messages as part of search results, the bot interacts with the Discord API to fetch the message
content. The user who requested the search results can view the message content, even if they were not part of
the original conversation. Messages are cached in the bot's memory for a limited time to improve performance.

Apart from interactions with the Discord API, no data is shared with third parties, and all data is securely stored
on the bot's server.
