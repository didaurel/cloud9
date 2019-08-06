expandFS:
  cmd.run:
    - name: |
        DISK=`sudo fdisk -l | egrep -o "/dev[^:]+" | head -n 1`
        PART=`sudo df -h / | egrep -o "/dev[^ ]+" | head -n 1` 
        sudo growpart ${DISK} 1
        sudo resize2fs ${PART}
