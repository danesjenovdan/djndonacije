# djndonacije

## local setup
```
docker-compose up --build -d
docker-compose exec donacije python manage.py migrate
docker-compose exec donacije python manage.py createsupseruser

open page in browser: localhost:8080
* finish instalation of mautic
  insert db data:
      - MAUTIC_DB_HOST=mauticdb
      - MAUTIC_DB_USER=root
      - MAUTIC_DB_PASSWORD=mysecret
      - MAUTIC_DB_NAME=mautic
* make user and login with it
* gear -> configure -> API settings
    API enabled -> Yes
    Enable HTTP basic auth -> Yes
* gear -> Users
  create new user test@test.si with password `password`
```

after instalation delete cache folder of Mautic:

```
docker-compose exec mautic bash
rm -rf app/cache/*
```




## TODO make command which finds all active subscription and set field is_active
