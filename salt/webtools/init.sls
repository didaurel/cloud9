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
/home/ec2-user/.config/httpd:
  file.directory:
    - user:  ec2-user
    - group: ec2-user
    - dir_mode: 2700
    - name:  /home/ec2-user/.config/httpd
    - makedirs: true
    - recurse:
      - user
      - group
      - mode
/mnt/docker/logs:
  file.directory:
    - user:  ec2-user
    - group: ec2-user
{% for directory in ['/mnt/docker/datas/elasticsearch','/mnt/docker/logs/elasticsearch'] %}
{{ directory }}:
  file.directory:
    - user:  1000
{% endfor %}
/mnt/docker/webtools-docker-compose.yml:
  file.managed:
    - template: jinja
    - source: salt://webtools/files/docker-compose.yml
    - user:  ec2-user
    - group: ec2-user
    - require: 
      - file: /mnt/docker/datas
/home/ec2-user/.config/httpd/euwebtoolsws.conf:
  file.managed:
    - template: jinja
    - source: salt://webtools/files/euwebtoolsws.conf
    - user:  ec2-user
    - group: ec2-user
    - require: 
      - file: /home/ec2-user/.config/httpd
start-containers:
  cmd.run:
    - name: /usr/local/bin/docker-compose -f /mnt/docker/webtools-docker-compose.yml up -d --force-recreate
    - require:
      - file: /mnt/docker/webtools-docker-compose.yml
      - file: /home/ec2-user/.config/httpd/euwebtoolsws.conf
