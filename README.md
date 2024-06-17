# Bookshelfdb
Hackmann library scan and DB



## Using Docker Compose
Create a ```docker-compose.yml``` file with the following contents. Add in the UID and GID that you would like to run as in the user line below, or remove the user line to use the default (root).
```services:
  flask-app:
    image: "alexreynen/bookshelfdb:latest"
    container_name: bookshelfdb
    volumes:
      - ./data:/app/data
    environment:
      - BOOKSHELFDB_PASSWORD=changeme
      - BOOKSHELFDB_PASSWORD_EDITOR=changeme2
      - BOOKSHELFDB_SECRET_KEY=changeme
    ports:
      - "5000:5000"
```

The environmental variables BOOKSHELFDB_PASSWORD is for admin password for the database, BOOKSHELFDB_PASSWORD_EDITOR is for edit permissions, and BOOKSHELFDB_SECRET_KEY is being used for security, change this to something secure.


Then while in the same folder as the docker-compose.yml run:

```
docker compose up
```

To run the container in background add -d to the above command.


# Permissions

There are three tiers of permissions that can be use by anyone accessing the database, general user, editor, and admin. The admin can change how the other two user types are allowed to interact with the database as well as having full access, these permissions are visible in admin.yml
```
default_address: place
editor_can_remove: false
visitor_can_add: true
```

general user can view the database and assuming visitor_can_add is enabled, add new content and remove or edit content they have created this session

editor can edit any entries and if editor_can_remove is enabled, remove any file, not just those they have entered this session.



# User script
