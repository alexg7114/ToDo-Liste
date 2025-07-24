ToDo REST-API

Ein einfaches FastAPI-Backend zur Verwaltung von ToDo Einträgen mit BenutzerßAuthentifizierung (JWT).

Setup-Anleitung:

1. Repository klonen:
   git clone https://github.com/alexg7114/ToDo-Liste.git
   cd to_do_liste

2. Virtuelle Umgebung erstellen und aktivieren:
   python -m venv venv
   source venv/Scripts/activate   (Windows)
   oder
   source venv/bin/activate       (Linux/Mac)

3. Abhängigkeiten installieren:
   pip install -r requirements.txt

4. Server starten:
   uvicorn main:app --reload

5. Im Browser öffnen:
   http://localhost:8000/docs


Testbenutzer erstellen:

- Gehe zu POST / register
- Beispiel:
  {
    "username": "alex",
    "password": "test"
  }

Danach kann man sich mit POST / login anmelden und bekommt ein Token.

Authorisierung:

- Auf "Authorize" klicken.
- Login und Password eingeben.
- Token wird automatisch gespeichert und für Anfragen benutzt.

Verfügbare Endpunkte:

- POST / register
- POST / login
- GET /me
- POST / todos
- GET / todos
- PUT / todos/{id}
- DELETE /todos/{id}

Die API-Dokumentation ist automatisch unter /docs erreichbar.
