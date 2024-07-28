## v1.0.0 (2024-07-28)

### BREAKING CHANGE

- dependencies are no longer updated

### Feat

- lock dependencies for final version

## v0.10.0 (2024-07-28)

### Feat

- frequency time divisions (#62)
- add topics command that lists the most used keywords (#61)
- add user keyword frequency (#60)

### Fix

- capitalize embed title
- ensure consistent styling on embed titles
- improve logging for all interactions

### Refactor

- log message processed as debug event
- log database event as error
- simplify messages cog
- remove redundant error class
- remove redundant decorator
- split up keywords and sentiment cogs, improve cog documentation

## v0.9.0 (2024-07-28)

### Feat

- add praise interaction for user and message sentiment
- harmonize sentiment embeds
- add details to frequency embed
- refactor cogs with ui components and complete existing interactions

### Fix

- increase search results max preview length
- show channel in search results
- avoid error when no sentiment data is available for a user

### Refactor

- remove redundant code
- remove unused component
- move message processing to a separate module

## v0.8.0 (2024-07-27)

### Feat

- plot message frequency graph

### Fix

- reference current version in documentation
- update app description and set embed footer
- handle missing sentiment data
- restore user sentiment interaction
- add exists check
- silence KeyboardInterrupt on application shutdown (#59)
- remove  cog from erroneous merge conflict resolution (#58)
- remove unused context menu loader

## v0.7.0 (2024-07-26)

### Feat

- add user sentiment interaction (#54)
- set up frequency cog (#53)
- add sentiment chart (#52)
- add cog that returns information about the app (#50)
- add drop_code_blocks processor
- get message rate by duration (#49)
- calculate count of tokens across messages (#48)
- allow redis search filtering across multiple ids (#47)
- add development mode (#46)

### Fix

- remove reference to link from general bot description and add it to the about message
- handle PackageNotFoundError
- add __version__ and log version on startup

## v0.6.0 (2024-07-24)

### Feat

- store message tokens (#45)
- limit queries to most recent messsages (#43)
- store sentiment results along with message (#42)

### Refactor

- simplify function signatures and make it easier to build scope filters (#44)

## v0.5.0 (2024-07-23)

### Feat

- add docker compose and fix production dockerfile

## v0.4.0 (2024-07-23)

### Feat

- revert back to hash data type for storing messages (#41)

### Fix

- open app config in read mode
- trucate uses correct length
- preprocessing drops extra whitespace

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
