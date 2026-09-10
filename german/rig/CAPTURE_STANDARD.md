# Capture standard

Tape this next to the rig. Every photo in the dataset must follow it, and the
live demo must run under the same conditions. If the capture changes, the model
has to be retrained.

## Building the fixture

1. `python scripts/make_markers.py` then print `rig/markers.png` at **100% scale**
   (no "fit to page" — that changes the marker size and the detector cares).
2. Cut out the four squares **keeping the white border**. The border is part of
   the marker; without it the detector will not see it at all.
3. Glue them to the corners of a stiff card or board, in the printed order:
   id 0 top-left, id 1 top-right, id 2 bottom-right, id 3 bottom-left.
4. Tape an outline of the PCB in the middle so every board sits in the same place.
5. Keep the card flat. A bent card bends the geometry and the crop drifts.

## Phone

- Mounted on a stand, lens pointing straight down, roughly 15 to 20 cm above.
- All four markers fully inside the frame with a margin. If a marker is clipped
  the photo is discarded.
- Settings, Camera, Formats, **Most Compatible** so photos are JPEG not HEIC.
- Before each session, long-press the board in the Camera app to lock exposure
  and focus. The yellow AE/AF LOCK banner must be showing.
- Flash off. Never use it: it blows out the polarity band, which is the one
  feature that matters.

## Light

- One lamp, off to the side, diffused through a sheet of paper.
- No window light. Daylight changes over the session and the model learns the
  time of day instead of the part.
- Room light stable. Do not switch the ceiling light on and off mid-session.

## Shooting

- One physical board keeps one board id for its whole life. Never reuse an id
  for a different board, and never give the same board two ids.
- Between bursts, deliberately vary: lamp position, board shifted a few mm
  inside its outline, card tilted slightly, phone height a centimetre, a
  fingerprint or speck of dust. That variation is what makes the model robust.
- Aim for 200 to 500 usable photos per class across at least five boards.

## Rules that are not negotiable

- **Wrong boards must be real.** Get scrap or rework boards with the part
  physically placed backwards. Never fake a reversed part by rotating a photo
  180 degrees: that rotates the silkscreen and pads too, and the model learns
  the silkscreen instead of the component.
- **Never mix components in one dataset.** One config, one designator.
- **Discard, do not fix.** A photo that fails alignment or the blur gate is
  deleted, not rescued. `results/logs/align_<component>.csv` lists why.

## After a session

```bash
python scripts/ingest.py --src <phone folder> --label correct --board 03 --note "lamp left"
python scripts/align.py
python scripts/align.py --preview     # look at the crops before shooting more
```
