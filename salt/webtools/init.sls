mysql-client:
  pkg.latest:
    - pkgs:
      - mysql{{ salt['pillar.get']('webtools:mysql_version','latest')|replace(".", "") }}
/mnt/docker:
  file.directory:
    - user:  ec2-user
    - group: ec2-user
    - name:  /mnt/docker
/mnt/docker/docker-compose.yml:
  file.managed:
    - template: jinja
    - source: salt://webtools/files/docker-compose.yml
    - user:  ec2-user
    - group: ec2-user
    - require: 
      - file: /mnt/docker