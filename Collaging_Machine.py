from PIL import Image
import time
import os

path = "coll"


def main(path, repeats):
    if not os.path.exists(path):
        os.mkdir(path)
        dummy = input("Hit enter when you've added the photos to folder 'coll' ")
    path = path + "/"
    pics, min_side, params, area, equivalent, ignored = list_pics(path, set())
    if len(pics) == 0:
        return print("Add .jpg files to 'coll' and try again")
    mothers = len(pics)
    pix = 0
    if len(pics) == 1:
        pix = cut_up(pics)
        pics, min_side, params, area, equivalent, ignored = list_pics(path, ignored)
        pics = pix
    elif len(pics) < 4:
        choice = input(
            "Enter 'c' for 'cut up photo' - or anything else to collage these images "
        )
        if choice.lower() == "c":
            pix = cut_up(pics)
            pics, min_side, params, area, equivalent, ignored = list_pics(path, ignored)
            pics = pix
    background = True
    grid = grid_size(pics)
    seed = 1
    while repeats > 0:
        seed += 1
        if equivalent:
            collage(
                pics, min_side, params, area, mothers, equivalent, grid, seed, background
            )
        else:
            zzz(path, repeats)
            quit()
        repeats -= 1
    if pix != 0:
        remove_later = set()
        for pic in pix:
            remove_later.add(pic[0])
        delete_jpeg_files(path, remove_later, path)


