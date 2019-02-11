from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import sRGBColor, LabColor
import discord
import config
from discord.ext import commands
import numpy as np
import skimage.io 
import skimage.transform
import os

# import emoji
# import requests
# import re
# import base64

TOKEN = config.TOKEN # Get token form config file
bot_prefix = ('!') # Prefix to use
bot = commands.Bot(command_prefix=bot_prefix)

message_limit = 2000 # Limit for discord's messages
output_size = 30 # Will be a square, so used for both X and Y
emote_directory = './images_36x36'

# Dictionary of colors to use
colors = {
    (221, 46, 68)   : ':red_circle:',
    (120, 177, 87)  : ':green_heart:',
    (255, 172, 51)  : ':large_orange_diamond:',
    (85, 172, 238)  : ':large_blue_circle:',
    (253, 203, 88)  : ':yellow_heart:',
    (170, 142, 214) : ':purple_heart:',
    (230, 231, 232) : ':white_circle:',
    (41, 47, 51)    : ':black_circle:',
    (91, 104, 118)  : ':new_moon:',
    (204, 214, 21)  : ':full_moon:',
    (244, 144, 12)  : ':tangerine:',
    (154, 78, 28)   : ':briefcase:',
    (116, 78, 170)  : ':eggplant:',
}
col_keys, col_vals = zip(*list(colors.items()))
col_keys = np.array(col_keys).astype(np.float) / 255

def closest_emoji(pixel_value):
    # Absolutely not optimized. Hard on the CPU.
    diffs = []
    for color in col_keys:
        col1 = sRGBColor(*color)
        col2 = sRGBColor(*pixel_value)
        color1_lab = convert_color(col1, LabColor)
        color2_lab = convert_color(col2, LabColor)
        delta_e = delta_e_cie2000(color1_lab, color2_lab)
        diffs.append(delta_e)
        
    return col_vals[np.argmin(diffs)]

def get_image(emote):
    full_path = os.path.realpath(emote_directory)
    image_path = full_path + '/' + emote + '.png'
    return image_path

def convert_image(path_to_image):
    image = skimage.io.imread(path_to_image)
    size = np.array(image.shape[:2]).astype(np.float)
    size *= output_size / size[1]
    size = np.round(size).astype(np.int)
    image = skimage.transform.resize(image, size)

    # Iterate over the image rows and yield lines of emojis
    block = ''  # A block is multiple lines of emojis
    first_line = True
    for i in range(image.shape[0]):
        # Create one line of emojis
        line = [closest_emoji(image[i][j][:3]) for j in range(image.shape[1])]
        line_length = sum(len(emoji) for emoji in line)
        
        # Add the line to the block. If the block is too long (2000 characters), yield it and 
        # start a new one
        if len(block) + line_length > message_limit:
            yield block
            block = ''
            # Prune the two first characters of the first line to make up for the bot's name space
            first_line = True
        block += ''.join(line[2:] if first_line else line) + '\n'
        first_line = False
        
    # We'll always be left with one final block. 
    yield block

@bot.event
async def on_ready():
    print("Connected")
    print("---------")


@bot.command(name='convert')
async def draw_image(context, arg):
    output_size = int(arg) if len(arg) > 1 else 30  # Default to max width
    # print(emoji.url)
    emote = f'{ord(arg):X}' # Get what emote was said
    print(emote)
    path = get_image(emote) # Path to selected emoji
    print(path)

    # Rename to '----' so more icons can be displayed
    # previous_bot_name = bot.user.display_name
    # self_member = discord.utils.get(message.server.members, id=bot.user.id)
    # await bot.user.edit(username='----')
    # print('name changed')
    try:
        for block in convert_image(path):
            await context.send(block)
    except:
        raise
    # finally:
    #     await bot.user.edit(username=previous_bot_name)
        
    msg = 'Function being implemeted!'
    await context.send(msg + '\n' + arg)


bot.run(TOKEN)