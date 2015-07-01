import ROOT, math, palette, array, os, sys

## Take care of color palette
def set_palette(name='blue', ncontours=50):
    """Set a color palette from a given RGB list
    stops, red, green and blue should all be lists of the same length
    see set_decent_colors for an example"""

    if name == "blue":
        stops = [0.00, 1.00]
        red   = [0.00, 0.00]
        green = [0.00, 0.80]
        blue  = [0.31, 1.00]

    elif name == "inverse blue":
		stops = [0.00, 0.30, 1.00]
		red   = [0.80, 0.00, 0.00]
		green = [0.95, 0.80, 0.00]
		blue  = [1.00, 1.00, 0.31]
    # elif name == "whatever":
        # (define more palettes)
    else:
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00]

    s = array.array('d', stops)
    r = array.array('d', red)
    g = array.array('d', green)
    b = array.array('d', blue)

    npoints = len(s)
    ROOT.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    ROOT.gStyle.SetNumberContours(ncontours)

set_palette('default')


###################################################
def remove_negative_bins(h):
	"""
	Sets all negative bins to 0
	"""

	nx = h.GetNbinsX()

	for i in range(nx):
		if h.GetBinContent(i+1) < 0:
			h.SetBinContent(i+1, 0)


###################################################
def make_band(curve, nom, up, down):
	"""
	Make a graph band from an up and a down variation around a nominal
	"""

	g = ROOT.TGraphAsymmErrors()

	nx    = curve.GetNbinsX()
	xaxis = curve.GetXaxis()

	for i in range(nx):
		x = xaxis.GetBinLowEdge(i+1) + xaxis.GetBinWidth(i+1)/2.0
		y = curve.GetBinContent(i+1)

		y_nom  = nom.GetBinContent(i+1)
		y_up   = up.GetBinContent(i+1)
		y_down = down.GetBinContent(i+1)

		g.SetPoint(i, x, y)
		g.SetPointEYlow(i, abs(y_nom-y_down))
		g.SetPointEYhigh(i, abs(y_up-y_nom))
		g.SetPointEXlow(i, 0)
		g.SetPointEXhigh(i, 0)
	return g






###################################################
def copy_histogram(th1f):
	"""
	Copy a histogram
	"""

	name  = th1f.GetName()
	if name.endswith('copy'):
		copy_index = int(name[-5])
		name = name.replace('_{0}copy'.format(copy_index), '_{0}copy'.format(copy_index + 1))
	else:
		name += '_0copy'
	nx    = th1f.GetNbinsX()
	xaxis = th1f.GetXaxis()
	xlo   = xaxis.GetBinLowEdge(1)
	xhi   = xaxis.GetBinUpEdge(nx)

	new_th1f = ROOT.TH1F(name, th1f.GetTitle(), nx, xlo, xhi)
	for i in range(nx):
		new_th1f.SetBinContent(i+1, th1f.GetBinContent(i+1))
		new_th1f.SetBinError(i+1, th1f.GetBinError(i+1))

	return new_th1f





###################################################
def add_in_all_bins(th1f, value):
	"""
	Shifts the histogram up and down
	"""

	nx = th1f.GetNbinsX()
	for i in range(nx):
		th1f.SetBinContent(i+1, th1f.GetBinContent(i+1) + value)



###################################################
def function_to_histogram(tf1, nbins, xlo, xhi):
	"""
	transform a function into a histogram
	"""

	name = tf1.GetName()
	th1f = ROOT.TH1F('%s_tf1' % name, '%s_tf1' % name, nbins, xlo, xhi)

	nx    = th1f.GetNbinsX()
	xaxis = th1f.GetXaxis()

	for i in range(nx):
		x = xaxis.GetBinLowEdge(i+1) + xaxis.GetBinWidth(i+1)/2.0
		bin_content = tf1.Eval(x)
		th1f.SetBinContent(i+1, bin_content)
		th1f.SetBinError(i+1, 0.0)

	return th1f



###################################################
def custom_divide(num, den):
	"""
	Divides histograms together and deal correctly with the error in case the distributions are statistically correlated
	"""

	num_name = num.GetName()
	den_name = den.GetName()

	nx    = num.GetNbinsX()
	xaxis = num.GetXaxis()
	xlo   = xaxis.GetBinLowEdge(1)
	xhi   = xaxis.GetBinUpEdge(nx)

	dividend = ROOT.TH1F('%s_div_%s' % (num_name, den_name), '%s_div_%s' % (num_name, den_name), nx, xlo, xhi)

	for i in range(nx):
		num_value = num.GetBinContent(i+1)
		num_error = num.GetBinError(i+1)
		den_value = den.GetBinContent(i+1)

		if den_value == 0.0: continue

		div_value = float(num_value)/float(den_value)
		div_error = float(num_error)/float(den_value)

		dividend.SetBinContent(i+1, div_value)
		dividend.SetBinError(i+1, div_error)

	return dividend





