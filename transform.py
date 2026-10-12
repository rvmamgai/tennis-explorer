def parse_competitions(payload):
    """Takes the raw dict from competitions.json.
    Returns two lists: (categories, competitions) - flat and ready for SQL."""

    categories = {}      # keyed by category_id, so duplicates collapse automatically
    competitions = []

    for item in payload["competitions"]:
        competition_id = item["id"]
        competition_name = item["name"]
        comp_type = item["type"]
        gender = item["gender"]
        parent_id = item.get("parent_id")
        level = item.get("level")

        category = item.get("category", {})
        category_id = category.get("id")
        category_name = category.get("name")

        if category_id:
            categories[category_id] = {
                "category_id": category_id,
                "category_name": category_name
            }

        competitions.append({
            "competition_id": competition_id,
            "competition_name": competition_name,
            "type": comp_type,
            "gender": gender,
            "parent_id": parent_id,
            "level": level,
            "category_id": category_id
        })

    return list(categories.values()), competitions


def parse_complexes(payload):
    """Takes the raw dict from complexes.json.
    Returns two lists: (complexes, venues) - flat and ready for SQL."""

    complexes = []
    venues = []

    for complex_item in payload["complexes"]:
        complex_id = complex_item["id"]
        complex_name = complex_item["name"]

        complexes.append({
            "complex_id": complex_id,
            "complex_name": complex_name
        })

        for venue in complex_item.get("venues", []):
            venues.append({
                "venue_id": venue["id"],
                "venue_name": venue["name"],
                "city_name": venue.get("city_name"),
                "country_name": venue.get("country_name"),
                "country_code": venue.get("country_code"),
                "timezone": venue.get("timezone"),
                "complex_id": complex_id   # links each venue back to its parent complex
            })

    return complexes, venues


def parse_doubles_rankings(payload):
    """Takes the raw dict from double_competitors_rankings.json.
    Returns two lists: (competitors, rankings) - flat and ready for SQL."""

    competitors = {}   # keyed by competitor_id, so a player appears only once
    rankings = []

    for tour in payload["rankings"]:
        ranking_name = tour["name"]        # "ATP" or "WTA"
        gender = tour["gender"]
        year = tour.get("year")
        week = tour.get("week")

        for entry in tour["competitor_rankings"]:
            competitor = entry.get("competitor", {})
            competitor_id = competitor.get("id")

            competitors[competitor_id] = {
                "competitor_id": competitor_id,
                "name": competitor.get("name"),
                "country": competitor.get("country"),
                "country_code": competitor.get("country_code"),
                "abbreviation": competitor.get("abbreviation")
            }

            rankings.append({
                "rank": entry.get("rank"),
                "movement": entry.get("movement"),
                "points": entry.get("points"),
                "competitions_played": entry.get("competitions_played"),
                "ranking_name": ranking_name,
                "gender": gender,
                "year": year,
                "week": week,
                "competitor_id": competitor_id
            })

    return list(competitors.values()), rankings


if __name__ == "__main__":
    import json

    # ---- Competitions ----
    with open("sample_response.json") as f:
        payload = json.load(f)

    categories, competitions = parse_competitions(payload)
    print("Categories found:", len(categories))
    print("Competitions found:", len(competitions))
    print(competitions[0])
    print(categories[0])

    missing_category = [c for c in competitions if c["category_id"] is None]
    print("Competitions with no category:", len(missing_category))

    # ---- Complexes and venues ----
    with open("sample_complexes.json") as f:
        complexes_payload = json.load(f)

    complexes, venues = parse_complexes(complexes_payload)
    print("Complexes found:", len(complexes))
    print("Venues found:", len(venues))
    print(complexes[0])
    print(venues[0])

    # ---- Doubles rankings ----
    with open("sample_rankings.json") as f:
        rankings_payload = json.load(f)

    competitors, rankings = parse_doubles_rankings(rankings_payload)
    print("Competitors found:", len(competitors))
    print("Rankings found:", len(rankings))
    print(competitors[0])
    print(rankings[0])