def add_coordinates_antistreak(
    pics, pic_width, pic_height, border, seed, mothers, basis, grid, indices
):
    for i in range(len(pics)):
        if i % grid[1] == 0:
            seed += 1
        ii = i + seed
        pic = indices[ii % mothers][ii**2 % len(indices[ii % mothers])]
        indices[ii % mothers].remove(pic)
        pics[pic][3] = (i % grid[1]) * (pic_width + border)
        pics[pic][4] = (i // grid[1]) * (pic_height + border)
    return (
        pic_width * grid[1] + (grid[1] - 1) * border,
        pic_height * grid[2] + (grid[2] - 1) * border,
    )


def add_top_and_side_borders(pics, params, dimensions):
    top = int(params[1] * dimensions[1])
    side = int(params[2] * dimensions[0])
    if top == 0 and side == 0:
        return 0, 0
    for pic in range(len(pics)):
        pics[pic][3] += side
        pics[pic][4] += top
    return side, top


def average_colour(pic, x_separation, y_separation):
    img = Image.open(pic)
    x, y = img.size
    points = (x // x_separation + 1) * (y // y_separation + 1)
    total = [0, 0, 0]
    for i in range(1, x, x_separation):
        for j in range(1, y, y_separation):
            rgb = img.getpixel((i, j))
            total[0] += rgb[0]
            total[1] += rgb[1]
            total[2] += rgb[2]
    for i in range(3):
        total[i] = total[i] // points
    return total[0], total[1], total[2]


def collage(pics, min_side, params, area, mothers, equivalent, grid, seed, background):
    if equivalent:
        return collage_equivalent(
            pics, min_side, params, area, mothers, grid, seed, background
        )
    else:
        print("NOT AVAILABLE ATM - Try the Collaging Machine, which may be nearby")


def collage_equivalent(pics, min_side, params, area, mothers, grid, seed, background):
    len_pics = len(pics)
    if mothers == len_pics:
        basis = len_pics
        mothers = 1
    else:
        basis = len_pics // mothers
    indices = []
    for ii in range(mothers):
        similar = []
        block = ii * basis
        for jj in range(basis):
            similar.append(block + jj)
        indices.append(similar)
    total = 0
    if grid[1] % mothers == 0:
        dimensions = add_coordinates_antistreak(
            pics, pics[0][1], pics[0][2], params[0], seed, mothers, basis, grid, indices
        )
    side, top = add_top_and_side_borders(pics, params, dimensions)
    print_collage(pics, background, dimensions, side, top)


def colour(pics, background, x_separation, y_separation):
    f = 2
    rgb = [0, 0, 0]
    for pic in pics:
        r, g, b = average_colour(pic[0], x_separation, y_separation)
        rgb[0] += r
        rgb[1] += g
        rgb[2] += b
    grey = (rgb[0] + rgb[1] + rgb[2]) / len(pics)
    if grey > 483 and background:
        rgb_final = (0, 0, 0)
    elif grey < 482 and background:
        rgb_final = (255, 255, 255)
    else:
        rgb_final = (
            rgb[1] // (len(pics) * f),
            rgb[2] // (len(pics) * f),
            rgb[0] // (len(pics) * f),
        )
    return rgb_final


def cut_save(pic, pix, xx, yy, x, y, dim):
    counter = 0
    if dim == 0:
        width = int(x / xx)
        height = int(y / yy)
        xx, yy = width, height
    else:
        width = dim[0]
        height = dim[1]
        if int(x / xx) == width and int(y / yy) == height:
            xx, yy = width, height
        else:
            xx = int((x - width) / (xx - 1))
            yy = int((y - height) / (yy - 1))
    img = Image.open(pic[0])
    for i in range(0, x - width + 1, xx):
        for j in range(0, y - height + 1, yy):
            counter += 1
            cropped_region = img.crop((i, j, i + width, j + height))
            cropped_region.save(pic[0] + str(counter) + ".jpg", quality=100)
            pix.append([pic[0] + str(counter) + ".jpg", width, height, 0, 0])
    return (width, height)


def cut_up(pics):
    pix = []
    x = pics[0][1]
    y = pics[0][2]
    if x / y > 2:
        xx = 6
        yy = 2
    elif x / y > 1:
        xx = 4
        yy = 3
    elif x / y > 0.5:
        xx = 3
        yy = 4
    else:
        xx = 2
        yy = 6
    dim = cut_save(pics[0], pix, xx, yy, x, y, 0)
    if len(pics) > 1:
        for pic in range(1, len(pics)):
            x, y = Image.open(pics[pic][0]).size
            if x / y > 2:
                cut_save(pics[pic], pix, 6, 2, x, y, dim)
            elif x / y > 1:
                cut_save(pics[pic], pix, 4, 3, x, y, dim)
            elif x / y > 0.5:
                cut_save(pics[pic], pix, 3, 4, x, y, dim)
            else:
                cut_save(pics[pic], pix, 2, 6, x, y, dim)
    return pix


def delete_jpeg_files(directory, remove_later, path):
    files = 0
    for file in os.listdir(directory):
        filepath = os.path.join(path, file)
        if filepath in remove_later:
            os.remove(filepath)
            files += 1
    print(files, " files deleted")


def grid_size(pics):
    len_pics = len(pics)
    pic_width = pics[0][1]
    pic_height = pics[0][2]
    compact = [10, 0, 0]
    for i in range(1, int(len_pics**0.5) + 2):
        if len_pics % i == 0:
            elongatness = is_elongate(pic_width, pic_height, i, len_pics // i)
            if elongatness < compact[0]:
                compact = [elongatness, i, len_pics // i]
            elongatness = is_elongate(pic_width, pic_height, len_pics // i, i)
            if elongatness < compact[0]:
                compact = [elongatness, len_pics // i, i]
    if compact[1] == 0:
        return 0
    return compact


def interpret_pic(pic, x_separation, y_separation):
    img = Image.open(pic)
    x, y = img.size
    total = [0, 0, 0]
    for i in range(1, x, x_separation):
        for j in range(1, y, y_separation):
            rgb = img.getpixel((i, j))
            total[0] += rgb[0]
            total[1] += rgb[1]
            total[2] += rgb[2]
    points = (x // x_separation + 1) * (y // y_separation + 1)
    for i in range(3):
        total[i] = int(total[i] / points)
    return total[0], total[1], total[2]


def is_elongate(pic_width, pic_height, x_wide, y_high):
    elongatness = pic_width * x_wide / (pic_height * y_high) + (
        pic_height * y_high / (pic_width * x_wide)
    )
    if elongatness < 3:
        return elongatness
    return 10


def list_pics(path, ignored):
    pics = []
    area = 0
    dimensions = (0, 0)
    equivalent = 0
    for name in os.listdir(path):
        if name in ignored:
            continue
        else:
            ignored.add(name)
        if not (name[-3] == "j" and name[-2] == "p" and name[-1] == "g"):
            continue
        x, y = Image.open(path + name).size
        if dimensions[0] == x and dimensions[1] == y:
            equivalent += 1
        else:
            dimensions = (x, y)
        area += x * y
        pics.append([path + name, x, y, 0, 0])
    if equivalent == len(pics) - 1:
        equivalent = True
    else:
        equivalent = False
    min_side = int(area**0.5) + 1
    pics.sort()
    return pics, min_side, [100, 0.05, 0.05], area, equivalent, ignored


def print_collage(pics, background, dimensions, side, top):
    f = 3
    if background != 0:
        rgb = colour(pics, background, 10, 10)
    else:
        rgb = [0, 0, 0]
    collage = Image.new("RGB", (dimensions[0] + 2 * side, dimensions[1] + 2 * top), rgb)
    for pic in pics:
        collage.paste(Image.open(pic[0]), (pic[3], pic[4]))
    collage.show()
    collage.save("coll" + str(int(time.time())) + ".jpg", quality=100)


def zzz(path, repeats):

    import copy
    
    def main(path, repeats):
        faff = input("Welcome to Collaging Machine. Make sure you have added the pics to the folder 'coll' and hope for the best. The first time you answer this, it's probably best to just hit enter \nDo you want to faff? ")
        pix, min_side, params, area, equivalent = getpix(path)
        background = True
        if equivalent:
            print("Mkay - you're using equal sized pics, so let's see about that...")
            equivalent = equivalent_suite(pix, min_side, params, area, repeats, background)
            if equivalent:
                return
            if len(pix) > 2:
                answer = input("would you prefer to remove a pic and try again? ")
                if answer.lower() in {"yes", "y"}:
                    main(repeats)
                    return
            
        if (
            faff in {"Y", "y"}
            or len(faff) < 5
            and len(faff) > 1
            and faff[0] in {"y", "Y"}
            and faff[1] in {"e", "E"}
        ):
            return advanced_suite(repeats, background, path)
        if (
            faff in {"", "n", "N"}
            or len(faff) < 4
            and faff[0].lower() == "n"
        ):
            pix = getpix(path)[0]
            return printmostcompact(len(pix)**2, [0.5, 1, 1, 0], background)

        return semi_advanced_suite(repeats, background, path)

    def printmostcompact(x, params, background):
        min_bad = [[], 10**50]
        bigrandomnumber = 997
        for i in range(x):
            pix, min_side, paramsthrowaway, area, equivalent = getpix("coll/")
            params[-1] = i + bigrandomnumber
            border = int(((area / len(pix))**0.5) * params[0] / 4)
            min_side_corrected = min_side + (len(pix)**0.5 - 1) * border
            print_complete = layout(copy.deepcopy(pix), min_side_corrected, params, area, equivalent)
            total_area = print_complete[1][0] * print_complete[1][1]
            if print_complete[2] * total_area < min_bad[-1]:
                print_complete[2] *= total_area
                min_bad = print_complete
        coll(min_bad, background)


    def coll(print_complete, background):
        f = 3
        if len(print_complete[0]) == 0:
            print("add pics to /coll/")
            return
        rgb = [0, 0, 0]
        for pic in print_complete[0]:
            r, g, b = colour(pic[0])
            rgb[0] += r
            rgb[1] += g
            rgb[2] += b
        if (rgb[0] + rgb[1] + rgb[2]) / len(print_complete[0]) > 383 and background:
            rgb_final = (0, 0, 0)
        elif (rgb[0] + rgb[1] + rgb[2]) / len(print_complete[0]) < 382 and background:
            rgb_final = (255, 255, 255) 
        else:
            rgb_final = (int(rgb[1] / (len(print_complete[0]) * f)), int(rgb[2] / (len(print_complete[0]) * f)), int(rgb[0] / (len(print_complete[0]) * f)))
        collage = Image.new("RGB", print_complete[1], rgb_final)
        for name in print_complete[0]:
            collage.paste(Image.open(name[0]), (name[3], name[4]))
        collage.show()
        collage.save("coll"+str(int(time.time()))+".jpg",quality=99) 

    def colour(pic):
        img = Image.open(pic)
        x, y = img.size
        points = 0
        total = [0, 0, 0]
        for i in range(1, x, 10):
            for j in range(1, y, 10):
                points += 1
                rgb = img.getpixel((i, j))
                total[0] += rgb[0]
                total[1] += rgb[1]
                total[2] += rgb[2]
        for i in range(3):
            total[i] = int(total[i] / points)
        return total[0], total[1], total[2]

    def isfloat(x):
        try:
            float(x)
            return True
        except ValueError:
            return False
        
    def advanced_suite(repeats, background, path):
        not_equivalent = True

        pix, min_side, params, area, equivalent = getpix(path)
        displayed = (
            "do you want to reshuffle? Type 'rs' ",
            "how much border do you like? try using lower numbers ",
            "How much top border do you like? ",
            "How much side border do you like? ",
        )
        print("this probably won't produce the best results (try trying something different next time)")
        params = [0, 0, 0, 0]
        bigrandomnumber = 997
        for rep in range(repeats):
            for i in range(len(displayed)):
                text = input(displayed[i])
                if i == 0:
                    if rep != 0:
                        if text.lower() == "rs":
                            params[-1] += bigrandomnumber
                            print_complete = layout(copy.deepcopy(pix), min_side, params, area, not_equivalent)
                            coll(print_complete)
                            break
                    continue
                while not isfloat(text) or float(text) < -5 or float(text) > 30:
                    print("enter a number between -5 and 30")
                    text = input(displayed[i])
                params[i - 1] = float(text)
            if text.lower() == "rs":
                continue
            params[-1] = 0
            border = int(((area / len(pix))**0.5) * params[0] / 4)
            min_side_corrected = min_side + (len(pix)**0.5 - 1) * border
            print_complete = layout(copy.deepcopy(pix), min_side_corrected, params, area, not_equivalent)
            coll(print_complete, background)
            
    def semi_advanced_suite(repeats, background, path):

        pix, min_side, params, area, not_equivalent = getpix(path)
        displayed = (
            "how much border do you like? - type as many 'b's as you fancy (don't go overboard!)",
            "How much top border do you like? - type as many 'b's as you fancy ",
            "How much side border do you like? - type as many 'b's as you fancy ",
        )
        params = [0, 0, 0, 0]
        for rep in range(repeats):
            for i in range(len(displayed)):
                text = input(displayed[i])
                b=0
                for char in text:
                    if char in {"b", "B"}:
                        b += 1
                
                if b > 0:
                    params[i] = 0.2 * 1.5**b
                else:
                    params[i] = 0
            printmostcompact(len(pix)**2, params, background)
            
    def getpix(path):

        pix = []
        area = 0
        dimensions = (0, 0)
        equivalent = 0
        
        for i in os.listdir(path):
            if i in {".DS_Store"}:
                continue
            img = Image.open(path + i)
            x, y = img.size
            if dimensions[0] == x and dimensions[1] == y:
                equivalent += 1
            else:
                dimensions = (x, y)
            area += x * y
            pix.append([path + i, x, y, 0, 0])
        pix.sort()
        if equivalent == len(pix) - 1:
            equivalent = True
        else:
            equivalent = False
        for i in range(len(pix)):
            pix[i].append(i)
        min_side = int(area**0.5) + 1
        return pix, min_side, [1, 1, 1, 0], area, equivalent


    def layout(pix, min_side, params, area, not_equivalent):
        widest = [0, 0, 0, 0, 0]
        tallest = [0, 0, 0, 0, 0]
        sprawlingest = [0]
        for pic in pix:
            if pic[1] > widest[1]:
                widest = pic
            if pic[2] > tallest[2]:
                tallest = pic
            pic_area = pic[1] * pic[2]
            if pic_area > sprawlingest[0]:
                sprawlingest = [pic_area, pic]
        wide = []
        tall = []
        min_max_side = min_side
        for pic in pix:
            if pic[1] >= min_side:
                min_max_side = pic[1]
                wide.append(pic)
                continue
            if pic[2] >= min_side:
                min_side = pic[2]
                tall.append(pic)
        if min_max_side > min_side:
            min_side = min_max_side
        if not_equivalent:
            min_side = int(min_side * 1.1)
        
        if len(wide) + len(tall) == 0 and len(pix) < 4:
            pass
        orientation = 0
        if tallest[2] > widest[1] and len(tall) > 0:
            orientation = 1
        widest_tallest = [widest, tallest]
        print_complete = draw(
            pix, orientation, sprawlingest[1], widest_tallest, params, min_side, area, not_equivalent
        )
        return print_complete


    def draw(pix, orientation, sprawlingest, widest_tallest, params, min_side, area, not_equivalent):
        # determine which pic to add next
        def nextpic(pix, print_folder, min_side, border, orientation, aspect):
            
            def returnbestmatch(print_folder, candidates, space):
                best = candidates[0]
                for pic in candidates:
                    if (pic[aspect + 1] - print_folder[-1][aspect + 1])**2 < (best[aspect + 1] - print_folder[-1][aspect + 1])**2:
                        best = pic
                return best
            
            candidates = []
            for pic in pix:
                if (
                    pic[1 + orientation]
                    + print_folder[-1][1 + orientation]
                    + print_folder[-1][3 + orientation]
                    + border
                    <= min_side
                ):
                    candidates.append(pic)
            if len(candidates) == 0:
                return pix[0]
            return returnbestmatch(print_folder.copy(), candidates, min_side - print_folder[-1][1 + orientation] - print_folder[-1][3 + orientation])

        # add x,y coordinates to the most recently added pic
        def addcoordinates(print_folder, min_side, border, orientation, aspect):
            if (
                print_folder[-1][orientation + 1]
                + print_folder[-2][orientation + 1]
                + print_folder[-2][orientation + 3]
                + border
                <= min_side
            ):
                print_folder[-1][orientation + 3] = (
                    print_folder[-2][orientation + 1]
                    + print_folder[-2][orientation + 3]
                    + border
                )
                print_folder[-1][aspect + 3] = print_folder[-2][aspect + 3]
            else:
                # find the most awkward pic added to print_folder recently, and copy its awkward height/width as 'mostawkward'
                mostawkward = 0
                for i in range(1, len(print_folder)):
                    if print_folder[-1 - i][aspect + 1] > mostawkward:
                        mostawkward = print_folder[-1 - i][aspect + 1]
                    if print_folder[-1 - i][orientation + 3] != 0:
                        continue
                    # populate the coordinates with the correct layout data
                    print_folder[-1][orientation + 3] = 0
                    print_folder[-1][aspect + 3] = (
                        mostawkward + print_folder[-1 - i][aspect + 3] + border
                    )
                    break

        print_folder = []
        border = int(((area / len(pix))**0.5) * params[0] / 4)
        if not_equivalent:
            min_side += border * len(print_folder)**0.5
        top = int(((area / len(pix))**0.5) * params[1] / 4)
        side = int(((area / len(pix))**0.5) * params[2] / 4)
        aspect = 1
        if orientation == 1:
            aspect = 0
        ## add 'random' pics to print_folder
        rand = params[-1]
        while rand > 0 and len(pix) > 0:
            print_folder.append(pix[params[-1] % len(pix)])
            pix.remove(pix[params[-1] % len(pix)])
            if len(print_folder) > 1:
                addcoordinates(print_folder, min_side, border, orientation, aspect)
            rand -= 1

        if len(print_folder) == 0:
            print_folder.append(widest_tallest[orientation])
            pix.remove(widest_tallest[orientation])

        while len(pix) > 0:
            next_pic = nextpic(pix, print_folder, min_side, border, orientation, aspect)
            pix.remove(next_pic)
            print_folder.append(next_pic)
            addcoordinates(print_folder, min_side, border, orientation, aspect)

        # get size of the grid
        x = 0
        y = 0
        for pic in print_folder:
            if pic[1] + pic[3] > x:
                x = pic[1] + pic[3]
            if pic[2] + pic[4] > y:
                y = pic[2] + pic[4]

        unbalancedness = centreofmass(print_folder, x, y)

        # increase all coordinates in light of top/bottom and side borders
        for pic in print_folder:
            pic[3] += side
            pic[4] += top

        return [print_folder, (x + 2 * side, y + 2 * top), unbalancedness]

    def centreofmass(print_folder, x, y):
        offset_x = 0
        offset_y = 0
        total_area = 0
        for pic in print_folder:
            area = pic[1] * pic[2]
            offset_x += (pic[3] + pic[1] / 2) * area
            offset_y += (pic[4] + pic[2] / 2) * area
            total_area += area
        ideal_x = x * total_area / 2
        ideal_y = y * total_area / 2
        offcentre_x = ideal_x - offset_x
        offcentre_y = ideal_y - offset_y
        
        unbalancedness = (offcentre_x**2 + offcentre_y**2)**0.5 / total_area 
        return unbalancedness + total_area**0.5

    def equivalent_suite(pix, min_side, params, area, repeats, background):
        not_equivalent = False
        n = len(pix)
        candidates = []
        
        for i in range(1, n + 1):
            if n % i == 0 and pix[0][1] * n / i < 2 * min_side and pix[0][1] * n / i > 0.5 * min_side:
                candidates.append((int((n / i) + 0.1), pix[0][1] * n / (i**2 * pix[0][2])))
        if len(candidates) == 0:
            return False
        
        candidate = (0, 11)
        for grouping in candidates:
            if grouping[1] + 1 / grouping[1] < candidate[1]:
                candidate = (grouping[0], grouping[1] + 1 / grouping[1])
        

        displayed = (
            "do you want to reshuffle? Type 'rs' ",
            "how much border do you like? try using lower numbers ",
            "How much top border do you like? ",
            "How much side border do you like? ",
        )
        params = [0, 0, 0, 0]
        for rep in range(repeats):
            for i in range(len(displayed)):
                text = input(displayed[i])
                if i == 0:
                    if rep != 0:
                        if text.lower() == "rs":
                            params[-1] += 997
                            border = int(((area / len(pix))**0.5) * params[0] / 4)
                            min_side = candidate[0] * pix[0][1] + (candidate[0] - 1) * border
                            print_complete = layout(copy.deepcopy(pix), min_side, params, area, not_equivalent)
                            coll(print_complete, background)
                            break
                    continue
                while not isfloat(text) or float(text) < -5 or float(text) > 30:
                    print("enter a number between -5 and 30")
                    text = input(displayed[i])
                params[i - 1] = float(text) / 4
            if text.lower() == "rs":
                continue
            params[-1] = 0
            border = int(((area / len(pix))**0.5) * params[0] / 4)
            min_side = candidate[0] * pix[0][1] + (candidate[0] - 1) * border
            print_complete = layout(copy.deepcopy(pix), min_side, params, area, not_equivalent)
            coll(print_complete, background)
        return True

    main(path, repeats)

if __name__ == "__main__":
    main(path, 3)
