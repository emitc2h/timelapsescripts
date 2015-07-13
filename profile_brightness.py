import cv2, ROOT, os, sys, numpy as np
from progressbar import *

input_dirs = sys.argv[1].split(',')

widgets = [Percentage(), ' ', Bar(marker='*'), ' ', ETA()]

for input_dir in input_dirs:

    print 'Processing {0} ...'.format(input_dir)

    smooth_file = ROOT.TFile('smooth-{0}.root'.format(input_dir.rstrip('/')), 'RECREATE')
    
    l = os.listdir(input_dir)
    
    graph_min_blue = ROOT.TGraph()
    graph_min_blue.SetName('min_blue')
    graph_max_blue = ROOT.TGraph()
    graph_max_blue.SetName('max_blue')
    graph_avg_blue = ROOT.TGraph()
    graph_avg_blue.SetName('avg_blue')
    
    n = len(l)-1
    pbar = ProgressBar(widgets=widgets, maxval=n).start()

    for i in range(n):
    
        if not '.jpg' in l[i]: continue
    
        img  = cv2.imread(os.path.join(input_dir, l[i]))
        blue = cv2.split(img)[0]

        graph_min_blue.SetPoint(i, i, blue.min())
        graph_max_blue.SetPoint(i, i, blue.max())
        graph_avg_blue.SetPoint(i, i, np.average(blue))

        pbar.update(i)

    pbar.finish()
    
    graph_min_blue.Write()
    graph_max_blue.Write()
    graph_avg_blue.Write()
    smooth_file.Write()
    smooth_file.Close()
    
    canvas = ROOT.TCanvas()
    graph_min_blue.SetMarkerColor(ROOT.kBlue)
    graph_min_blue.SetMarkerStyle(20)
    graph_min_blue.SetMarkerSize(0.2)
    graph_min_blue.SetMaximum(255)
    graph_min_blue.Draw('AP')
    graph_max_blue.SetMarkerColor(ROOT.kRed)
    graph_max_blue.SetMarkerStyle(20)
    graph_max_blue.SetMarkerSize(0.2)
    graph_max_blue.Draw('P')
    graph_avg_blue.SetMarkerColor(ROOT.kGreen+2)
    graph_avg_blue.SetMarkerStyle(20)
    graph_avg_blue.SetMarkerSize(0.2)
    graph_avg_blue.Draw('P')
    canvas.Print('{0}.png'.format(input_dir.rstrip('/')))