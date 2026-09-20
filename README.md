# Rhodonite Pulse

Full-colour Python 3 neon rising-lane rhythm tap for [ElbowOS](https://x.com/ElbowOS).

Four plum lanes. Rose / gold / magenta pulses climb the shaft.
Tap **D F J K** when a pulse kisses the crown ring.

## Play

```bash
pip install -r requirements.txt
python3 rhodonite_pulse.py --play
```

Controls: **D / F / J / K** hit lanes, **R** restart, **Esc** quit.

## Record a 9:16 reel

```bash
python3 rhodonite_pulse.py --record
# or
ELBOWOS_RECORD=1 python3 rhodonite_pulse.py
```

Writes a 15s 1080×1920 H.264 MP4 (libx264, yuv420p, CRF 20, +faststart).

## Links

- Featured: https://x.com/ElbowOS
- Reel (Drive): https://drive.google.com/file/d/1pwS4rkBtL_gsV9K9qVe9-DGzO551CnGv/view?usp=drivesdk
- Source: https://github.com/ApacheAde/elbowos-rhodonite-pulse
