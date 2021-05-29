import flask
import json
import yaml
from googlemap_api import Gmap_API
from flask import request, Response, jsonify

# Create and configure the Flask app
application = flask.Flask(__name__)
application.config.from_object('default_config')
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']

# load config
stream = open('./config/secrets.yaml', 'r')
config = yaml.load(stream)['production']


@application.route('/')
def index():
    return {"status":"ok","message":"DrinkKing API v1 at /api/v1/ in production mode"}, 200


@application.route('/test')
def test():
    print(config)
    return ""


# POST /api/v1/shops/可不可?latitude=24.7961217&longitude=120.996669
@application.route('/api/v1/shops/<keyword>', methods=['POST', 'GET'])
def store_shop(keyword):
    try:
        location = request.args

        api = Gmap_API()
        response = api.nearbysearch(keyword, location)
        if response['status'] == 'OK':
            places = response['results']

            save_places = []
            for place in places:
                place_details = api.placedetails(place['place_id'])['result']
                processed_place = process_place_data(place, place_details)
                save_places.append(processed_place)

            return jsonify(save_places)
        elif response['status'] == 'ZERO_RESULTS':
            return response, 404
        else:
            return response, 400
    # except BadRequestKeyError:
    #     return "Bad request", 400
    except Exception as e:
        # print(type(e).__name_)
        # print(e)
        return "Internal Error", 500

# GET /menus?keyword={keyword}&searchby={shop/drink}
@application.route("/api/v1/menus")
def getShopMenu():
    try:
        keyword = request.args.get("keyword")
        searchby = request.args.get("searchby")
        result = ""
        with open("./assets/shops_menu.json", encoding="utf-8") as f:
            data = json.load(f)
            if searchby == "shop":
                result = findByShopName(keyword, data)
            elif searchby == "drink":
                result = findByDrink(keyword, data)
            elif searchby == "both":
                shop_result = findByShopName(keyword,data)
                drink_result = findByDrink(keyword,data)
                result = shop_result + drink_result
            f.close()

        if result == None:
            return "Not found", 404
        return jsonify(result), 200
    except Exception as e:
        print(e)
        return "Internal Error", 500


def findByShopName(shopname, data):
    for shop in data:
        if shopname in shop["shopname"]:
            return [shop]
    return []


def findByDrink(drinkname, data):
    shops = []
    for shop in data:
        for item in shop["drinks"]:
            if drinkname in item["name"]:
                shops.append(shop)
                break
    return shops

def process_place_data(place, place_details):
    save_place = {
        "shopname": place['name'],
        "place_id": place['place_id'],
        "url": place_details['url'],
        "location": place['geometry']['location'],
        "opening_now": place_details['opening_hours']['open_now'],
        "opening_hours": place_details['opening_hours']['weekday_text'],
        # "reviews": [item for item in place_details['reviews'] for key in item.keys() if key == "rating"]
        "address": place_details['formatted_address'],
        "phone_number": place_details['formatted_phone_number'],
        "rating": place['rating'],
        "reviews": place_details['reviews']
    }

    for review in save_place['reviews']:
        unwanted = set(review.keys()) - set({'author_name', 'rating', 'relative_time_description', 'text'})
        for key in unwanted:
            del review[key]


    return save_place


if __name__ == '__main__':
    application.run(host='0.0.0.0')
