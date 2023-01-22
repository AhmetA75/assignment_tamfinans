## Question 2

Firstly, up all the containers via this command:
```
docker-compose up -d
```

After that, install requirements in virtual environment via:
```
pip3 install -r requirements.txt
```

To insert the data and calculate the similarities run **assignment_Q2.py** file with:
```
python3 assignment_Q2.py
```
 
For showing results and running *RedisGraph* queries please visit **localhost:8001** in the browser.
- Host name is => **redis-stack-container**
- Port => **6379**


To stop containers, run this command:
```
docker-compose down --volumes
```
