from pydantic import BaseModel,field_validator
import re
import json
from datetime import datetime,time,timedelta

class Location(BaseModel):
    address:str
    country:str
    latitude:float
    longitude:float

class TimeRange(BaseModel):
    start_day:time
    end_day:time

    @field_validator('start_day', 'end_day', mode='before')
    def validate_time(cls, v):
        try:
            v = int(v)
            hours = v // 60
            minutes = v % 60
            return time(hours, minutes)
        except Exception:
            raise ValueError("Invalid time format")
        
class Availability(BaseModel):
    day_range: str
    time_range: list[TimeRange]   

class Items(BaseModel):
    item_name:str
    item_img:str | None
    price:float
    description:str

class Menu(BaseModel):
    category:str
    items:list[Items]

class UberEats(BaseModel):
    restaurant_name: str
    phone_number:str
    product_category:list
    img:str
    location:Location
    currency:str
    delivery_time:str
    rating:float | None
    availability:list[Availability]
    deliverable_distance:str
    menu:list[Menu]

with open('uber_eats.json','r',encoding='utf-8') as f:
    data=json.load(f)

data=data['data']
restaurant_name=data['title']
phone_number=data['phoneNumber']
product_category=data['categories']
img_path=data['heroImageUrls']

try:
    img=img_path.pop()['url']
except IndexError:
    img=None

location_path=data['location']
address=location_path['address']
country=location_path['country']
latitude=location_path['latitude']  
longitude=location_path['longitude']
location=Location(address=address,country=country,latitude=latitude,longitude=longitude)

currency=data['currencyCode']
delivery_time=data['etaRange']['text']
rating=data['rating']

values=data['hours']

aval=list()


for value in values:
    day_range=value['dayRange']
    
    selection_hours=list()
    for t in value['sectionHours']:
        start_time = t['startTime']
        end_time = t['endTime']
        timeRange=TimeRange(start_day=start_time,end_day=end_time)
        selection_hours.append(timeRange)
        
    availability=Availability(day_range=day_range,time_range=selection_hours)
    aval.append(availability)
        
deliverable_distance=data['distanceBadge']['accessibilityText']



items=data['catalogSectionsMap']
menu_items=list()
for key in items.keys():
    category_list=items[key]
    
    for item in category_list:
        path_0=item['payload']['standardItemsPayload']
        category=path_0['title']['text']
        items_list=path_0['catalogItems']
        items=list()
        items = []

        for item in items_list:
            obj = Items(
                item_name=item.get('title', 'Unknown'),
                item_img=item.get('imageUrl', None),
                price=item.get('price', 0),
                description=item.get('itemDescription', '')
            )
            items.append(obj)
        menu = Menu(category=category, items=items)
        menu_items.append(menu)
      
uber_eats=UberEats(restaurant_name=restaurant_name,phone_number=phone_number,product_category=product_category,img=img,location=location,currency=currency,delivery_time=delivery_time,rating=rating,availability=aval,deliverable_distance=deliverable_distance,menu=menu_items)

with open('uber_output.json','w',encoding='utf-8') as f:
    json.dump(uber_eats.model_dump(),f,ensure_ascii=False,indent=4,default=str)
