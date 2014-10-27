# Introduction
These are all the files to get a Docker instance running with eduVPN.

To build the Docker image:

    docker build --rm -t fkooman/eduvpn .

To run the container:

    docker run -d -p 443:443 fkooman/eduvpn

That should be all. You can replace `fkooman` with your own name of course.
