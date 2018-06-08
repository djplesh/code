


class Tetra(object):

    def __init__(self, loc, box_list):
        self.loc = fix_loc(loc)
        boxes = []
        if box_list == 'all' or box_list == 0:
            box_list = box_numbers(self.loc)
        for b in box_list:
            boxes.append(fix_num(b))
        self.box = boxes