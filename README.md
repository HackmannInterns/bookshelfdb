# Bookshelfdb
Hackmann library scan and DB

## Using Docker Compose
The image is hosted on [DockerHub]("https://hub.docker.com/r/alexreynen/bookshelfdb").

Create a ```docker-compose.yml``` file with the following contents. An example can be see in [docker-compose.yml](/docker-compose.yml) or below:
```
services:
  flask-app:
    image: "alexreynen/bookshelfdb:latest"
    container_name: bookshelfdb
    volumes:
      - ./data:/app/data
    environment:
      - BOOKSHELFDB_PASSWORD=changeme  # Change this to a secure password
      - BOOKSHELFDB_PASSWORD_EDITOR=changeme2  # Change this to a secure password
      - BOOKSHELFDB_SECRET_KEY=changeme  # Change this to a secure key
    ports:
      - "5000:5000"
    restart: unless-stopped

```

Then while in the same folder as the ``docker-compose.yml`` run:

```
docker compose up
```

To run the container in background add `-d` to the above command. The app can be accessed at http://localhost:5000 by default.

The environmental variables:

``BOOKSHELFDB_PASSWORD`` is for admin password for site 

``BOOKSHELFDB_PASSWORD_EDITOR`` is for editor permissions

``BOOKSHELFDB_SECRET_KEY`` is being used for security, change this to something secure.

View [here](#permissions) for more information regarding the permissions


Additionally, the persistent storage for the app is held in /data, and can be stored outside of the container, as demonstrated in the compose file. The main library database, the cache database, and the admin configuration file are stored here. All will be created upon use.



# Permissions

There are three tiers of users in terms of accessing the database: a general (not logged in) user (referred to a viewer), an editor, and an admin. The admin can change how the other two user types are allowed to interact with the database as well as having full access, these permissions are visible and editable in ``/data/admin.yml``.
```
    'viewer_can_add': False,
    'editor_can_remove': True,
    'default_address': "",
    'header_name': "My Library"
```

General user can view the database via the web UI and if viewer_can_add is enabled, add new content (this includes being able to remove or edit content they have just created this session).  This prevents tampering with the database.

Editors can add entries, edit any entries, and if ``editor_can_remove`` is enabled, remove any file, not just those they have entered this session.
### Default Permissions
|     Permissions | Viewer | Viewer (recent) | Editor | Editor (recent) | Admin |
|----------------:|:------:|:---------------:|:------:|:---------------:|:-----:|
|       View Data |   1    |        1        |   1    |        1        |   1   |
|             Add |   0*   |        0*       |   1    |        1        |   1   |
|            Edit |   0    |        1        |   1    |        1        |   1   |
|          Remove |   0    |        1        |   1*   |        1        |   1   |
| View Admin Page |   0    |        0        |   0    |        0        |   1   |

\* indicated default app behavior. This is able to be changed via configuration - either using the web UI (via the /admin page) or directly changing the ``/data/admin.yml`` file.

1 meaning true; 0 meaning false. Recent means this session. For example, if a viewer adds something they can then edit or remove only the recently added item. 

# Userscript
We include a userscript for ease of entry. To install a userscript, first install a userscript extension, such as [Violentmonkey]("https://violentmonkey.github.io/"). With the extension installed, install the userscript by clicking [here](https://github.com/HackmannInterns/bookshelfdb/raw/main/barcode.user.js) or copying and pasting it into a new script.  Ensure that the ``@match`` matches your hosted copy of the app (http://localhost:5000 or https://my.server.domain).

This will allow for easy scanning using scanapp.org, which is linked on the header of the web app. When scanning the book's ISBN code, it will redirect you to the ``Add Book`` page with information already filled out about the book. If an error page is displayed, ensure what you scanned is an ISBN barcode and not another type of barcode.
