expandFS:
  cmd.run:
    - name: |
        DEV=`sudo fdisk -l | egrep -o "/dev[^:]+" | head -n 1` 
        sudo growpart ${DEV} 1
        sudo resize2fs ${DEV}1
