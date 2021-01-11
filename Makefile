






bisque05-caffe-xenial: source
	docker build -t biodev.ece.ucsb.edu:5000/bisque05-caffe-xenial:info_update -f Dockerfile.caffe.xenial .
	#docker push amilworks/bisque05-caffe-xenial:flour-v0.6.1
	#docker run -u 1000:1000 -w /source -p 8765:8080  bisque05 bootstrap start
#docker run -u 1000:1000 -w /source -v $(CURDIR)/reports:/source/reports bisque05 bootstrap



source:  source/*
	#rm -rf source
	#hg clone ../bq059 source
	#cp -al ../bq059 source
	rm -rf source/data source/.hg source/public source/config

clean:
	rm -rf source reports
