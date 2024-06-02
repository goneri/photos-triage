# Simple script to triage incoming photos on NextCloud

Photos are stored in the `/Photos` directory, incoming files come first in the `/Photos/a_trier`.
The script is in charge of moving them to the right directory in the `/Photos` directory.

Build the container:

```
podman build -f Containerfile --tag quay.io/goneri/photos-triage:latest .
```

And run the script:

```
podman run -it --volume ./secret:/secret:z quay.io/goneri/photos-triage:latest
```
