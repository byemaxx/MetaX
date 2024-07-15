# this script is used to generate distinct colors for plotting

from distinctipy import distinctipy

import matplotlib.pyplot as plt
import colorsys


class GetDistinctColors:
    def __init__(self):
        pass
    
    def assign_colors(self, groups_list: list) -> list:
        '''
        Assign colors of the number of unique groups in the list
        - return a list of colors in hex format
        '''
        colors = self.get_distinct_colors(len(set(groups_list)))
        result = []
        for group in groups_list:
            index = sorted(set(groups_list)).index(group)
            result.append(colors[index])
        return result
    
    def adjust_color(self, color, sat_factor=0.7, light_factor=1.2):
        """
        Adjusts the given color's saturation and lightness. each factor should be between 0 and 2.
        Args:
            sat_factor: Factor to adjust saturation
            light_factor: Factor to adjust lightness
        Returns:
            Adjusted color as a tuple of RGB values.
        """
        c = colorsys.rgb_to_hls(*color)
        return colorsys.hls_to_rgb(c[0], max(0, c[1] * light_factor), max(0, c[2] * sat_factor))

    
    def get_distinct_colors(self, num: int, convert:bool= False) -> list:
        '''
        Get distinct colors for plotting
        - `parameters:`
            - num: number of colors to generate
            - convert: bool, if True, convert the colors to rgb values
        - `return`:
            a list of colors in hex format or rgb format
        '''
        if num <= 10:
            # use deep from seaborn
            # distinct_colors = sns.color_palette('tab10', num)
            # use tab10 colors from matplotlib
            distinct_colors = plt.cm.tab10.colors
            colors = [self.adjust_color(i, 0.75, 1.1) for i in distinct_colors]
            
        elif num <= 20:
            # use tab20 colors from matplotlib
            distinct_colors = plt.cm.tab20.colors
            colors = [self.adjust_color(i, 0.8, 0.95) for i in distinct_colors]
            
            
        else:
            # rgb colour values (floats between 0 and 1)
            RED = (1, 0, 0)
            GREEN = (0, 1, 0)
            # BLUE = (0, 0, 1)
            BLACK = (0, 0, 0)
            WHITE = (1, 1, 1)

            # generated colours will be as distinct as possible from these colours
            input_colors = [WHITE, GREEN, RED, BLACK]
            colors = distinctipy.get_colors(num, exclude_colors= input_colors, pastel_factor=0.7, rng=123)
            # colors = distinctipy.get_colors(num, exclude_colors= input_colors, rng=123)
            colors = [self.adjust_color(i, 0.7, 0.9) for i in colors]

        if convert: # convert to rgb values
            converted_colors = []
            converted_colors.extend(
                f'rgb({i[0] * 255},{i[1] * 255},{i[2] * 255})' for i in colors
            )
            colors = converted_colors
            
        return colors
    
    
if __name__ == '__main__':
    # test the GetDistinctColors class
    gdc = GetDistinctColors()
    color_1 = gdc.get_distinct_colors(10)
    color_2 = gdc.get_distinct_colors(20)
    color_3 = gdc.get_distinct_colors(30)
    
    # plot the colors
    fig, ax = plt.subplots(1, 3, figsize=(20, 5))
    for i, color in enumerate([color_1, color_2, color_3]):
        for j, c in enumerate(color):
            ax[i].bar(j, 1, color=c)
        ax[i].set_title(f'Color Set {i+1}')
        ax[i].axis('off')
    plt.show()