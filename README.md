## Usage

### Build

Build `home-test` docker image from Dockerfile:

    docker build -t home-test .

### Run Docker Image

Run the docker image and login into `bash`:

    docker run -it home-test


### Run Application

Run the application and get the help page

    root@2408f0b971ed:~# ./fetch -h
    usage: Fetch webpages and saves them do disk [-h] [--metadata] WEB-URL [WEB-URL ...]

    positional arguments:
        WEB-URL     Collection of web url's to fetch

    options:
      -h, --help  show this help message and exit
      --metadata  Print metadata information about the web url's

