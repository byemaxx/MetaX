from distinctipy import distinctipy

# number of colours to generate
N = 16
existing_colors = [(0, 0, 0), (1, 1, 1)]
# generate N visually distinct colours
colors = distinctipy.get_colors(N, existing_colors)
# convert rgb to hex
print(colors)
colors = distinctipy.color_swatch(colors)
# display the colours
# distinctipy.color_swatch(colors)