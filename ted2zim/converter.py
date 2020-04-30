#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import pathlib
import subprocess
from zimscraperlib.logging import nicer_args_join
from zimscraperlib.imaging import resize_image

from .constants import logger

def post_process_video(video_dir, video_id, video_format, low_quality, skip_recompress=False):
    # apply custom post-processing to downloaded video
    # - resize thumbnail
    # - recompress video if incorrect video_format or low_quality requested
    # find downloaded video from video_dir
    files = [p for p in video_dir.iterdir() if p.stem == "video" and p.suffix != ".jpg"]
    if len(files) == 0:
        logger.error(f"Video file missing in {video_dir} for {video_id}")
        logger.debug(list(video_dir.iterdir()))
        raise FileNotFoundError(f"Missing video file in {video_dir}")
    if len(files) > 1:
        logger.warning(f"Multiple video file candidates for {video_id} in {video_dir}. Picking {files[0]} out of {files}")
    src_path = files[0]

    # resize thumbnail. we use max width:248x187px in listing
    # but our posters are 480x270px
    resize_image(
        src_path.parent.joinpath("thumbnail.jpg"), width=480, height=270, method="cover"
    )

    # don't reencode if not requesting low-quality and received wanted format
    if skip_recompress or (not low_quality and src_path.suffix[1:] == video_format):
        return

    dst_path = src_path.parent.joinpath(f"video.{video_format}")
    recompress_video(src_path, dst_path, video_format)

def recompress_video(src_path, dst_path, video_format):
    """ re-encode in-place (via temp file) for format at lower quality

        references:
            - https://trac.ffmpeg.org/wiki/Limiting%20the%20output%20bitrate
            - https://ffmpeg.org/ffmpeg-filters.html#scale

            - webm options: https://trac.ffmpeg.org/wiki/Encode/VP9
            - h264 options: https://trac.ffmpeg.org/wiki/Encode/H.264
                            https://sites.google.com/site/linuxencoding/x264-ffmpeg-mapping

            - vorbis options: https://trac.ffmpeg.org/wiki/TheoraVorbisEncodingGuide
            - acc options: https://trac.ffmpeg.org/wiki/Encode/AAC
    """

    tmp_path = src_path.parent.joinpath(f"video.tmp.{video_format}")

    video_codecs = {"mp4": "h264", "webm": "libvpx"}
    audio_codecs = {"mp4": "aac", "webm": "libvorbis"}
    params = {"mp4": ["-movflags", "+faststart"], "webm": []}

    args = ["ffmpeg", "-y", "-i", f"file:{src_path}"]

    args += [
        # target video codec
        "-codec:v",
        video_codecs[video_format],
        # compression efficiency
        "-quality",
        "best",
        # increases encoding speed by degrading quality (0: don't speed-up)
        "-cpu-used",
        "0",
        # set output video average bitrate
        "-b:v",
        "300k",
        # quality range (min, max), the higher the worst quality
        # qmin 0 qmax 1 == best quality
        # qmin 50 qmax 51 == worst quality
        "-qmin",
        "30",
        "-qmax",
        "42",
        # constrain quality to not exceed this bitrate
        "-maxrate",
        "300k",
        # decoder buffer size, which determines the variability of the output bitrate
        "-bufsize",
        "1000k",
        # nb of threads to use
        "-threads",
        "8",
        # change output video dimensions
        "-vf",
        "scale='480:trunc(ow/a/2)*2'",
        # target audio codec
        "-codec:a",
        audio_codecs[video_format],
        # set sample rate
        "-ar",
        "44100",
        # set output audio average bitrate
        "-b:a",
        "128k",
        # increase queue size to prevent failure on system without swap
        "-max_muxing_queue_size",
        "9999",
    ]
    args += params[video_format]
    args += [f"file:{tmp_path}"]

    logger.info(f"recompress {src_path} -> {dst_path} {video_format=}")
    logger.debug(nicer_args_join(args))

    ffmpeg = subprocess.run(args)
    ffmpeg.check_returncode()

    # delete original
    src_path.unlink()
    # rename temp filename with final one
    tmp_path.replace(dst_path)
