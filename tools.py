import os
import requests

OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "get_city_local_time",
            "description": "Gets the current local time for provided area and location",
            "parameters": {
                "type": "object",
                "properties": {
                    "area": {"type": "string","description": "The area usually a continent e.g. America or Europe"},
                    "location": {"type": "string", "description": "The location usually a city e.g. Toronto"},
                },
                "required": ["area", "location"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_city_weather",
            "description": "Get current temperature in celsius for provided coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_city",
            "description": "Finds the city wikiDataId for cities with a minimum population of 1000000 given the prefix of it's name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_city_details",
            "description": "Get basic city facts (e.g., country, population, description) from a wikiDataId",
            "parameters": {
                "type": "object",
                "properties": {
                    "wikiDataId": {"type": "string", "details": "The wikiDataId returned from the find_city tool"},
                },
                "required": ["wikiDataId"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

def get_current_city_weather(latitude, longitude):
  url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OPEN_WEATHER_API_KEY}"
  response = requests.get(url)
  data = response.json()
  return data

def get_city_local_time(area, location):
  url = f"http://worldtimeapi.org/api/timezone/{area}/{location}"
  response = requests.get(url)
  data = response.json()
  return data

def get_city_nearby_attractions(wikiDataId):
  near_by_cities_url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities/{wikiDataId}/nearbyCities?radius=10&minPopulation=500000"
  headers = {"user-x-rapidapi-host": "wft-geo-db.p.rapidapi.com", 'x-rapidapi-key': RAPID_API_KEY}
  near_by_cities_response = requests.get(near_by_cities_url, headers=headers)
  near_by_cities_data = near_by_cities_response.json()
  attraction_query = [f"{{?attraction wdt:P131 wd:{wikiDataId}}}"]
  for city in near_by_cities_data.get("data",[]):
    found_data_id = city.get("wikiDataId", None)
    if found_data_id:
      attraction_query.append(f"{{?attraction wdt:P131 wd:{found_data_id}}}")

  SPARQL_query = f"""
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  PREFIX wd: <http://www.wikidata.org/entity/>
  PREFIX wdt: <http://www.wikidata.org/prop/direct/>

  SELECT DISTINCT ?attraction ?attractionLabel ?gps 

  WHERE {{
      ?attraction (wdt:P31/wdt:P279*) wd:Q570116;
          wdt:P625 ?gps;
          rdfs:label ?attractionLabel.
      
      {"UNION".join(attraction_query)}

      FILTER(LANG(?attractionLabel) = "en")
  }}
  """

  wikiData_url = f"https://query.wikidata.org/sparql?format=json&query={requests.utils.quote(SPARQL_query, safe='')}"
  near_by_attractions_response = requests.get(wikiData_url)
  data = near_by_attractions_response.json()
  return data

def find_city(name):
  find_city_url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities?namePrefix={name}&minPopulation=1000000" 
  headers = {"user-x-rapidapi-host": "wft-geo-db.p.rapidapi.com", 'x-rapidapi-key': RAPID_API_KEY}
  response = requests.get(find_city_url, headers=headers)
  data = response.json()
  return data["data"]

def find_city_details(wikiDataId):
  find_city_url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities/{wikiDataId}" 
  headers = {"user-x-rapidapi-host": "wft-geo-db.p.rapidapi.com", 'x-rapidapi-key': RAPID_API_KEY}
  response = requests.get(find_city_url, headers=headers)
  data = response.json()
  print(data)
  return data

TOOL_MAPPING = {
  "get_current_city_weather": get_current_city_weather, 
  "find_city": find_city,
  "get_city_local_time": get_city_local_time,
  "find_city_details": find_city_details
}