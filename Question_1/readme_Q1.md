## Question 1

Firstly, up all the containers via this command:
```
docker-compose up -d
```

After that, open **localhost:5533** pgadmin:

Password = *admin*

In pgadmin open **ai_db**  and open query tool. ai_db password = **admin**. 
In this query tool run the commands in the **answers.sql** file.


To stop containers, run this command:
```
docker-compose down --volumes
```

