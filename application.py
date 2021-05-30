import flask
import json
import yaml
from flask import request, Response, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequestKeyError
from googlemap_api import Gmap_API
from aws import DynamoDB, IOT_CORE

# Create and configure the Flask app
application = flask.Flask(__name__)
application.config.from_object('default_config')
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']
application.config['JSON_SORT_KEYS'] = False
CORS(application)

# load config
stream = open('./config/secrets.yaml', 'r')
config = yaml.load(stream)['production']


@application.route('/')
def index():
    return {"status":"ok","message":"DrinkKing API v1 at /api/v1/ in production mode"}, 200


# POST /api/v1/shops/可不可?latitude=24.7961217&longitude=120.996669
@application.route('/api/v1/shops/<keyword>', methods=['POST', 'GET'])
def store_shop(keyword):
    try:
        location = request.args

        api = Gmap_API()
        dynamodb = DynamoDB()

        response = api.nearbysearch(keyword, location)

        if response['status'] == 'OK':
            places = response['results']

            save_places = []
            for place in places:
                place_details = api.placedetails(place['place_id'])['result']
                processed_place = process_place_data(place, place_details)
                save_places.append(processed_place)

            # save to dynamoDB
            dynamodb.insert_data('shops', save_places)

            return jsonify(save_places)
        elif response['status'] == 'ZERO_RESULTS':
            return response, 404
        else:
            return response, 400
    except BadRequestKeyError:
        return "Bad request", 400
    except Exception as e:
        return e, 500  # for debug
        # return "Internal Error", 500


# GET /api/v1/shops?keyword=可不可
@application.route('/api/v1/shops', methods=['GET'])
def list_shop():
    # try:
        keyword = request.args.get("keyword")
        dynamodb = DynamoDB()
        iot_client = IOT_CORE()

        shops = dynamodb.fetch_data('shops', keyword)

        for shop in shops:
            with open("./assets/shops_menu.json", encoding="utf-8") as f:
                data = json.load(f)
                menu_info = findByShopName(shop['shopname'], data)
                if menu_info:
                    shop['fb_url'] = menu_info[0]['fb_url']
                    shop['menu'] = menu_info[0]['drinks']

                #  publish to MQTT topic
                place_id_data = {"place_id": shop['place_id']}
                response = iot_client.publish_to_topic("drinkshop_pie", place_id_data)
                # print(response)

        return jsonify(shops), 200
    # except Exception as e:
    #     return e, 500  # for debug
        # return "Internal Error", 500


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

        if result is None:
            return "Not found", 404
        return jsonify(result), 200
    except Exception as e:
        return "Internal Error", 500


def findByShopName(shopname, data):
    for shop in data:
        if shopname in shop["shopname"] or shop["shopname"] in shopname:
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
        "location": {key: str(value) for key, value in place['geometry']['location'].items()},
        "opening_now": place_details['opening_hours']['open_now'],
        "opening_hours": place_details['opening_hours']['weekday_text'],
        "address": place_details['formatted_address'],
        "phone_number": place_details['formatted_phone_number'],
        "rating": str(place['rating']),
        "reviews": place_details['reviews']
    }

    for review in save_place['reviews']:
        review['rating'] = str(review['rating'])  # dynamoDB scan return "Decimal problem"
        unwanted = set(review.keys()) - set({'author_name', 'rating', 'relative_time_description', 'text'})
        for key in unwanted:
            del review[key]

    return save_place


if __name__ == '__main__':
    application.run(host='0.0.0.0')
