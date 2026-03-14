# Some tests for discord bot

from utils import generate_waifu, crosshair
from pytest import raises

def test_gen_waifu():
    assert generate_waifu()

def test_crosshair_gen():
    assert isinstance(crosshair(), list)

