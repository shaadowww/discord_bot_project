import requests
import sys
from random import choice
from pathlib import Path
from typing import List

current_file = Path(__file__).resolve()

project = current_file.parent.parent

sys.path.append(str(project))

from cfg import CROSSHAIRS

def generate_waifu():
    response = requests.get("https://api.waifu.pics/sfw/waifu")

    if response.status_code == 200:
        data = response.json()
        img = data['url']
        return img
    
def crosshair() -> List[str]:
    random_crosshair, random_code = choice(list(CROSSHAIRS.items()))
    return [random_crosshair, random_code]