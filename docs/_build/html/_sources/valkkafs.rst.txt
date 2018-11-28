
.. _valkkafs:

ValkkaFS
========

ValkkaFS is a custom filesystem for storing streaming media data.

Video frames (typically H264) are dumped into a block device, which is a regular file or a disk partition.

You can use a single ValkkaFS instance per camera, but typically you would be streaming live video from several cameras into the same ValkkaFS.  

How does this look like on the disk?  Let's take cameras A, B, C and D.  Uppercase letters designate "seek-points" (i.e. sps, pps, intra-frame sequences), numbers designate timestamps

::
    
    c1 c2 b4 C5 A8 a10 d11 D12 a15 B16 b17 c18 a20 ..
    
Frames from different cameras alternate, so do seek points, while all frames are written in the order of their arrival.

Once limit of the file (or the partition) is reached, frames are written from the beginning of the partition, effectively overwriting oldest frames.

This scheme discards automatically oldest data, while minimizes wear and tear on hard-disk arms in the long run (in the case you are using an entire disk or a partition). When using regular files with ValkkaFS, the underlying filesystem (say, ext4) is not required to manage and grow continuously the space required for streaming data.

The written frame sequences are organized in blocks.  ValkkaFS maintains metadata about the minimum seek-point timestamp and maximum frame timestamp of each block.  The minimum requirement is, that for actively streaming cameras, there is at least one key-frame in each block.

Frames are requested from ValkkaFS on a per-block basis.

For concrete examples of the python API, please refer to the :ref:`Tutorial <valkkafs_tutorial>`.  For more info on ValkkaFS, refer to the `cpp documentation <https://elsampsa.github.io/valkka-core/html/valkkafs.html>`_.  For calculating disk space requirements, keep on reading.

Using an entire partition
-------------------------

*(and an example how to calculate the required disk-space)*

An entire disk or partition can be dedicated to ValkkaFS.

In Linux, disks and partitions appear as block devices under the directory */dev/*.  For example, */dev/sdb* is typically that external hard disk drive you plug into your USB port.

To grant access to a linux user to read and write block devices directly, use the following command:

::

    sudo usermod -a -G disk username
    
After that you still need to logout and login again.

Now you can verify that block devices can be read and written as regular files.  Try this command:

::

    head -n 10 /dev/sdb
    
to read the first ten bytes of that external hard-drive.

ValkkaFS uses **Linux swap partitions** located **on block devices**.  So, the next thing we need, is to create a Linux swap partition on that external (or internal) hard disk.  Use the following command to create the partition */dev/sdb1*

::

    cfdisk /dev/sdb

Let's see how it worked out, so type

::

    sudo fdisk -l
    
You should get something like this:   
    
::

    Device     Start   End        Sectors   Size    Type
    /dev/sdb1  2048    976773134  976771087 465,8G  Linux swap

    
To get the exact size in bytes, type:
    
::

    blockdev --getsize64 /dev/sdb1
    
So, in this case we'd be dedicating an external USB drive of 465 GB for recording streaming video.  

To identify disks, Valkka uses uuid partition identification.  The uuid can be found with

::

    blkid /dev/sdb1
    
Next, suppose that we have:

- 16 cameras
- Each camera having a target bitrate of 2048Kbits per second
- Each camera writing a key-frame every second.  

We'll be scoring around **4 MBytes per second**.

Next, let's have a few seconds worth of video in each block (say, 5 secs) and we'll get a **blocksize of 20 MBytes** (remember to double-check that the blocksize is a multiple of 512 Bytes).

Finally, let's leave out 2% of the disk space and we get **23370 blocks** for our ValkkaFS.

That was 5 secs per block, so this disk is capable of storing **32 hours** of video.

And that is in the worst case scenario where all the cameras are writing to the disk continuously (typically you would want to start recording at movement only).  Nice!  :) 

