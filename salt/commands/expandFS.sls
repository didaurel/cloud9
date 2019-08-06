expandFS:
  cmd.run:
    - name: |
        DEV=`fdisk -l | egrep -o "/dev[^:]+"` 
        sudo growpart ${DEV} 1
        sudo resize2fs ${DEV}1
