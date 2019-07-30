copy_route53_service:
  file.managed:
   - name: /etc/init.d/route53
   - source: salt://config/files/route53.service
   - mode: 755
   
enabled_route53_service:
  service.running:
    - name: route53
    - enable: true
