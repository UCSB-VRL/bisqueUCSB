# BisQue Module Service Integration

**Step 1 :** To Build the current Branch and Run Bisque Service 

To run on localhost : 

```docker run --name bisque  -p 8080:8080 -p 27000:27000 -v /var/run/docker.sock:/var/run/docker.sock {docker_image_name}```

To run on server :  

```docker run --name bisque --add-host vrl-4090.ece.ucsb.edu:127.0.0.1  -p 8080:8080 -p 27000:27000  -v /var/run/docker.sock:/var/run/docker.sock  {docker_image_name}```


**Step 2 :** Register Modules in Engine Service 

- Go to module manager from bisque profile > Modules
- Enter engine service url
http://vrl-4090.ece.ucsb.edu:8080/engine_service/
or 
http://localhost:8080/engine_service/ 

We will see the dummy EdgeDetection module , register it . 

**Step 3 :** ON BisQue main page > Analyze we will see listed module ( that throws the thumbnail issue )

**Step 4 :** Because of thumnail issue for now module page could be listed under Browse > module > edge detection ( module tg errors are throwing after running it )

**Note :** also refresh Bisque page if module option is not showing up ! 
