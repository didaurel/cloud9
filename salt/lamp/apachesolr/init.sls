include:
  - lamp.httpd
  - docker

fpfis/solr5:
  docker_image.present:
    - tag: latest
    - force: True

ApacheSolr:
  docker_container.running:
    - image: fpfis/solr5
    - watch_action: SIGHUP
    - detach: True
    - force: True
    - port_bindings:
      - 8983:8983
    - restart_policy: always

/etc/httpd/conf.d/apachesolr.conf:
  file.managed:
    - source: salt://lamp/apachesolr/files/apachesolr.conf
    - listen_in:
      - service: httpd
    - require:
      - httpd24

{% set tika_version = salt['pillar.get']('tika:version', "1.5") %}
# Tika from archive:
# https://archive.apache.org/dist/tika/
/home/ec2-user/environment/.c9/tika/tika-app-{{ tika_version }}.jar:
  file.managed:
    - source: http://archive.apache.org/dist/tika/tika-app-{{ tika_version }}.jar
    - source_hash: https://archive.apache.org/dist/tika/tika-app-{{ tika_version }}.jar.md5
    - makedirs: true
    - user: ec2-user
    - group: ec2-user

# Tika symlink:
tika_symlink:
  file.symlink:
    - name: /home/ec2-user/environment/.c9/tika/tika-app-current.jar
    - target: /home/ec2-user/environment/.c9/tika/tika-app-{{ tika_version }}.jar
    - onlyif: "test ! -d /home/ec2-user/environment/.c9/tika/tika-app-{{ tika_version }}.jar"
    - user: ec2-user
    - group: ec2-user
