import cv2, ROOT, os, sys, numpy as np
from progressbar import *

input_dirs = sys.argv[1].split(',')

widgets = [Percentage(), ' ', Bar(marker='*'), ' ', ETA()]

fourcc = cv2.VideoWriter_fourcc(*'raw ')

for input_dir in input_dirs:

    print 'Processing {0} ...'.format(input_dir)

    l = os.listdir(input_dir)
    l = [f for f in l if f.lower().endswith('.jpg')]

    img  = cv2.imread(os.path.join(input_dir, l[0]))
    height, width, channels = img.shape
    aspect_ratio = float(width-422)/float(height-574)
    video_size   = (int(1080*aspect_ratio), 1080)
    size_ratio   = int((height-574)/1080.0)
    if size_ratio%2==0:
        size_ratio += 1

    out = cv2.VideoWriter('{0}.raw'.format(input_dir.rstrip('/')), fourcc, 24.0, video_size, isColor=True)

    n = len(l)-1
    pbar = ProgressBar(widgets=widgets, maxval=n).start()

    for i in range(n):
    
        img = cv2.imread(os.path.join(input_dir, l[i]))
        img = img[574:height, 422:width]
        img = cv2.GaussianBlur(img, (size_ratio, size_ratio), 0)
        img = cv2.resize(img, video_size)
        out.write(img)

        pbar.update(i)

    pbar.finish()
    out.release()

    os.rename('{0}.raw'.format(input_dir.rstrip('/')), '{0}.mov'.format(input_dir.rstrip('/')))