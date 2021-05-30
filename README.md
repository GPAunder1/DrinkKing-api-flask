# DrinkKing Web API - Flask
Web API for cloudprog course, using flask and AWS services

API has several features:
1. Store shops by calling googlemap API
2. List drink shops
3. Get shop menu

## Routes
### Route check
`GET /`

Status:
- 200: API server running (happy)

### List shops
`GET /shops?keyword={keyword}`

Status:
- 200: shoplist returned
- 404: no shop is found from database
- 500: internal error

### Store shops
`POST /shops/{keyword}`

Status:
- 201: shops stored
- 400: invalid keyword
- 404: no shop is found in menu or googlemap API
- 500: internal error

### Get shop menu
`GET /menus?keyword={keyword}&searchby={shop/drink}`

Status:
- 200: shop menu returned
- 404: shop menu not found
