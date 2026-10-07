"""NLE hand-off: FCPXML 1.9 (Final Cut / Premiere / DaVinci Resolve) and CMX3600 EDL.

Cuts are exact (frame-quantised source in/out). Punch-ins are carried as transform keyframes in
FCPXML so a finishing editor opens a timeline that already looks like the render.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape


def _tc(sec: float, fps: int) -> str:
    f = int(round(sec * fps))
    return f"{f // (3600*fps):02d}:{f // (60*fps) % 60:02d}:{f // fps % 60:02d}:{f % fps:02d}"


def write_edl(shots, src: Path, fps: int, title: str, dst: Path) -> Path:
    lines = [f"TITLE: {title}", "FCM: NON-DROP FRAME", ""]
    rec = 0.0
    for i, sh in enumerate(shots, 1):
        d = sh.e - sh.s
        lines.append(f"{i:03d}  AX       AA/V  C        {_tc(sh.s, fps)} {_tc(sh.e, fps)} {_tc(rec, fps)} {_tc(rec + d, fps)}")
        lines.append(f"* FROM CLIP NAME: {src.name}")
        if abs(sh.z0 - 1) > 0.01:
            lines.append(f"* ZOOM {sh.z0:.2f} -> {sh.z1:.2f}")
        lines.append("")
        rec += d
    dst.write_text("\n".join(lines), encoding="utf-8")
    return dst


def write_fcpxml(shots, src: Path, info, fps: int, W: int, H: int, title: str, dst: Path) -> Path:
    fd = f"100/{fps * 100}s"

    def r(sec: float) -> str:
        return f"{int(round(sec * fps)) * 100}/{fps * 100}s"

    total = sum(sh.e - sh.s for sh in shots)
    clips, off = [], 0.0
    for sh in shots:
        d = sh.e - sh.s
        kf = ""
        if abs(sh.z0 - 1) > 0.005 or abs(sh.z1 - 1) > 0.005:
            sx0, sx1 = sh.z0 * 100, sh.z1 * 100
            kf = (f'<adjust-transform><param name="scale"><keyframeAnimation>'
                  f'<keyframe time="{r(sh.s)}" value="{sx0/100:.3f} {sx0/100:.3f}"/>'
                  f'<keyframe time="{r(sh.e)}" value="{sx1/100:.3f} {sx1/100:.3f}"/>'
                  f'</keyframeAnimation></param></adjust-transform>')
        clips.append(f'<asset-clip ref="r2" offset="{r(off)}" name="{escape(src.stem)}" start="{r(sh.s)}" '
                     f'duration="{r(d)}" tcFormat="NDF">{kf}</asset-clip>')
        off += d
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.9">
  <resources>
    <format id="r1" name="FFVideoFormat{H}p{fps}" frameDuration="{fd}" width="{W}" height="{H}"/>
    <asset id="r2" name="{escape(src.stem)}" start="0s" duration="{r(info.duration)}" hasVideo="1" hasAudio="1"
           format="r1" audioSources="1" audioChannels="2">
      <media-rep kind="original-media" src="{src.resolve().as_uri()}"/>
    </asset>
  </resources>
  <library>
    <event name="Video Factory">
      <project name="{escape(title)}">
        <sequence format="r1" duration="{r(total)}" tcStart="0s" tcFormat="NDF">
          <spine>
            {chr(10).join('            ' + c for c in clips).strip()}
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
"""
    dst.write_text(xml, encoding="utf-8")
    return dst
