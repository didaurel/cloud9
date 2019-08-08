/mnt/docker/datas:
  file.directory:
    - user:  ec2-user
    - group: ec2-user
    - dir_mode: 2755
    - name:  /mnt/docker/datas
    - makedirs: true
    - recurse:
      - user
      - group
      - mode
/mnt/docker/logs:
  file.directory:
    - user:  ec2-user
    - group: ec2-user
/mnt/docker/datas/elasticsearch:
  file.directory:
    - user:  1000
/mnt/docker/logs/elasticsearch:
  file.directory:
    - user:  1000
/mnt/docker/webtools-docker-compose.yml:
  file.managed:
    - template: jinja
    - source: salt://webtools/files/docker-compose.yml
    - user:  ec2-user
    - group: ec2-user
    - require: 
      - file: /mnt/docker/datas
start-containers:
  cmd.run:
    - name: /usr/local/bin/docker-compose -f /mnt/docker/webtools-docker-compose.yml up -d --force-recreate
    - require:
      - file: /mnt/docker/webtools-docker-compose.yml
