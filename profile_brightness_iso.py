import cv2, ROOT, PIL.Image, os, sys, math, numpy as np
from progressbar import *
import PIL.ExifTags

input_dirs = sys.argv[1].split(',')

widgets = [Percentage(), ' ', Bar(marker='*'), ' ', ETA()]

for input_dir in input_dirs:

    print 'Processing {0} ...'.format(input_dir)

    smooth_file = ROOT.TFile('smooth-iso-{0}.root'.format(input_dir.rstrip('/')), 'RECREATE')
    
    l = os.listdir(input_dir)
    l = [f for f in l if f.lower().endswith('.jpg')]
    
    graph_avg = ROOT.TGraph()
    graph_avg.SetName('avg')

    graph_iso = ROOT.TGraph()
    graph_iso.SetName('iso')
    
    n = len(l)-1
    pbar = ProgressBar(widgets=widgets, maxval=n).start()

    for i in range(n):
    
        ## Gather brightness info
        img  = cv2.imread(os.path.join(input_dir, l[i]))
        blue, green, red = cv2.split(img)

        brightness = math.sqrt(np.average(blue)**2 + np.average(green)**2 + np.average(red)**2)
        graph_avg.SetPoint(i, i, brightness)

        ## Gather ISO info
        img = PIL.Image.open(os.path.join(input_dir, l[i]))
        ISO = int(img._getexif()[34855])
        graph_iso.SetPoint(i, i, ISO)

        pbar.update(i)

    pbar.finish()
    
    graph_avg.Write()
    graph_iso.Write()
    smooth_file.Write()
    smooth_file.Close()
    
    canvas = ROOT.TCanvas()
    graph_avg.SetMarkerColor(ROOT.kGreen+2)
    graph_avg.SetMarkerStyle(20)
    graph_avg.SetMarkerSize(0.2)
    graph_avg.Draw('AP')
    canvas.Print('{0}_avg.png'.format(input_dir.rstrip('/')))

    graph_iso.SetMarkerColor(ROOT.kRed+1)
    graph_iso.SetMarkerStyle(20)
    graph_iso.SetMarkerSize(0.2)
    graph_iso.Draw('AP')
    canvas.Print('{0}_iso.png'.format(input_dir.rstrip('/')))