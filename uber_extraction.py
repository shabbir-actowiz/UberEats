from pydantic import BaseModel,field_validator
import re
import json
from datetime import datetime,time,timedelta

class Location(BaseModel):
    address:str
    country:str
    latitude:float
    longitude:float

    @field_validator("latitude")
    def validate_latitude(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

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

    @field_validator("price")
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

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

    @field_validator("currency")
    def validate_currency(cls, v):
        if not re.match(r"^[A-Z]{3}$", v):
            raise ValueError("Invalid currency code")
        return v
    
    @field_validator("phone_number")
    def validate_phone(cls, v):
        if not re.match(r'^\+?\d{7,15}$', v):
            raise ValueError("Invalid phone number")
        return v

with open('uber_eats.json','r',encoding='utf-8') as f:
    data=json.load(f)

try:
    data=data['data']
    restaurant_name=data['title']
    phone_number=data['phoneNumber']
    product_category=data['categories']
    img_path=data['heroImageUrls']
except Exception as e:
    print("Basic data error:", e)

try:
    img=img_path.pop()['url']
except Exception:
    img=None

try:
    location_path=data['location']
    address=location_path['address']
    country=location_path['country']
    latitude=location_path['latitude']  
    longitude=location_path['longitude']
    location=Location(address=address,country=country,latitude=latitude,longitude=longitude)
except Exception as e:
    print("Location error:", e)
    location=None

try:
    currency=data['currencyCode']
    delivery_time=data['etaRange']['text']
    rating=data['rating']
except Exception as e:
    print("Meta error:", e)

aval=list()

try:
    values=data['hours']

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

except Exception as e:
    print("Availability error:", e)

try:
    deliverable_distance=data['distanceBadge']['accessibilityText']
except Exception:
    deliverable_distance=None

menu_items=list()

try:
    items=data['catalogSectionsMap']

    for key in items.keys():
        category_list=items[key]
        
        for item in category_list:
            path_0=item['payload']['standardItemsPayload']
            category=path_0['title']['text']
            items_list=path_0['catalogItems']
            items=list()
            items = []

            for item in items_list:
                decimal=int(item.get('spanCount', 0))
                price=item.get('price', 0)/(10**decimal)
                obj = Items(
                    item_name=item.get('title', 'Unknown'),
                    item_img=item.get('imageUrl', None),
                    price=price,
                    description=item.get('itemDescription', '')
                )
                items.append(obj)
                
            menu = Menu(category=category, items=items)
            menu_items.append(menu)

except Exception as e:
    print("Menu error:", e)

try:
    uber_eats=UberEats(
        restaurant_name=restaurant_name,
        phone_number=phone_number,
        product_category=product_category,
        img=img,
        location=location,
        currency=currency,
        delivery_time=delivery_time,
        rating=rating,
        availability=aval,
        deliverable_distance=deliverable_distance,
        menu=menu_items
    )
except Exception as e:
    print("Final object error:", e)

with open('uber_output.json','w',encoding='utf-8') as f:
    json.dump(uber_eats.model_dump(),f,ensure_ascii=False,indent=4,default=str)
