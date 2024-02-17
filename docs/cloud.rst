.. _cloud:

Cloud Streaming
***************

*Here we describe how to stream live, low latency video from your IP cameras to cloud and how to visualize the live video in a web browser.*

A good video container format for this is "fragmented MP4" (frag-MP4 aka FMP4).  This is basically the same
format you have in those .mp4 files of yours, but it is fragmented into smaller chunks (aka "boxes"), so that it can be sent, chunk-by-chunk,
for low-latency live video streaming over your LAN or WAN.  

LibValkka is able produce the fragmented MP4 "boxes" for you, while you can read them one-by-one, in your python code.  How to do this, please refer to
the :ref:`tutorial <fragmp4>`.

After obtaining the MP4 boxes, just use your imagination.  You can send them over the internet using websockets, `gRPC <https://grpc.io/>`_, or any protocol of your choice.
You can also dump them into an .mp4 file, and that file is understood by all media clients (just remember to cache and write the ftyp and moov packets in the beginning of the file).
For creating a pipelines like that, please take a look `here <https://github.com/elsampsa/valkka-examples/tree/master/example_projects/basic>`_.

To play live video in your browser, use `Media Source Extensions (MSEs) <https://www.w3.org/TR/media-source/>`_.  Receive the MP4 boxes through a websocket and push them 
into the MSE API to achieve low-latency live video.

This is a true cross-platform solution, that works in Linux, Windows and desktop Mac iOS.  

As of September 2020, iPhone iOS is still lacking the MSEs, so that is the only
device where this approach doesn't work.  
In that case, you should use dynamically generated `HLS playlists <https://developer.apple.com/documentation/http_live_streaming/example_playlists_for_http_live_streaming>`_, while
in this approach it is again convenient to use frag-MP4.

For more information about the frag-MP4 structure, see  `this stack overflow post <https://stackoverflow.com/questions/54186634/sending-periodic-metadata-in-fragmented-live-mp4-stream>`_
and `this github repository <https://github.com/elsampsa/websocket-mse-demo>`_.

MP4 is described extensively in `this document <https://www.iso.org/standard/68960.html>`_.

Remember that not all codec + container format combinations are supported by the major browser.  Most typical combination for video is H264 + MP4.
For a list of supported codec + container formats, please see `this link <https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Video_codecs#codec_details>`_.
Note that H265 support is still lacking behind.

For some more references on the subject, see in 
`here <https://developer.mozilla.org/en-US/docs/Web/API/MediaSource#examples>`_ and 
`here <https://developer.mozilla.org/en-US/docs/Web/API/Media_Source_Extensions_API>`_.
