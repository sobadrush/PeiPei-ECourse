# -*- coding: utf-8 -*-

import re

if __name__ == '__main__':
    # gotoCourse(10001401);
    # gotoCourse(10001400);
    print('Call it locally')
    print(re.search("\(([^)]+)\)", "gotoCourse(10001400)").group(1))
    print(re.search("\(([^()]*)\)", "gotoCourse(10001400)").string)