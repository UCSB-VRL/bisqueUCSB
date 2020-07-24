
# Build the developer image of BisQue

bisque05-caffe-xenial: source
	docker build -t bisque-developer-beta:0.7-broccolli -f Dockerfile.caffe.xenial .

