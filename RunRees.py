#!/usr/bin/env python
from dateutil.parser import parse
from matplotlib.pyplot import show
import seaborn as sns
sns.color_palette(sns.color_palette("cubehelix"))
sns.set(context='talk', style='whitegrid',font_scale=1.5,
        rc={'image.cmap': 'cubehelix_r'}) #for contour
from numpy import array
#
from reesaurora import (reesiono,loadaltenergrid,lambda_comp,albedo,
                                   PitchAngle_range, energy_deg)
from reesaurora.plots import fig7,fig8,fig11, fig12, fig13, plotA
from gridaurora.writeeigen import writeeigen
from gridaurora.solarangle import solarzenithangle
#
isotropic=True
"""
Models unit incident flux from the magnetosphere ionizing N2,O,O2
vs. altitude and inital beam energy in the ionosphere.
The electron production rate q is related to auroral optical intensity via
known proportions.

Variables:
q: e- production rate [cm^-3 s^-1]
Phi: "flux" [cm^-2 s^-1 eV^-1]
A: energy deposition matrix [eV cm^-1]

References:
Rees 1989
Wedlund et al "Electron Energy Spectra and Auroral Arcs" JGR 2013
Sergienko and Ivanov 1993 "A new approach to calculate the excitation of atmospheric gases by auroral electron impact"
"""
Eplot = array([50,100,500,1e3,5e3,1e4])
llp = (65., -148.)
tp = '2013-01-01T12Z'

def runrees(t,glat,glon,isotropic,outfn,minalt,nalt,vlim,verbose):
    """
    inputs:
    t: time(s) to model, datetime() or ut1_unix


    """
    z,E = loadaltenergrid(minalt,nalt)

    Q = reesiono(t, z, E, glat, glon,isotropic,verbose,datfn='data/SergienkoIvanov.h5')

#%% outputs
    writeeigen(outfn,E,t,z,prates=Q,tezs=None,latlon=(glat,glon))

    plotA(Q,'Volume Production Rate {}  ({:.2f},{:.2f})'.format(t,glat,glon),vlim)

def makefig7():
    """
    Energy deposition (W Eqn A1) plots
    """
    z = loadaltenergrid(80.,200)[0]

    dens,temp = rungtd1d(tp,z,llp[0],llp[1],f107a=150.,f107=150.,ap=4.,
                         mass=48., #leave mass=48. !
                     tselecopts=array([1,1,1,1,1,1,1,1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],float))

    # NOTE kg m^-2 *10 = g cm^-2
    rho = dens.loc[:,'Total'] * 10. # mass density of atmosphere [g cm^-3]
    #eqn A1 Sergienko 1993
    W = energy_deg(Eplot,isotropic,rho,datfn,verbose=0)

    fig7(W,z,Eplot)

def makefig8():
    z = loadaltenergrid(80.,200)[0]

    E = array([300,500,1000,5000,10000])

    Q = reesiono('2013-01-01T12Z', z, E, glat=65., glon=-148.,
                 isotropic=False,verbose=0,datfn='data/SergienkoIvanov.h5')

    fig8(Q)


def makefig11(datfn):
#%% make figure 11 from Sergienko and Ivanov 1993
    #Am,Lambda,chi = energy_deg(E,isotropic,dens)
    chi = tile(arange(0,3,0.01),(Eplot.size,1))

    Lambda_m = lambda_comp(chi,Eplot,isotropic=False,fn=datfn)[0]
    Lambda_i = lambda_comp(chi,Eplot,isotropic=True,fn=datfn)[0]

    fig11(Eplot,chi,Lambda_m,Lambda_i)

def makefig12(datfn):
#%% make figure 12
    chi = float('nan') #not used here

    E = logspace(1.69,4,200)
    C_m = lambda_comp(chi,E,isotropic=False,fn=datfn)[1]
    C_i = lambda_comp(chi,E,isotropic=True,fn=datfn)[1]

    fig12(E,C_m,C_i)

def makefig13(datfn):
    # albedo plots
    E = logspace(1.69,4,200)

    af_m = albedo(E,isotropic=False,fn=datfn)
    af_i = albedo(E,isotropic=True,fn=datfn)

    rng_m = PitchAngle_range(E,isotropic=False)
    rng_i = PitchAngle_range(E,isotropic=True)

    fig13(E,af_m,af_i,rng_m,rng_i)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='rees model of excitation rates for the aurora')
    p.add_argument('-t','--simtime',help='yyyy-mm-ddTHH:MM:SSZ time of sim',default='2013-01-01T12Z')
    p.add_argument('-c','--latlon',help='geodetic latitude/longitude (deg)',type=float,nargs=2,default=(65.,-148.))
    p.add_argument('--minalt',help='minimum altitude in grid [km]',type=float,default=80.)
    p.add_argument('--nalt',help='Number of points in altitude grid',type=int,default=286)
    p.add_argument('-o','--outfn',help='give hdf5 filename to save eigenprofile production')
    p.add_argument('--isotropic',help='isotropic or non-isotropic pitch angle',action='store_true')
    p.add_argument('--vlim',help='plotting limits on energy dep and production plots',nargs=2,type=float,default=(1e-7,1e1))
    p.add_argument('-v','--verbose',help='plots inline',action='count',default=0)
    p = p.parse_args()

    datfn='data/SergienkoIvanov.h5'

    t = parse(p.simtime)
#%%
    #makefig7()
    makefig8()
    #makefig11(datfn)
    #makefig12(datfn)
    #makefig13(datfn)

    runrees(t,p.latlon[0],p.latlon[1], p.isotropic,  p.outfn,p.minalt,p.nalt,p.vlim,p.verbose)

    print('solar zenith angle  {:.1f} '.format(solarzenithangle(p.simtime,p.latlon[0],p.latlon[1],0.)[0]))

    show()
