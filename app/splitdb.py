import json

with open('db.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

users = []
app_data = []
locations = []

# Modele przestrzeni użytkownika, które pomijamy w app_data
user_related_models = [
    "api.resources",
    "api.userlocation",
    "api.userquest",
    "api.userquestrequirement",
    "api.useritems",
    "api.userpotions",
    "api.usercollectableitem",
    "api.character",
    "api.userlvl",
    "api.characteritem",
    "api.userrquest",
    "api.userquestrequirement",
    "api.transaction",
    "authtoken.token"
]

location_models = [
    "api.region",
    "api.location",
]

# Modele adminowe, których nie potrzebujemy
admin_related_models = [
    "admin.logentry",
    "auth.permission",
    "contenttypes.contenttype",
    "sessions.session",
]

for obj in data:
    if obj["model"] == "api.customuser":
        users.append(obj)
    elif obj["model"] in location_models:
        locations.append(obj)
    elif obj["model"] not in user_related_models and obj["model"] not in admin_related_models:
        app_data.append(obj)

# Zapisz użytkowników
with open('users.json', 'w', encoding='utf-8') as f:
    json.dump(users, f, indent=4, ensure_ascii=False)

# Zapisz dane aplikacji
with open('app_data.json', 'w', encoding='utf-8') as f:
    json.dump(app_data, f, indent=4, ensure_ascii=False)

with open('locations.json', 'w', encoding='utf-8') as f:
    json.dump(locations, f, indent=4, ensure_ascii=False)

print("✅ Podzielono dane na users.json i app_data.json!")
