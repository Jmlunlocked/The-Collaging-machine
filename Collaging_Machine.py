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
        collage(
            pics, min_side, params, area, mothers, equivalent, grid, seed, background
        )
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


if __name__ == "__main__":
    main(path, 3)
