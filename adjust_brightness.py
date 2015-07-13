import cv2, ROOT, plotting, os, sys, numpy as np
from progressbar import *

input_dirs = sys.argv[1].split(',')

widgets = [Percentage(), ' ', Bar(marker='*'), ' ', ETA()]

for input_dir in input_dirs:
    
    print 'Processing {0} ...'.format(input_dir)

    ff = ROOT.TFile('smooth-{0}.root'.format(input_dir))
    g = ff.Get('avg_blue')
    h = plotting.graph_to_histogram(g)
    h.Smooth(10)
    
    new_g = ROOT.TGraph(h)
    
    canvas = ROOT.TCanvas()
    
    g.SetMarkerColor(ROOT.kRed)
    g.SetMarkerStyle(20)
    g.SetMarkerSize(0.2)
    #g.SetMaximum(220)
    #g.SetMinimum(120)
    g.Draw('AP')
    
    new_g.SetMarkerColor(ROOT.kGreen+2)
    new_g.SetMarkerStyle(20)
    new_g.SetMarkerSize(0.2)
    new_g.Draw('SAMEP')
    
    canvas.Print('{0}-smoothing.png'.format(input_dir.rstrip('/')))
    
    output_dir = input_dir + '_smooth'
    
    try:
        os.mkdir(output_dir)
    except OSError:
        pass
    
    l = os.listdir(input_dir)
    
    counter = 1
    
    x = ROOT.Double()
    y1 = ROOT.Double()
    y2 = ROOT.Double()

    n = len(l)-1
    pbar = ProgressBar(widgets=widgets, maxval=n).start()
    
    for i in range(n):
    
        if not '.jpg' in l[i]: continue
    
        number_original = '{0}'.format(counter).zfill(4)
        counter += 1
    
        new_g.GetPoint(i, x, y2)
        g.GetPoint(i, x, y1)
    
        correction_factor = 1.0 - (y1 - y2)/y2
    
        img = cv2.imread(os.path.join(input_dir, l[i]))
    
        new_img = np.multiply(correction_factor, img)
    
        cv2.imwrite(os.path.join(output_dir, 'IMG_{0}.jpg'.format(number_original)), new_img)

        pbar.update(i)

    pbar.finish()
