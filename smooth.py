from PIL import Image
import ROOT
import os, sys

input_dir = sys.argv[1]

smooth_file = ROOT.TFile('smooth.root', 'RECREATE')

l = os.listdir(input_dir)

graph_min_blue = ROOT.TGraph()
graph_min_blue.SetName('min_blue')
graph_max_blue = ROOT.TGraph()
graph_max_blue.SetName('max_blue')
graph_avg_blue = ROOT.TGraph()
graph_avg_blue.SetName('avg_blue')

for i in range(len(l)-1):

    if not '.jpg' in l[i]: continue

    print os.path.join(input_dir, l[i])
    img = Image.open(os.path.join(input_dir, l[i]))

    y = img.getextrema()
    data = img.getdata()
    blue = [pixel[2] for pixel in data]
    avg = sum(blue)/float(len(blue))

    print avg

    graph_min_blue.SetPoint(i, i, y[2][0])
    graph_max_blue.SetPoint(i, i, y[2][1])
    graph_avg_blue.SetPoint(i, i, avg)

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
canvas.Print('{0}.png'.format(input_dir))

