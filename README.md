# Skyroom recording automation
This repository is a dockerized environment to record classes of vclass.sharif.edu and skyroom.online.

## How to use?
It's simple. Install docker and then create a `downloads` directory and use:

```bash
docker run --rm -v "$(pwd)/downloads:/opt/downloads" atofighi/skyroom-record:latest -u VLASS_URL -d CLASS_DURATION
```

Notes:
 - VCLASS_URL must be the url of class with `https://`.
 - CLASS_DURATION must be the duration of recording in minutes. like `90`

## Development
The main file is `src/main.py`. source code is not clean enough! sorry! ;)

`src/screenshot.py` will screenshot whole screen every second and save it in `./downloads/my_screenshot.png` for development and debugging purpose.


## Roadmap
 1. Add cronjob for schedule recording
 2. Better failure detection (currently use screenshot similarity)
 3. Handling exceptions and retry when something went wrong.
 4. Logging for failure
 5. Refactor code and make it clean
