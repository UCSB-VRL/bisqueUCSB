![](source/bqcore/bq/core/public/images/bqlogo_git.png)

***

## Overview 

BisQue is a web-based platform specifically designed to provide researchers with organizational and quantitative analysis tools for up to 5D image data. Users can extend BisQue by creating their own modules that take advantage of cutting edge machine learning algorithms. BisQue’s extensibility stems from two core concepts: flexible metadata facility and an open web-based architecture. Together these empower researchers to create, develop and share novel multimodal data analyses.

### Features
- Bisque is free and open-source
- Flexible textual and graphical annotations
- Cloud scalability: PBs of images, millions of annotations
- Distributed storage: local, iRODS, S3
- Integrated image analysis, high-throughput with Condor
- Analysis in MATLAB, Python, Java+ImageJ
- 100+ biological image formats 
- Very large 5D images (100+ GB)

## Documentation

[__BisQue Documentation__](https://ucsb-vrl.github.io/bisqueUCSB/)

The official documentation covers the [BisQue cloud service](https://bisque.ece.ucsb.edu) running live at UCSB, module development for the platform, and the BQAPI. If you have any questions, feel free to reach out. We will be continuously updating the documentation so check back often for updates!

## Papers using BisQue

* Latypov, M.I., Khan, A., Lang, C.A. et al. Integr Mater Manuf Innov (2019) 8: 52. https://doi.org/10.1007/s40192-019-00128-5
* Polonsky, A.T., Lang, C.A., Kvilekval, K.G. et al. Integr Mater Manuf Innov (2019) 8: 37. https://doi.org/10.1007/s40192-019-00126-7
* Kvilekval K, Fedorov D, Obara B, Singh A, Manjunath BS. Bisque: a platform for bioimage analysis and management. Bioinformatics. 2010 Feb 15;26(4):544-52. doi: 10.1093/bioinformatics/btp699. Epub 2009 Dec 22. PMID: 20031971.

## Active Developers

* Amil Khan  (BisQue Team)
* Satish Kumar  (BisQue Team)
* Mike Goebel

### Built With
* Docker
* ExtJS (UI)
* Imaris Convert (Image Service)
* OpenSlide (Image Service)
* Bio-Formats (Image Service)
* FFMpeg (Image Service)
* libTIFF (Image Service)
* TurboGears (backend)
* SQLAlchemy (backend)

### Acknowledgments

[__License__](https://github.com/UCSB-VRL/bisqueUCSB/blob/master/source/LICENSE)

* Kristian Kvilekval, Dmitry Fedorov, Christian Lang 
* NSF SI2-SSI No.1664172, NSF MCB Grant No. 1715544
* Cyverse at University of Arizona
