import ffmpeg
from django.http import HttpResponseBadRequest, StreamingHttpResponse, JsonResponse
import os
import time
from django.shortcuts import get_object_or_404, render
from core.models import Post
from core.utils import related_tools
from yt_dlp import YoutubeDL
from yt_dlp.utils import UnsupportedError
from tools.tools.Youtube import YouTube


def merge_video_audio(video_url, audio_url, output_filepath):
    input_video = ffmpeg.input(video_url)
    input_audio = ffmpeg.input(audio_url)
    (
        ffmpeg
        .concat(input_video, input_audio, v=1, a=1)
        .output(output_filepath)
        .run(overwrite_output=True)
    )


def merge_and_stream(output_filepath):
    with open(output_filepath, 'rb') as f:
        while True:
            f.seek(-1, 2)
            last_size = f.tell()
            while f.tell() < last_size:
                time.sleep(2)
            chunk = f.read(1024)
            if not chunk:
                break
            yield chunk


async def download_view(request):
    video_url = "https://rr2---sn-jboxuo2-3uhe.googlevideo.com/videoplayback?expire=1706210041&ei=mV6yZfTjIcbOjuMPqvmwcA&ip=111.119.49.217&id=o-AFsTSG3tUjt6cRN3p_JW01rj4JE6yRdacKw3scldP-L2&itag=22&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&mh=iF&mm=31%2C29&mn=sn-jboxuo2-3uhe%2Csn-qxaelnek&ms=au%2Crdu&mv=m&mvi=2&pl=24&initcwndbps=803750&vprv=1&svpuc=1&mime=video%2Fmp4&cnr=14&ratebypass=yes&dur=279.870&lmt=1705567651917736&mt=1706188173&fvip=4&fexp=24007246&beids=24350017&c=ANDROID&txp=4532434&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cvprv%2Csvpuc%2Cmime%2Ccnr%2Cratebypass%2Cdur%2Clmt&sig=AJfQdSswRgIhANno_CJ_n4cxALG7G8Zl8B4DHWTnE_C5ZSUVOgX017wyAiEAwe4W_0esMHXsXiluViRs1ZqcBNTHWL1o3kiYeecPyNI%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AAO5W4owRQIhAMLgIK8OXmEIEoSumxi7JW1-UoCx8fIB-iyxp1U8hJdWAiBIku3n_QjC2x7WJF1IF828OGxjrj1ul65TZXzgE7yfFg%3D%3D"
    audio_url = "https://rr2---sn-jboxuo2-3uhe.googlevideo.com/videoplayback?expire=1706210041&ei=mV6yZfTjIcbOjuMPqvmwcA&ip=111.119.49.217&id=o-AFsTSG3tUjt6cRN3p_JW01rj4JE6yRdacKw3scldP-L2&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&mh=iF&mm=31%2C29&mn=sn-jboxuo2-3uhe%2Csn-qxaelnek&ms=au%2Crdu&mv=m&mvi=2&pl=24&initcwndbps=803750&vprv=1&svpuc=1&mime=audio%2Fwebm&gir=yes&clen=4736616&dur=279.841&lmt=1705566832666906&mt=1706188173&fvip=4&keepalive=yes&fexp=24007246&beids=24350017&c=ANDROID&txp=4532434&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cvprv%2Csvpuc%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgD6HMWJChYeJfGqm27JDqB8FvgYMpOTSPGejIUXYBPTcCIQD2z-0WNfTDk_oNdHoHSHH7g6JIh4heN3N_Mm-iIVp34A%3D%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AAO5W4owRQIhAMLgIK8OXmEIEoSumxi7JW1-UoCx8fIB-iyxp1U8hJdWAiBIku3n_QjC2x7WJF1IF828OGxjrj1ul65TZXzgE7yfFg%3D%3D"
    video_size = 1111
    audio_size = 1053

    output_filepath = './merged.mp4'

    merge_video_audio(video_url, audio_url, output_filepath)
    return JsonResponse({})


    # Create a flag to check if the merging is completed
    merging_completed = False

    try:
        response = StreamingHttpResponse(
            streaming_content=merge_and_stream(output_filepath),
            content_type="video/mp4",
        )
        response['Content-Disposition'] = f"attachment; filename={os.path.basename(output_filepath)}"

        # Close the connection after the download is complete
        response['Connection'] = 'close'

        return response
    except Exception as e:
        return HttpResponseBadRequest(f"Error merging files. {str(e)}")


def single_tool_view_raw(request):
    download_url = "https://www.youtube.com/watch?v=2Vv-BfVoq4g"
    with YoutubeDL({}) as ydl:
        info = ydl.extract_info(download_url, download=False)
        return JsonResponse(info, safe=False)


# Create your views here.
def single_tool_view(request, slug):
    try:
        download_url = "https://www.youtube.com/watch?v=2Vv-BfVoq4g"
        youtube = YouTube(download_url)
        urls = youtube.get_youtube_videos()
        return JsonResponse(urls, safe=False)
    except UnsupportedError:
        return JsonResponse({
            "success": False,
            "message": "This URL is not supported"
        }, safe=False)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, safe=False)
    # ffmpeg -i video.mp4 -i audio.mp4 -c:v copy -c:a aac output.mp4

    tool = get_object_or_404(Post, post_type="tool", slug=slug, status="active")
    context = {
        "results": False,
        "tool": tool,
        "related_tools": related_tools(Post, tool.category),
        "popular_tools": related_tools(Post, None, tool.id)
    }

    return render(request, "tools/page.html", context)
