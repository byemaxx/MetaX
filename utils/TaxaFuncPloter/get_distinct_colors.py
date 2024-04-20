# this script is used to generate distinct colors for plotting

from distinctipy import distinctipy

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
    
    def get_distinct_colors(self, num: int, convert:bool= False) -> list:
        '''
        Get distinct colors for plotting
        - `parameters:`
            - num: number of colors to generate
            - convert: bool, if True, convert the colors to rgb values
        - `return`:
            a list of colors in hex format or rgb format
        '''
        # rgb colour values (floats between 0 and 1)
        # RED = (1, 0, 0)
        # GREEN = (0, 1, 0)
        # BLUE = (0, 0, 1)
        # BLACK = (0, 0, 0)
        WHITE = (1, 1, 1)

        # generated colours will be as distinct as possible from these colours
        input_colors = [WHITE]
        colors = distinctipy.get_colors(num, exclude_colors= input_colors, pastel_factor=0.65, rng=123)
        if convert: # convert to rgb values
            converted_colors = []
            converted_colors.extend(
                f'rgb({i[0] * 255},{i[1] * 255},{i[2] * 255})' for i in colors
            )
            colors = converted_colors
        return colors
    