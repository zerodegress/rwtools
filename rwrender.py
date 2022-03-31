import os
import sys
from PIL import Image
from typing import List,Tuple,NoReturn

from rwpy.code import Ini,Section,Attribute

def draw_item(img:Image,item:Image,center_pos:Tuple[int,int],expand:bool) -> bool:
    if not expand:
        img.paste(item,(center_pos[0] - item._Size[0],center_pos[1] - item._Size[1]))

if __name__ == '__main__':
    pass