###################################################
def histogram_to_graph(th1f, index_offset=0):
	"""
	Creates a graph out of a histograms using only non-empty bins
	"""

	graph = ROOT.TGraphErrors()
	graph.SetName('%s_graph' % th1f.GetName())

	nx    = th1f.GetNbinsX()
	xaxis = th1f.GetXaxis()

	graph_i = 0 + index_offset

	for i in range(nx):
		bin_value = th1f.GetBinContent(i+1)
		bin_error = th1f.GetBinError(i+1)

		if bin_value > 0.0:
			graph.SetPoint(graph_i, xaxis.GetBinLowEdge(i+1), bin_value)
			graph.SetPointError(graph_i, 0, bin_error)
			graph_i += 1

	return graph



###################################################
def graph_to_histogram(g):
	"""
	Creates a graph out of a histograms using only non-empty bins
	"""

	nx = g.GetN()

	h = ROOT.TH1F('g_{0}'.format(g.GetName()), 'g_{0}'.format(g.GetTitle()), nx, 0, nx)

	x = ROOT.Double()
	y = ROOT.Double()

	for i in range(nx):
		g.GetPoint(i, x, y)
		h.SetBinContent(i+1, y)

	return h




###################################################
def relative_percent_plot(ref_th1f, th1f, x_avg_range=[], x_range=[]):
	"""
	Converts a histograms into a percent plot
	"""

	## truncate histograms
	truncated_ref_h = truncate(ref_th1f, x_range=x_range, identifier='ref')
	truncated_h     = truncate(th1f, x_range=x_range)

	## Calculate the average reference histogram
	name  = th1f.GetName()
	nx    = truncated_ref_h.GetNbinsX()
	xaxis = truncated_ref_h.GetXaxis()
	xlo   = xaxis.GetBinLowEdge(1)
	xhi   = xaxis.GetBinUpEdge(nx)

	if not x_avg_range:
		x_avg_range = [xlo, xhi]

	average_ref  = 0.0
	n_empty_bins = 0
	n_total_bins = 0

	for i in range(nx):

		bin_xlo   = xaxis.GetBinLowEdge(i+1)
		bin_xhi   = xaxis.GetBinUpEdge(i+1)

		if bin_xlo < x_avg_range[0]: continue
		if bin_xhi > x_avg_range[1]: continue

		n_total_bins += 1

		bin_value_ref = truncated_ref_h.GetBinContent(i+1)
		bin_value     = truncated_h.GetBinContent(i+1)
		if (abs(bin_value) > 0.0) and (abs(bin_value_ref) > 0.0):
			average_ref += bin_value_ref
		else:
			n_empty_bins += 1

	if nx > n_empty_bins:
		average_ref /= float(n_total_bins-n_empty_bins)
	else:
		return None

	## Create output histogram:
	output = ROOT.TH1F('%s_rpp' % name, '%s_rpp' % name, nx, xlo, xhi)

	for i in range(nx):
		bin_value = 100*(truncated_h.GetBinContent(i+1)/average_ref - 1)
		bin_error = 100*(truncated_h.GetBinError(i+1)/average_ref)
		if truncated_h.GetBinContent(i+1) == 0.0:
			bin_value = -1111
		output.SetBinContent(i+1, bin_value)
		output.SetBinError(i+1, bin_error)

	return output


