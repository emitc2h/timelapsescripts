import cv2, ROOT, plotting, os, sys, numpy as np
from progressbar import *

input_dirs = sys.argv[1].split(',')

widgets = [Percentage(), ' ', Bar(marker='*'), ' ', ETA()]

def make_corrected_iso(g_iso, g_avg):
    
    ## Prepare stitching variables
    avg_i, avg = ROOT.Double(), ROOT.Double()
    iso_i, iso = ROOT.Double(), ROOT.Double()
    old_iso    = ROOT.Double()
    old_avg    = ROOT.Double()
    iso_correction = 0.0
    g_iso.GetPoint(0, iso_i, old_iso)

    ## Prepare minimums and maximums
    min_avg = 255
    max_avg = 0

    min_new = 255
    max_new = 0

    g_new = ROOT.TGraph()

    ## Stitch the curves at different ISO settings
    for i in range(g_avg.GetN()):
        g_iso.GetPoint(i, iso_i, iso)
        g_avg.GetPoint(i, avg_i, avg)

        ## Find minimum and maximums
        if avg > max_avg: max_avg = float(avg)
        if avg < min_avg: min_avg = float(avg)

        if not iso == old_iso:
            iso_correction += (avg - old_avg)

        avg_new = avg - iso_correction
        if avg_new > max_new: max_new = avg_new
        if avg_new < min_new: min_new = avg_new

        g_new.SetPoint(i, avg_i, avg_new)

        old_iso = float(iso)
        old_avg = float(avg)

    ## Calculate ranges
    range_avg = max_avg - min_avg
    range_new = max_new - min_new

    def linear_mapping(y):
        return (y - min_new)*(range_avg/range_new) + min_avg

    return g_new, linear_mapping

for input_dir in input_dirs:
    
    print 'Processing {0} ...'.format(input_dir)

    ff = ROOT.TFile('iso-{0}.root'.format(input_dir))
    g_blue  = ff.Get('blue')
    g_green = ff.Get('green')
    g_red   = ff.Get('red')
    g_iso = ff.Get('iso')

    for i in range(g_avg.GetN()):
        g_new.GetPoint(i, avg_i, avg)
        g_new.SetPoint(i, avg_i, linear_mapping(avg))
    
    canvas = ROOT.TCanvas()
    
    g_new.SetMarkerColor(ROOT.kRed)
    g_new.SetMarkerStyle(20)
    g_new.SetMarkerSize(0.2)
    g_new.Draw('AP')
    
    g_avg.SetMarkerColor(ROOT.kGreen+2)
    g_avg.SetMarkerStyle(20)
    g_avg.SetMarkerSize(0.2)
    g_avg.Draw('SAMEP')
    
    canvas.Print('{0}-iso-flat.png'.format(input_dir.rstrip('/')))
    
    output_dir = input_dir + '_iso_flat'
    
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
    
        g_new.GetPoint(i, x, y2)
        g_avg.GetPoint(i, x, y1)
    
        correction_factor = 1.0 - (y1 - y2)/y2
    
        img = cv2.imread(os.path.join(input_dir, l[i]))
    
        new_img = cv2.multiply(img, np.array([correction_factor])
    
        cv2.imwrite(os.path.join(output_dir, 'IMG_{0}.jpg'.format(number_original)), new_img)

        pbar.update(i)

    pbar.finish()
