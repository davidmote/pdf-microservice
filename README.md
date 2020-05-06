
Note: This is a clone of https://github.com/Codebiosys/pdf-microservice.git,
which is no longer maintained.

# PDF Microservice

This service exposes an HTTP endpoint for uploading html mustache documents and receiving
a PDF file attachment response.



## Project Goals

* Must include dynamic templates (user should be able to choose template)
* Should be able to update template without having to update software
* Must be able to specify a header and footer
* Must be able to include images
* Must be able to include CSS styling


## Implementation

### pydf

This tool uses the [Pydf](http://github.com/davidmote/pydf.git) library
to generate a pdf

### flask

This tool uses [Flask](http://flask.pocoo.org/) to serve the http endpoint


### Installation

1. Clone the application:

    ```
    > git clone git@github.com:davidmote/pdf-microservice
    > cd pdf-microservice
    ```

1. Provision a new Docker machine called `pdf-microservice`:

    ```
    > docker-machine create -d virtualbox pdf-microservice
    > eval $(docker-machine env pdf-microservice)
    > docker-machine ls
    NAME                  ACTIVE   DRIVER       STATE     URL                         SWARM   DOCKER        ERRORS
    pdf-microservice   *        virtualbox   Running   tcp://192.168.99.102:2376           v18.06.0-ce
    ```

    **Note the asterisk in the "ACTIVE" column.**

1. Build the application stack and start the services:

    ```
    > docker-compose up -d --build
    ```

1. Once the application begins, the build process is complete you can post
   the following via http to http://{docker-machine-ip}:8000/

   Parameter | Required | Type | Description
   --- | --- | --- | ---
   template | Yes | HTML or ZIP | An HTML template file or bundle of assets to use
   params | No | JSON | Paramters to pass to the Mustache template
   config | No | JSON | Weasyprint configuration

   The application will respond with a pdf stream of the resulting pdf.


## Development and Testing

```
  > mkvirtualenv pydf-microservice
  > git clone https://github.com/davidmote/pdf-microservice.git
  > cd pdf-microservice
  > pip install -r requirements-develop.txt
  > pip install -e .
  > pytest -vv
```

## Contributing
If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are welcome.
