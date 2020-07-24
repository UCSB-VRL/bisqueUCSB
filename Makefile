





bisque05: source
	docker build -t bisque05_tomsatishamilmike:griffin .
	#docker run -u 1000:1000 -w /source -p 8765:8080  bisque05:jessie bootstrap start
	#docker run -u 1000:1000 -w /source -v $(CURDIR)/reports:/source/reports bisque05:jessie bootstrap
	#docker run -u 1000:1000 -w /source -v $(CURDIR)/reports:/source/reports bisque05:jessie bootstrap

bisque05-test:
	docker run -v $(CURDIR)/reports:/source/reports bisque05:jessie bootstrap pylint

bisque05-stretch: source
	docker build -t bisque05-stretch_tomamilmikesatishgriffin:dev -f Dockerfile.stretch .

bisque05-stretch-test:
	docker  run --rm -v $(CURDIR)/reports:/source/reports bisque05-stretch:dev bootstrap pylint

bisque05-stretch-run:
	docker run --rm -p 8181:8080 bisque05-stretch:dev

bisque05-caffe-xenial: source
	docker build -t bisque-developer-beta:0.7-broccolli -f Dockerfile.caffe.xenial .
	#docker run -u 1000:1000 -w /source -p 8765:8080  bisque05 bootstrap start
#docker run -u 1000:1000 -w /source -v $(CURDIR)/reports:/source/reports bisque05 bootstrap
#docker run -u 1000:1000 -w /source -v $(CURDIR)/reports:/source/reports bisque05 bootstrap


source:  source/*
	#rm -rf source
	#hg clone ../bq059 source
	#cp -al ../bq059 source
	rm -rf source/data source/.hg source/public source/config

clean:
	rm -rf source reports