###################################################
def truncate(th1f, x_range=[], identifier='', no_error=False):
	"""
	Truncate a histogram between bounds
	"""

	## Gather TH1F dimensions
	name  = th1f.GetName()
	nx    = th1f.GetNbinsX()
	xaxis = th1f.GetXaxis()
	xlo   = xaxis.GetBinLowEdge(1)
	xhi   = xaxis.GetBinUpEdge(nx)

	## Make sure the ranges provided make sense
	if x_range == []:
		x_range = [xlo, xhi]
	else:
		if x_range[0] < xlo: x_range[0] = xlo
		if x_range[1] > xhi: x_range[1] = xhi

	## Make sure the ranges correspond to bin boundaries
	xlo_integer = int(math.floor( (nx*(x_range[0] - xlo)/(xhi - xlo)) ))
	xhi_integer = int(math.ceil( (nx*(x_range[1] - xlo)/(xhi - xlo)) ))
	x_range[0] = xlo + xlo_integer * (xhi - xlo)/float(nx)
	x_range[1] = xlo + xhi_integer * (xhi - xlo)/float(nx)
	x_nbins    = xhi_integer - xlo_integer

	## Create new histogram
	truncated_name = '%s_(%f-%f)_%s' % (name, x_range[0], x_range[1], identifier)
	truncated = ROOT.TH1F(truncated_name, truncated_name, x_nbins, x_range[0], x_range[1])
	truncated.Sumw2()

	## j is the axis being integrated, i is the axis being integrated
	for i in range(xlo_integer, xhi_integer):
		bin_content = th1f.GetBinContent(i+1)
		bin_error   = th1f.GetBinError(i+1)

		truncated.SetBinContent(i - xlo_integer + 1, bin_content)
		if not no_error:
			truncated.SetBinError(i - xlo_integer + 1, bin_error)
		else:
			truncated.SetBinError(i - xlo_integer + 1, 0)

	return truncated



###################################################
def project_and_cut(th2f, project_on_axis='x', x_range=[], y_range=[], variable_binning=False):
	"""
	Project a TH2F along a particular axis, with an optional range cut on the other axis
	"""

	## Gather TH2F dimensions
	name = th2f.GetName()

	nx = th2f.GetNbinsX()
	ny = th2f.GetNbinsY()

	xaxis = th2f.GetXaxis()
	yaxis = th2f.GetYaxis()

	xlo = xaxis.GetBinLowEdge(1)
	xhi = xaxis.GetBinUpEdge(nx)

	ylo = yaxis.GetBinLowEdge(1)
	yhi = yaxis.GetBinUpEdge(ny)

	xbins = []
	for i in range(nx):
		xbins.append(xaxis.GetBinLowEdge(i+1))
	xbins.append(xaxis.GetBinUpEdge(nx))

	ybins = []
	for i in range(ny):
		ybins.append(yaxis.GetBinLowEdge(i+1))
	ybins.append(yaxis.GetBinUpEdge(ny))


	## Make sure the ranges provided make sense
	if x_range == []:
		x_range = [xlo, xhi]
	else:
		if x_range[0] < xlo: x_range[0] = xlo
		if x_range[1] > xhi: x_range[1] = xhi

	if y_range == []:
		y_range = [ylo, yhi]
	else:
		if y_range[0] < ylo: y_range[0] = ylo
		if y_range[1] > yhi: y_range[1] = yhi

	## Make sure the ranges correspond to bin boundaries
	## for x axis range
	xlo_integer, x_range[0] = min(enumerate(xbins), key=lambda x: abs(x[1]-x_range[0]))
	xhi_integer, x_range[1] = min(enumerate(xbins), key=lambda x: abs(x[1]-x_range[1]))
	x_nbins                 = xhi_integer - xlo_integer

	## for y axis range
	ylo_integer, y_range[0] = min(enumerate(ybins), key=lambda x: abs(x[1]-y_range[0]))
	yhi_integer, y_range[1] = min(enumerate(ybins), key=lambda x: abs(x[1]-y_range[1]))
	y_nbins                 = yhi_integer - ylo_integer

	## Select the axes for the projection
	if project_on_axis == 'x':
		nbins = x_nbins
		bins  = xbins
		lo    = x_range[0]
		hi    = x_range[1]
		ilo   = xlo_integer
		ihi   = xhi_integer
		jlo   = ylo_integer
		jhi   = yhi_integer

	else:
		nbins = y_nbins
		bins  = ybins
		lo    = y_range[0]
		hi    = y_range[1]
		ilo   = ylo_integer
		ihi   = yhi_integer
		jlo   = xlo_integer
		jhi   = xhi_integer

	projection_name = '%s_%s_x(%f-%f)_y(%f-%f)' % (name, project_on_axis, x_range[0], x_range[1], y_range[0], y_range[1])
	if variable_binning:
		projection = ROOT.TH1F(projection_name, projection_name, nbins, array.array('d', bins))
	else:
		projection = ROOT.TH1F(projection_name, projection_name, nbins, lo, hi)

	## j is the axis being integrated, i is the axis being integrated
	for i in range(ilo, ihi):
		bin_content = 0.0
		bin_error   = 0.0
		for j in range(jlo, jhi):
			if project_on_axis == 'x':
				bin_index = th2f.GetBin(i+1,j+1)
			else:
				bin_index = th2f.GetBin(j+1,i+1)

			bin_content += th2f.GetBinContent(bin_index)
			bin_error   += th2f.GetBinError(bin_index)**2

		bin_error = math.sqrt(bin_error)
		projection.SetBinContent(i - ilo + 1, bin_content)
		projection.SetBinError(i - ilo + 1, bin_error)

	return projection


