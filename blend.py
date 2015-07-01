from PIL import Image
import os, sys

input_dir = sys.argv[1]
output_dir = input_dir + '_blend'

try:
    os.mkdir(output_dir)
except OSError:
    pass
l = os.listdir(input_dir)

counter = 1

for i in range(len(l)-1):

    if not '.jpg' in l[i]: continue

    number_original = '{0}'.format(counter).zfill(4)
    counter += 1
    number_blend    = '{0}'.format(counter).zfill(4)
    counter += 1

    print os.path.join(input_dir, l[i])
    img1 = Image.open(os.path.join(input_dir, l[i]))
    print os.path.join(input_dir, l[i+1])
    img2 = Image.open(os.path.join(input_dir, l[i+1]))

    img1.save(os.path.join(output_dir, 'IMG_{0}.jpg'.format(number_original)))
    img3 = Image.blend(img1, img2, 0.5)
    img3.save(os.path.join(output_dir, 'IMG_{0}.jpg'.format(number_blend)))


# image = '1.png'
# watermark = '2.png'

# wmark = Image.open(watermark)
# img = Image.open(image)

# img.paste(wmark, (0, 0), wmark)
# img.save("result.png", "PNG")