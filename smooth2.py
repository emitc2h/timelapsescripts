import ROOT, plotting
from PIL import Image, ImageEnhance
import os, sys

input_dir = sys.argv[1]

ff = ROOT.TFile('{0}-smooth.root'.format(input_dir))
g = ff.Get('avg_blue')
h = plotting.graph_to_histogram(g)
h.Smooth(2)

new_g = ROOT.TGraph(h)

canvas = ROOT.TCanvas()

g.SetMarkerColor(ROOT.kRed)
g.SetMarkerStyle(20)
g.SetMarkerSize(0.2)
g.SetMaximum(220)
g.SetMinimum(120)
g.Draw('AP')

new_g.SetMarkerColor(ROOT.kGreen+2)
new_g.SetMarkerStyle(20)
new_g.SetMarkerSize(0.2)
new_g.Draw('SAMEP')

print g.GetN(), new_g.GetN()

canvas.Print('smooth2.png')

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

for i in range(len(l)-1):

    if not '.jpg' in l[i]: continue

    number_original = '{0}'.format(counter).zfill(4)
    counter += 1

    new_g.GetPoint(i, x, y2)
    g.GetPoint(i, x, y1)

    correction_factor = 1.0 - (y1 - y2)/y2

    print os.path.join(input_dir, l[i])
    img = Image.open(os.path.join(input_dir, l[i]))

    print 'correction factor:', correction_factor

    enhancer = ImageEnhance.Brightness(img)
    new_img = enhancer.enhance(correction_factor)

    new_img.save(os.path.join(output_dir, 'IMG_{0}.jpg'.format(number_original)))