###############################################################
def project_and_cut_3D(th3f, project_on_plane='xy', x_range=[], y_range=[], z_range=[]):
	"""
	Project a 3D histogram into a 2D histogram
	"""

	## Gather TH2F dimensions
	name = th3f.GetName()

	nx = th3f.GetNbinsX()
	ny = th3f.GetNbinsY()
	nz = th3f.GetNbinsZ()

	xaxis = th3f.GetXaxis()
	yaxis = th3f.GetYaxis()
	zaxis = th3f.GetZaxis()

	xlo = xaxis.GetBinLowEdge(1)
	xhi = xaxis.GetBinUpEdge(nx)

	ylo = yaxis.GetBinLowEdge(1)
	yhi = yaxis.GetBinUpEdge(ny)

	zlo = zaxis.GetBinLowEdge(1)
	zhi = zaxis.GetBinUpEdge(nz)

	## Make sure the ranges provided make sense
	if x_range == []:
		x_range = [xlo, xhi]
	else:
		if x_range[0] < xlo: x_range[0] = xlo
		if x_range[1] > xhi: x_range[1] = xhi

	if y_range == []:
		y_range = [ylo, yhi]
	else:
		if y_range[0] < ylo: y_range[0] = ylo
		if y_range[1] > yhi: y_range[1] = yhi

	if z_range == []:
		z_range = [zlo, zhi]
	else:
		if z_range[0] < zlo: z_range[0] = zlo
		if z_range[1] > zhi: z_range[1] = zhi

	## Make sure the ranges correspond to bin boundaries

	## for x axis range
	xlo_integer = int(math.floor( (nx*(x_range[0] - xlo)/(xhi - xlo)) ))
	xhi_integer = int(math.ceil( (nx*(x_range[1] - xlo)/(xhi - xlo)) ))
	x_range[0] = xlo + xlo_integer * (xhi - xlo)/float(nx)
	x_range[1] = xlo + xhi_integer * (xhi - xlo)/float(nx)
	x_nbins    = xhi_integer - xlo_integer

	## for y axis range
	ylo_integer = int(math.floor( (ny*(y_range[0] - ylo)/(yhi - ylo)) ))
	yhi_integer = int(math.ceil( (ny*(y_range[1] - ylo)/(yhi - ylo)) ))
	y_range[0] = ylo + ylo_integer * (yhi - ylo)/float(ny)
	y_range[1] = ylo + yhi_integer * (yhi - ylo)/float(ny)
	y_nbins    = yhi_integer - ylo_integer

	## for y axis range
	zlo_integer = int(math.floor( (nz*(z_range[0] - zlo)/(zhi - zlo)) ))
	zhi_integer = int(math.ceil( (nz*(z_range[1] - zlo)/(zhi - zlo)) ))
	z_range[0] = zlo + zlo_integer * (zhi - zlo)/float(nz)
	z_range[1] = zlo + zhi_integer * (zhi - zlo)/float(nz)
	z_nbins    = zhi_integer - zlo_integer

	## Figure out the projection (i and j are the indices of the new th2f,
	## k is the index being integrated on)
	if project_on_plane == 'xy':
		nbins_i = x_nbins
		lo_i    = x_range[0]
		hi_i    = x_range[1]

		nbins_j = y_nbins
		lo_j    = y_range[0]
		hi_j    = y_range[1]

		ilo   = xlo_integer
		ihi   = xhi_integer

		jlo   = ylo_integer
		jhi   = yhi_integer

		klo   = zlo_integer
		khi   = zhi_integer

	elif project_on_plane == 'yx':
		nbins_i = y_nbins
		lo_i    = y_range[0]
		hi_i    = y_range[1]

		nbins_j = x_nbins
		lo_j    = x_range[0]
		hi_j    = x_range[1]

		ilo   = ylo_integer
		ihi   = yhi_integer

		jlo   = xlo_integer
		jhi   = xhi_integer

		klo   = zlo_integer
		khi   = zhi_integer

	elif project_on_plane == 'xz':
		nbins_i = x_nbins
		lo_i    = x_range[0]
		hi_i    = x_range[1]

		nbins_j = z_nbins
		lo_j    = z_range[0]
		hi_j    = z_range[1]

		ilo   = xlo_integer
		ihi   = xhi_integer

		jlo   = zlo_integer
		jhi   = zhi_integer

		klo   = ylo_integer
		khi   = yhi_integer

	elif project_on_plane == 'zx':
		nbins_i = z_nbins
		lo_i    = z_range[0]
		hi_i    = z_range[1]

		nbins_j = x_nbins
		lo_j    = x_range[0]
		hi_j    = x_range[1]

		ilo   = zlo_integer
		ihi   = zhi_integer

		jlo   = xlo_integer
		jhi   = xhi_integer

		klo   = ylo_integer
		khi   = yhi_integer

	elif project_on_plane == 'yz':
		nbins_i = y_nbins
		lo_i    = y_range[0]
		hi_i    = y_range[1]

		nbins_j = z_nbins
		lo_j    = z_range[0]
		hi_j    = z_range[1]

		ilo   = ylo_integer
		ihi   = yhi_integer

		jlo   = zlo_integer
		jhi   = zhi_integer

		klo   = xlo_integer
		khi   = xhi_integer

	elif project_on_plane == 'zy':
		nbins_i = z_nbins
		lo_i    = z_range[0]
		hi_i    = z_range[1]

		nbins_j = y_nbins
		lo_j    = y_range[0]
		hi_j    = y_range[1]

		ilo   = zlo_integer
		ihi   = zhi_integer

		jlo   = ylo_integer
		jhi   = yhi_integer

		klo   = xlo_integer
		khi   = xhi_integer

	else:
		print 'Wrong axes passed to project_and_cut_3D()'
		return

	projection_name = '%s_%s_x(%f-%f)_y(%f-%f)_z(%f-%f)' % (
		name,
		project_on_plane,
		x_range[0], x_range[1],
		y_range[0], y_range[1],
		z_range[0], z_range[1]
		)

	projection = ROOT.TH2F(
		projection_name,
		projection_name,
		nbins_i, lo_i, hi_i,
		nbins_j, lo_j, hi_j)

	## j is the axis being integrated, i is the axis being integrated
	for i in range(ilo, ihi):
		for j in range(jlo, jhi):
			bin_content = 0.0
			bin_error   = 0.0
			for k in range(klo, khi+1):
				if project_on_plane == 'xy':
					bin_index = th3f.GetBin(i+1,j+1,k+1)
				elif project_on_plane == 'yx':
					bin_index = th3f.GetBin(j+1,i+1,k+1)
				elif project_on_plane == 'zx':
					bin_index = th3f.GetBin(j+1,k+1,i+1)
				elif project_on_plane == 'xz':
					bin_index = th3f.GetBin(i+1,k+1,j+1)
				elif project_on_plane == 'zy':
					bin_index = th3f.GetBin(k+1,j+1,i+1)
				elif project_on_plane == 'yz':
					bin_index = th3f.GetBin(k+1,i+1,j+1)
				else:
					return

				bin_content += th3f.GetBinContent(bin_index)
				bin_error   += th3f.GetBinError(bin_index)**2

			bin_error = math.sqrt(bin_error)
			projection.SetBinContent(i-ilo+1, j-jlo+1, bin_content)
			projection.SetBinError(i-ilo+1, j-jlo+1, math.sqrt(bin_error))

	return projection



