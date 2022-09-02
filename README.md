![](docs/images/bq-github-banner2.svg)

![workflow](https://github.com/UCSB-VRL/bisqueUCSB/actions/workflows/docker-image.yml/badge.svg)
![](https://img.shields.io/badge/BisQue%20Stable%20Release-v1.0.0-brightgreen)

## 🔭 Overview 

BisQue is a web-based platform specifically designed to provide researchers with organizational and quantitative analysis tools for up to 5D image data. Users can extend BisQue by creating their own modules that take advantage of cutting edge machine learning algorithms. BisQue’s extensibility stems from two core concepts: flexible metadata facility and an open web-based architecture. Together these empower researchers to create, develop and share novel multimodal data analyses.




![](docs/images/bisqueviewer.gif)

## 💡 Features
- Bisque is free and open-source
- Flexible textual and graphical annotations
- Cloud scalability: PBs of images, millions of annotations
- Distributed storage: local, iRODS, S3
- Integrated image analysis, high-throughput with Condor
- Analysis in MATLAB, Python, Java+ImageJ
- 100+ biological image formats 
- Very large 5D images (100+ GB)

Start using BisQue now by [__Requesting an account!__](https://docs.google.com/forms/d/e/1FAIpQLSfUCwOdl8Gd1KErPXbLWSPvF74ApT7M142sYQVdwluDUJXMAg/viewform)


## 🤖 Machine Learning Workflows 

![](tutorials/edited-nph-720.mov)



## ✅ Getting Started

### Docker Installation  


#### Download 

Ensure you have the latest release by first running the following pull command:

```
  docker pull amilworks/bisque-module-dev:git
```

### __Intro: BisQue Docker Container__ 

#### Run the BisQue Docker Container 

 To run the docker version of BisQue locally, start a bisque server on the host port 8080:

```
docker run --name bisque --rm -p 8080:8080 amilworks/bisque-module-dev:git
```

and point your browser at `http://localhost:8080`. You should see a BisQue homepage similar to the one on [bisque2.ece.ucsb.edu](https://bisque2.ece.ucsb.edu/client_service/). If you do __not__ see the homepage, check to make sure that port 8080 is not being used by another container or application _and_ that you have correctly mapped the ports using `-p 8080:8080`, where `-p` is short for port.


#### Registering Modules 

To register all the modules to your local server:
   * Login to your BisQue server using admin:admin
   * Find the module manager under the Admin button on the top right hand corner
   * Put `http://localhost:8080/engine_service` in the right panel where it says __Enter Engine URL__ and hit Load
     *  NOTE: Use `localhost:8080` here because it's internal to the container.
   * Drag and Drop __MetaData__ to the left panel---or whatever module you would like---and the module will now be registered and available for use. You can make the module Public by hitting __Set Public__ in the left panel, which basically means the module is Published and ready for public use. 


#### Custom Modules, Copying Folders out of the Container 

If you would like to build and test your own module locally, using host mounted modules will make life easier to build, test, debug, and deploy locally. 

   1. Copy the module directory out of the container and into the folder on your local system named `container-modules`. 

      ```
         docker cp bisque:/source/modules container-modules
      ```
   2. Copy your module into the `container-modules` folder on your local system.
   3. Restart the container with host mounted modules. Be careful with the command `$(pwd)/container-modules` that we are using here. If the `/container-modules` is __not__ in the specified path, you will not see any of the modules during the registration process.

      ```
      docker stop bisque
      docker run --name bisque --rm -p 8080:8080 -v $(pwd)/container-modules:/source/modules  amilworks/bisque-module-dev:git
      ```
   4. Register your module from the above steps in "3. __Registering Modules. __", using the Module Manager.
   
> __Pushing your Module to Production.__ If you feel that your module is ready to be added to the production version of BisQue, please feel free to contact us and we will gladly begin the process.

#### Data Storage 

Use an external data directory so you don't lose data when the service stops
    - Uploaded image and workdirs are store in `/source/data`.  You can change this to be a host mounted directory with

```sh
docker run --name bisque --rm -p 8080:8080 -v $(pwd)/container-data:/source/data  amilworks/bisque-module-dev:git
```

  - The default sqlite database is stored inside the container at `/source/data/bisque.db`
  - The uploaded images are stored inside the container at `/source/data/imagedir`
  
  
#### View Downloaded Images, Running Containers  

List all the docker __images__ on your system:

```sh
docker images
```

List all running __containers__ on your system:

```sh
docker ps
```

#### SSH into the Container 

If you would like to see everything inside the container, you can use the following command _while the container is running_:

```sh
docker exec -it amilworks/bisque-module-dev:git bash
```
The `-it` flag enables you to run interactively inside the container. There are numerous other flags you can take advantage of as shown here:

```bash
--detach ,      -d    Detached mode: run command in the background
--detach-keys         Override the key sequence for detaching a container
--env ,         -e    Set environment variables
--interactive , -i    Keep STDIN open even if not attached
--privileged          Give extended privileges to the command
--tty ,         -t    Allocate a pseudo-TTY
--user ,        -u    Username or UID (format: <name|uid>[:<group|gid>])
--workdir ,     -w    Working directory inside the container
```

Now, let's say you want to ssh into an image without fully starting BisQue. More precisely, you want to ssh into a non-running container. You can accomplish this by running:

```sh
docker run -it amilworks/bisque-module-dev:git bash
```

If you want to __exit__, simply type `exit` and you will be taken back outside of the container. 

#### Stop the Container  

Say you are done playing with your container for today, you can stop the container by using the following command:

```sh
docker stop amilworks/bisque-module-dev:git 
docker stop {YOUR_CONTAINER_NAME} #  <--- If you named the container
```



## 💾 Documentation

[__BisQue Documentation__](https://ucsb-vrl.github.io/bisqueUCSB/)

The official documentation covers the [BisQue cloud service](https://bisque.ece.ucsb.edu) running live at UCSB, module development for the platform, and the BQAPI. If you have any questions, feel free to reach out. We will be continuously updating the documentation so check back often for updates!

## Papers using BisQue

* Jangid, Devendra K., Neal R. Brodnik, Amil Khan, Michael G. Goebel, McLean P. Echlin, Tresa M. Pollock, Samantha H. Daly, and B. S. Manjunath. __"3D Grain Shape Generation in Polycrystals Using Generative Adversarial Networks."__ Integrating Materials and Manufacturing Innovation (2022): 1-14.
*  Zhang, Angela, Amil Khan, Saisidharth Majeti, Judy Pham, Christopher Nguyen, Peter Tran, Vikram Iyer, Ashutosh Shelat, Jefferson Chen, and B S Manjunath. __“Automated Segmentation and Connectivity Analysis for Normal Pressure Hydrocephalus.”__ BME Frontiers 2022 (2022): 1–13.
* Latypov, Marat I., Amil Khan, Christian A. Lang, Kris Kvilekval, Andrew T. Polonsky, McLean P. Echlin, Irene J. Beyerlein, B. S. Manjunath, and Tresa M. Pollock. __"BisQue for 3D materials science in the cloud: microstructure–property linkages."__ Integrating Materials and Manufacturing Innovation 8, no. 1 (2019): 52-65.
* Polonsky, Andrew T., Christian A. Lang, Kristian G. Kvilekval, Marat I. Latypov, McLean P. Echlin, B. S. Manjunath, and Tresa M. Pollock. __"Three-dimensional analysis and reconstruction of additively manufactured materials in the cloud-based BisQue infrastructure."__ Integrating Materials and Manufacturing Innovation 8, no. 1 (2019): 37-51.
* Kvilekval K, Fedorov D, Obara B, Singh A, Manjunath BS. __Bisque: a platform for bioimage analysis and management__. Bioinformatics. 2010 Feb 15;26(4):544-52. doi: 10.1093/bioinformatics/btp699. Epub 2009 Dec 22. PMID: 20031971.

## Team

* Amil Khan  (Project Lead)
* Satish Kumar 
* Mike Goebel
* Connor Levenson
* Chandrakanth Gudavalli
* Tom Jiang


### Acknowledgments

* NSF SI2-SSI No.1664172, NSF MCB Grant No. 1715544

[__License__](https://github.com/UCSB-VRL/bisqueUCSB/blob/master/source/LICENSE)
