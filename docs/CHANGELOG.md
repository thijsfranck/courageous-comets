## v0.3.0 (2024-07-22)

### Feat

- store sentiment analysis with message data (#39)
- set up message content preprocessing (#40)
- replace sentence_transformers with transformers library (#36)
- add messages cog (#32)
- return messages based on similarity score (#30)

### Fix

- fix sync command signature and internal logic (#38)
- save messages with message_id on redis (#33)
- ensure consistent log output (#29)
- suppress warnings from libraries

### Refactor

- remove hfvectorizer (#35)
- include save_message in Messages cog (#34)
- remove throws clause from docstring

## v0.2.0 (2024-07-21)

### Feat

- setup transformer models (#28)
- use pydantic to model Redis hashes (#25)
- add sentiment analysis (#24)
- add api to store word frequency on redis (#23)
- download nltk resources on startup (#22)

### Fix

- handle contractions in tokenizer (#26)
- control max number of concurrent downloads
- add logging and remove return section from docstring

### Refactor

- move startup logic into bot class (#27)
- improve docs, types and fix some linter issues
- update docstrings
- improve type hints

## v0.1.0 (2024-07-20)

### Feat

- add bot boilerplate

### Fix

- improved error handling and settings validation
- include application config in docker image (#15)
- set redis host from environment variables

### Refactor

- improve error handling and logging

## v0.0.6 (2024-07-19)

## v0.0.5 (2024-07-17)

## v0.0.4 (2024-07-16)

## v0.0.3 (2024-07-16)

## v0.0.2 (2024-07-16)

## v0.0.1 (2024-07-15)
