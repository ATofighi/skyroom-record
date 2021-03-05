# Skyroom recording automation
![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/atofighi/skyroom-record)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/atofighi/skyroom-record)
![Docker Pulls](https://img.shields.io/docker/pulls/atofighi/skyroom-record)

This repository is a dockerized environment to record classes of vclass.sharif.edu and skyroom.online.

## How to use?
It's simple. Install docker and then create a `downloads` directory and use:

```bash
docker run --rm -v "$(pwd)/downloads:/opt/downloads" atofighi/skyroom-record:latest -u VLASS_URL -d CLASS_DURATION -n test-class -e encoding
```

Notes:
 - VCLASS_URL must be the url of class with `https://`.
 - CLASS_DURATION must be the duration of recording in minutes. like `90`
 - Your recorded video will be saved on `./downloads/test-class/NOW/video.mp4`.
 - Encoding preset -e
 
      This option converts the .webm file to a .mp4 file. It has encoding presets that should be defined otherwise no conversion would occur.

      `size-optimized` -for uploading, low size, low quality, somewhat fast

      `speed-optimized` -for high speed with good quality but higher size

      `quality-optimized` -for high quality with good compression but slow

      `no-encoding` -default -best quality, medium size

   

## Development
The main file is `src/main.py`. source code is not clean enough! sorry! ;)

There is also a simple flask app in `src/app.py` for viewing current window and can do clicks for test. You can expose port 5000 for viewing current screen for example with this command:
```bash
docker run --rm -v "$(pwd)/downloads:/opt/downloads" -p 5000:5000 atofighi/skyroom-record:latest -u VLASS_URL -d CLASS_DURATION -n test-class
```
And see `http://localhost:5000`. (Note: If you click on this page. App will click on docker window on that point.)


## Roadmap
Done:
 - Handling exceptions and retry when something went wrong.
 - Logging for failure

TODO:
 - Login with CW and vclass user/pass.
 - Add cronjob for schedule recording
 - Better failure detection (currently use screenshot similarity)
 - Refactor code and make it clean

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>, and it is offered “as-is”, without warranty, and we disclaim liability for any type of damages or problems resulting from using or abusing the project.
