# Introduction
These are all the files to get a Docker instance running with eduVPN.

To build the Docker image:

    $ sudo docker build -t fkooman/eduvpn .

To run the container:

    $ sudo docker run -d -p 443:443 fkooman/eduvpn

That should be all. You can replace `fkooman` with your own name of course.
