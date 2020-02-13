# README #

BisQue:

An application for the management and analysis of complex multi-dimensional data including bio-imaging and other scientific data.

### How do I get set up? ###

  - Original full instruction [http://biodev.ece.ucsb.edu/projects/bisque]

#### Quick setup using docker ####

  1.  Getting a running bisque server locally on your development machine
  2.  Using host mounted modules to make it easier to edit
  3.  Registering a module to your local server
  4.  Use an external data directory and database so you don't lose data when service stops
  5.  This script [https://bitbucket.org/CBIucsb/bisque-stable/downloads/build_bisque_docker_modules.sh] run the following commands for you.

Full instructions

  0. Ensure you have the latest stable locally

     ```
       docker pull cbiucsb/bisque05:stable
     ```

  1. Run a bisque server on the host port 9898:

    ```
    docker run --name bisque --rm -p 9898:8080 cbiucsb/bisque05:stable
    ```
    and point your browser at `http://<hostname>:9898`


  2. Using host mounted modules to make it easier to edit.

     1. Copy the module directory  out of the container

      ```
         docker cp bisque:/source/modules container-modules
      ```

     2. restart the container with host mounted module

        ```
        docker stop bisque
        docker run --name bisque --rm -p 9898:8080 -v $(pwd)/container-modules:/source/modules  cbiucsb/bisque05:stable
        ```

  3. Registering a module to your local server
     *  Login to your bisque server using admin:admin
     * Find the module manager under Admin button
     * put `http://localhost:8080/engine_service` in the right panel and hit load
       *  use localhost:8080 here because it's internal to the container.
     * Drag and Drop "MetaData" to the left panel


  4.  Use an external data directory so you don't lose data when service stops
      - Uploaded image and workdirs are store in /source/data.  You can change this to be a host mounted directory with

      ```
       docker run --name bisque --rm -p 9898:8080 -v $(pwd)/container-data:/source/data  cbiucsb/bisque05:stable
      ```

      - The default sqlite database is stored inside the container at /source/data/bisque.db
      - The uploaded images are stored inside the container at /source/data/imagedir


  5.  (Optional) Use  an external database server for performance and durability

    ```
       docker run --name bisque --rm -p 9898:8080 -e BISQUE_DBURL=postgresql://dbhost:5432/bisque  cbiucsb/bisque05:stable
    ```

  6.  (Optional) All together:

    ```
        docker run --name bisque --rm -p 9898:8080 \
             -v $(pwd)/container-data:/source/data \
             -v $(pwd)/container-modules:/source/modules \
             -e BISQUE_DBURL=postgresql://dbhost:5432/bisque \
             cbiucsb/bisque05:stable

    ```

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines
