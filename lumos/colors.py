
colors = {
    "mint_green": "#A7E9AF",
    "sky_blue": "#B3E5FC",
    "misty_pink": "#F8BBD0",
    "cream_yellow": "#FFF9C4",
    "hazy_gray": "#CFD8DC",
    "warm_chestnut": "#A0522D",
    "olive_green": "#808000",
    "deep_burgundy": "#8B0000",
    "golden_tan": "#D2B48C",
    "light_orange": "#FFA07A",
    "ink_blue_gray": "#4B5D67",
    "graphite_gray": "#6D6D6D",
    "ivory_white": "#F5F5F5",
    "frosted_blue": "#9BB7D4",
    "dusty_purple": "#8A708B",
    "sunset_orange": "#FF4500",
    "bright_yellow": "#FFD700",
    "minty_blue": "#40E0D0",
    "cherry_blossom_pink": "#FF69B4",
    "lime_green": "#32CD32"
}


def pick_color(n):
    # random pick a color from the colors dict
    color_list = list(colors.values())
    color_idx = hash(n) % len(color_list)
    return color_list[color_idx]