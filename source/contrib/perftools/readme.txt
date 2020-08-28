makehttperf generates testing scripts using httperf, it has two modes of operation. 
In either mode testing is done with all the images that are fetched using a user-given url.
The easiest call is to fetch image resources form data service with a limit:

python makehttperf.py "http://TEST_HOST/data_service/image?limit=10" > test.py

One should replace TEST_HOST for the actual host url.

It's also possible to make a more complex fetch using all the available attributes. 
In the following example we'll fetch the most recent 10 images:

python makehttperf.py "http://TEST_HOST/data_service/image?tag_order=%22@ts%22:desc&offset=0&limit=10" > test.py

from now on we'll be referring to the image fetching url as IMAGE_URL



Mode 1 - one session
--------------------

This is a default mode where a script is created that first cleans image service 
cache for all the requested images and then executes 100 httperf requests to fetch those images.
Therefore this mode mixes fetching brand new and pre-computed thumbnails imitating normal operation.
The second generated file file "req.txt" contains the httperf testing session.

1) First we need to generate the testing script:

python makehttperf.py IMAGE_URL > test.py

2) Now run the generated test script:

python test.py

This script will call httperf with the default of 8 parallel connections and will 
run 100 connections overall. It's possible to chnage those values directly in the 
generated test.py changing --rate=8 and --num-conn=100




Mode 2 - httperf sessions
-------------------------

In this mode the testing session file "reqs.txt" contains a two part session first cleaning all 
caches and then fetching thumbnails for them. Thus excersising more the ability of the server to
cope with many image processing requests.

Simply use --gensession argument to use this mode:

python makehttperf.py --gensession IMAGE_URL > test.py

the test.py script in this case simply contains the proper command line to call httperf
with the default of 8 parallel connections and will 100 connections overall. 
It's possible to chnage those values directly in the 
generated test.py changing --rate=8 and --num-conn=100