###############################################################
def make_fake_rate_graph(name, h_all, h_pass):
	"""
	Make a fake rate TGraphAsymmError out of a fail and a pass histogram
	"""

	h_fail  = ROOT.TH1F('%sall' % name, '%sall' % name, 70, 0, 70)
	h_fail.Add(h_all)
	h_fail.Add(h_pass, -1.0)

	g = ROOT.TGraphAsymmErrors(h_fail, h_all)

	## Adjustments
	g.SetMarkerStyle(20)
	g.SetMarkerSize(0.6)
	g.SetLineWidth(1)
	g.SetLineStyle(1)

	g.SetTitle('')
	g.GetXaxis().SetTitle('actual N_{int.} / bunch-crossing (MC)')
	g.GetXaxis().SetTitleSize(0.045)
	g.GetYaxis().SetTitle('Track fake rate')
	g.GetYaxis().SetTitleSize(0.045)
	g.GetYaxis().SetTitleOffset(1.15)

	## Suppress horizontal error bar
	n = g.GetN()
	for i in range(n):
		g.SetPointEXlow(i, 0)
		g.SetPointEXhigh(i,0)

	return g


###############################################################
def make_linearity_plot_single(name, h, h_mu):
        """
        Make a plot of the linearity of the total, number of tracks, and fake tracks
        """

        ## Fill the TGraph
        g = ROOT.TGraph()
        for i in range(0, 70):
            graph_i = i
            x = h.GetBinLowEdge(i+1)
            y = h.GetBinContent(i+1) / (h_mu.GetBinContent(i+1)*h_mu.GetBinLowEdge(i+1))
            g.SetPoint(graph_i, x, y)

        ## Adjustments
        g.SetMarkerStyle(20)
        g.SetMarkerSize(0.6)
        g.SetLineWidth(1)
        g.SetLineStyle(1)

        g.SetTitle('')
        g.GetXaxis().SetTitle('actual N_{int.} / bunch-crossing (MC)')
        g.GetXaxis().SetTitleSize(0.045)
        g.GetYaxis().SetTitle('Avg. N. tracks / interaction')
        g.GetYaxis().SetTitleSize(0.045)
        g.GetYaxis().SetTitleOffset(0.9)

        return g


