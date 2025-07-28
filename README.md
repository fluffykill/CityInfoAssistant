# City Information Assistant
A city information assistant agent built using fastapi and an llm through OpenRouter. As well as calling the following apis for city data.

| API | Purpose |
| ------------- | ------------- |
| [OpenWeatherMap API](https://openweathermap.org/current)  | Get current weather for a city  |
| [World Time API](https://worldtimeapi.org/)  | Get current time in a city  |
| [GeoDB Cities API](https://rapidapi.com/wirefreethought/api/geodb-cities)  | Get basic facts about a city  |

**Currently reasoning does not work as free models do not support the feature**

## Installation
Make sure you have python 3, pip, and pipenv installed. Then run the following command to download required packages.
```zsh
pipenv install
```
In the root directory create an env file from the sample and enter the appropriate api keys for each service.

## Run
First start the pipenv shell by running in the root of the project
```zsh
pipenv shell
```
Then to start in developer mode 
```zsh
fastapi dev main.py 
```
For production use
```zsh
fastapi run
```

## API
### POST /send_message 
Sends a message to agent with the following request body
```json
{
    "id": "uuid",
    "new_message":"string",
    "messages": "list of message objects"
}
```
The id field of the request is for us to better track different requests that come as well as any potential errors that appear.

Because this service does not use any database to store data, the message field is used as a way to track conversation context for the llm.

Example Response Body
```json
{
    "thinking": "LLM Reasoning",
    "function_calls": [{ "tool": "find_city", "parameters": { "name": "Paris" } }],
    "response": "LLM Response",
    "messages": [
        {
            "role": "system",
            "content": "You are a city information assistant that helps users gather factual information about cities, such as weather, current local time, and basic facts"
        },
        {
            "role": "user",
            "content": "I am planning a trip to Paris, France and I would like to know more about the city like it's current weather, local time, and some facts"
        }
    ]
}
```

## Production Readiness
Due to time limited nature of this project, I do not believe this project is production ready. At most this would be a proof of concept that would be either iterated upon or used as an example to build the actual production agent.

## Future Plans
For an initial alpha production version of the product provided there is already a working cloud environment
1. Add logging to better track current status and errors
2. Find a proper reasoning llm and update code to suport it
3. Evaluate llm usage and response quality. Add caps to llm calls or swap to a different llm if needed
4. Decide on a db service to use for chat history and potential user and other kinds of data as well as implementing the actual code to handle db
5. Update to save chat history in the chosen db so users do not have to provide entire chat history in request
6. Add auth for different users
7. Add security checks to prevent cross origin resource sharing
8. Decide on wether to use containerization or not, if yes then implement containerization
9. Add proper openapi documentation 
10. Update readme for production version
11. Create test suite

Future features.
1. Add feature for agent to provide ideas on places to visit for the particular city i.e local attractions or points of interest
2. Add feature for agent to be able to create a schedule/plan for the user
3. Add feature for agent to export plans or integrate it with another service i.e google calendar