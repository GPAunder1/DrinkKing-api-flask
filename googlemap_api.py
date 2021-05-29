import yaml
import json
import requests

# load config
stream = open('./config/secrets.yaml', 'r')
config = yaml.safe_load(stream)['production']


class Gmap_API:

    def __init__(self):
        self.API_ROOT = 'https://maps.googleapis.com/maps/api/place'
        self.TOKEN = config['GMAP_API_TOKEN']

    def nearbysearch(self, keyword, location):
        latitude = location['latitude']
        longitude = location['longitude']
        parameter = 'location={0},{1}&radius=1000&keyword={2}&language=zh-TW'.format(latitude, longitude, keyword)
        # parameter = "location=#{location[0]},#{location[1]}&radius=2000&keyword=#{keyword}&language=zh-TW"
        url = "{0}/nearbysearch/json?key={1}&{2}".format(self.API_ROOT, self.TOKEN, parameter)

        return json.loads(self.call_api_url(url))

    def placedetails(self, placeid):
        parameter = 'place_id={0}&language=zh-TW&fields=formatted_address,formatted_phone_number,opening_hours,reviews,url'.format(placeid)
        url = "{0}/details/json?key={1}&{2}".format(self.API_ROOT, self.TOKEN, parameter)

        # return self.call_api_url(url)
        return json.loads(self.call_api_url(url))

    """ private methods """
    def call_api_url(self, url):
        response = requests.get(url)
        return response.text
