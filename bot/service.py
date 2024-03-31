import logging, requests, logging, time, json, datetime, re

def patch_pokemon_data(iv):
    """Obtains Pokemon data from multiple sources and returns a combined list of Pokemon with 100% IV."""
    total_data = []

    urls = [
        "https://vanpokemap.com/query2.php",
        "https://nycpokemap.com/query2.php",
        "https://londonpogomap.com/query2.php",
        "https://sgpokemap.com/query2.php",
        "https://sydneypogomap.com/query2.php",
    ]

    headers = {
        "https://vanpokemap.com/query2.php": {"Referer": "https://vanpokemap.com/"},
        "https://nycpokemap.com/query2.php": {"Referer": "https://nycpokemap.com/"},
        "https://londonpogomap.com/query2.php": {
            "Referer": "https://londonpogomap.com/"
        },
        "https://sgpokemap.com/query2.php": {"Referer": "https://sgpokemap.com/"},
        "https://sydneypogomap.com/query2.php": {
            "Referer": "https://sydneypogomap.com/"
        },
    }
    
    params = {
        "mons" : ",".join(str(i) for i in range(999)),
        "minIV" : str(iv),
        "time" : int(time.time()),
        "since" : 0,
    }
    
    for url in urls:
        headers_for_url = headers.get(url, {})
        try:
            response = requests.get(url, params=params, headers=headers_for_url )
            response.raise_for_status() # * If an error occurs, it will throw an exception.
            data = response.json()
            for pokemon in data.get("pokemons", []):
                total_data.append(pokemon)
        except requests.exceptions.RequestException as e:
            logging.warning(f"Failed to fetch data from {url} : {e}")
            return None
        except json.decoder.JSONDecodeError as e :
            logging.error(f"Failed to decode JSON response from {url} : {e}")
            return None
    total_data.sort(key=lambda x : x["despawn"], reverse=True)
    return total_data