{{ salt['cmd.run']('touch /tmp/profile') }}
{% do salt['file.write']('/tmp/profile', "webtools") %}

include:
  - profiles.common
  - docker.docker-compose
  - docker.bashrc
  - webtools
