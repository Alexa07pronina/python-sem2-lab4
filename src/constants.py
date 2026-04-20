from typing import Any

"""Примеры payload для генерации"""
payloads_example:list[dict[str, Any]]=[
    {"role":"admin","password": 123},
    {"role":"user"},
    {"animal":"cat", "sound": "meow"},
    {"animal":"dog", "sound": "woof"},
    {"animal":"goose", "sound": "honk", "power": 10},
    {"dish": "pizza", "toppings": ["cheese", "pepperoni"], "size": "large"},
    {"recipe": "pancakes", "ingredients": ["flour", "milk", "eggs"], "time": 15},
    {"order": "coffee", "type": "latte", "size": "medium"},
    {"product": "apple", "quantity": 3, "unit": "pieces"},
    {"restaurant": "Burger King", "rating": 4, "review": "good fries"},
    {"city": "London", "temp": 12, "condition": "rainy"},
    {"forecast": "sunny", "wind": 5.2, "humidity": 65},
    {"sunrise": "06:30", "sunset": "19:45"},
    {"season": "spring", "activity": "hiking"},
    {"name": "John", "age": 25, "city": "New York"},
    {"birthday": "2025-05-20", "gift": "book", "recipient": "Anna"},
    {"hobby": "photography", "camera": "Canon"},
    {"event": "party", "theme": "80s", "guests": 15},
    {"device": "smartphone", "brand": "iPhone", "model": "15 Pro"},
    {"device": "smartphone", "brand": "Samsung", "model": "Galaxy S25"}
]
