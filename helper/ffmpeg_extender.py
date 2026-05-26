import json
import subprocess
from ffmpeg import Error
from ffmpeg._utils import convert_kwargs_to_cmd_line_args


def probe_bytes(data: bytes, cmd='ffprobe', **kwargs):
    """Run ffprobe on raw bytes and return JSON metadata."""

    args = [cmd, '-show_format', '-show_streams', '-of', 'json']
    args += convert_kwargs_to_cmd_line_args(kwargs)
    args += ['pipe:0']  # 👈 key difference

    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,   # 👈 required for piping
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = p.communicate(input=data)

    if p.returncode != 0:
        raise Error('ffprobe', out, err)

    return json.loads(out.decode('utf-8'))