###############################################################
def linearize_hist(h, h_mu):
	"""
	Linearize the histogram with a mu distribution
	"""

	for i in range(0, 70):
		if not h_mu.GetBinContent(i+1)*h_mu.GetBinLowEdge(i+1) == 0:
			value = h.GetBinContent(i+1) / (h_mu.GetBinContent(i+1)*h_mu.GetBinLowEdge(i+1))
			error = abs(h.GetBinError(i+1) / (h_mu.GetBinContent(i+1)*h_mu.GetBinLowEdge(i+1))) + abs(h_mu.GetBinError(i+1) * h.GetBinContent(i+1) / (h_mu.GetBinContent(i+1)**2 * h_mu.GetBinLowEdge(i+1)))
		else:
			value = 0
			error = 0
		h.SetBinContent(i+1, value)
		h.SetBinError(i+1, error)

################################################################
def set_range(graphs):
	"""
	Sets the y-axis plot ranges on a collection of graphs
	"""

	maximum = 0.0
	minimum = 100000000.0
	for g in graphs:

		n = g.GetN()
		for i in range(n):

			x,y = ROOT.Double(0), ROOT.Double(0)
			g.GetPoint(i, x ,y)

			if y < minimum:
				minimum = y

			if y > maximum:
				maximum = y

	for g in graphs:
		g.SetMinimum(minimum - 0.1*(maximum-minimum))
		g.SetMaximum(maximum + 0.3*(maximum-minimum))


################################################################
def apply_color_scheme(graphs):
	"""
	Define a color scheme for good contrast on graphs
	"""

	n = len(graphs)

	spectrum = palette.color_spectrum(n)

	for i in range(n):
		color = ROOT.TColor.GetColor(spectrum[i])
		graphs[i].SetMarkerColor(color)
		graphs[i].SetLineColor(color)
		graphs[i].SetFillColor(color)


################################################################
def draw_all(graphs, legend, canvas, name, extras=[]):
	"""
	Draws all the plots to canvas
	"""

	canvas.Clear()

	n = len(graphs)
	for i in range(n):
		if i == 0:
			graphs[i].Draw('ALP')
		else:
			graphs[i].Draw('SAMELP')

	legend.Draw('SAME')

	for extra in extras:
		extra.Draw('SAME')

	canvas.Print('%s.png' % name)


################################################################
def draw_all_hist(graphs, legend, canvas, label='', maximum = None):
	"""
	Draws all the plots to canvas
	"""

	canvas.Clear()
	n = len(graphs)

	if maximum is None:
		themax = 0
		for g in graphs:
			thismax = g.GetMaximum()
			if thismax > themax:
				themax = thismax

	for i in range(n):
		if i == 0:
			graphs[i].Draw('HIST')
		else:
			graphs[i].Draw('HISTSAME')

		graphs[i].SetMinimum(0.0)

		if not maximum is None:
			graphs[i].SetMaximum(maximum)
		else:
			graphs[i].SetMaximum(1.2*themax)


	legend.Draw('SAME')

	latex = ROOT.TLatex()
	latex.DrawLatexNDC(0.73, 0.83, label)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	