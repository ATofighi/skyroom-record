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

There is also a simple flask app in `src/app.py` for viewing current window and can do clicks for test. You can expose port 5000 for viewing current screen for example with this command:
```bash
docker run --rm -v "$(pwd)/downloads:/opt/downloads" -p 5000:5000 atofighi/skyroom-record:latest -u VLASS_URL -d CLASS_DURATION
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
