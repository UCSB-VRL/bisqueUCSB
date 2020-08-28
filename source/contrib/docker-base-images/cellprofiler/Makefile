ARCHIVES = http://d1zymp9ayga15t.cloudfront.net/content/Examplezips

.DEFAULT_GOAL: build
build:
		docker build -t cellprofiler .

ExampleHumanImages: ExampleHumanImages.zip
		unzip $<

.INTERMEDIATE: ExampleHumanImages.zip
ExampleHumanImages.zip:
		wget ${ARCHIVES}/$@

.PHONY: input
input:
		mkdir -p $@

output:
		mkdir -m 777 -p $@

input/ExampleHuman.cppipe: ExampleHumanImages
		cp ExampleHumanImages/ExampleHuman.cppipe $@

input/AS_09125_050116030001_D03f00d0.tif: ExampleHumanImages
		cp ExampleHumanImages/AS_09125_050116030001_D03f00d0.tif $@

input/AS_09125_050116030001_D03f00d1.tif: ExampleHumanImages
		cp ExampleHumanImages/AS_09125_050116030001_D03f00d1.tif $@

input/AS_09125_050116030001_D03f00d2.tif: ExampleHumanImages
		cp ExampleHumanImages/AS_09125_050116030001_D03f00d2.tif $@

input/filelist.txt: input/AS_09125_050116030001_D03f00d0.tif input/AS_09125_050116030001_D03f00d1.tif input/AS_09125_050116030001_D03f00d2.tif
		echo 'file:///input/AS_09125_050116030001_D03f00d0.tif' >> $@
		echo 'file:///input/AS_09125_050116030001_D03f00d1.tif' >> $@
		echo 'file:///input/AS_09125_050116030001_D03f00d2.tif' >> $@

.PHONY: test
test: input output input/filelist.txt input/ExampleHuman.cppipe
		docker run --volume=`pwd`/input:/input --volume=`pwd`/output:/output cellprofiler -c -r --image-directory=/input --output-directory=/output --pipeline=/input/ExampleHuman.cppipe --file-list=/input/filelist.txt
