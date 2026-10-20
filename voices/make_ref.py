#!/usr/bin/env python3
"""Regenerate voices/ref_af_heart.wav, the reference clip Chatterbox clones.
It is ~25 s of Kokoro-82M's af_heart voice (Apache-2.0) reading samples/opening.txt.
usage (from repo root): .venv-kokoro/bin/python voices/make_ref.py"""
import numpy as np, soundfile as sf
from kokoro import KPipeline
text = open("samples/opening.txt").read()
p = KPipeline(lang_code="a")
audio = np.concatenate([x.audio.numpy() for x in p(text, voice="af_heart")])
sf.write("voices/ref_af_heart.wav", audio, 24000)
print(f"wrote voices/ref_af_heart.wav ({len(audio)/24000:.1f} s)")
