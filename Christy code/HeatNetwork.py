'''
Basic Heat Network Model for LEO Osney Research Hub 3YP
Author: Christy Nganjimi
'''

import sys
sys.path.append(r'c:\python37\lib\site-packages')


def HN_Demand(Qc, Tsc, Trc, COP):

    ''' Returns a list
     [0] = HP Electricity Demand Under Normal Operation
     [1] = HN Pumping Demand
     [2] = HN Combined Electricity Demand without SMART operations '''

    import math

    # Water Constants
    nu = 485 * (10 ** -6)  # pa.s Viscosity
    cp = 4185              # J/kg.K Specific heat of water
    rho = 982.6            # kg/m-3 Density of Water
    hw = 3000              # W/m2.K Convective Coefficient of water

    # Natural Constants
    Tg = 14.6               # degrees C MeanSoil Temp
    g = 9.81                # m/s2 Gravitational constant

    # Pipe Dimensions
    d = 50 * (10 ** -3)     # m Pipe diameter
    r = d / 2               # m Pipe radius
    D = 125 * (10 ** -3)    # m Insulation diameter
    R = D / 2               # m Insulation radius
    L = 11*(10**3)          # m Length of pipeline
    ki = 0.0244             # W/m.K Insulation Conductivity

    # Pipe Constants
    ep = 0.045 * (10**-3)   # m Surface roughness of pipe
    Kl = 2.36  # Loss Coefficients

    def mass_flow(Qc, Tsc, Trc):
        ''' Returns mass flow rates in kg/s with inputs
        Qc = consumer heat demand kW
        Tsc = Supply temperature degrees C
        Trc = Return temperature degrees C
        cp = Specific heat capacity of water '''

        cp = 4185  # J/kg.K Specific heat of water
        delta_t = Tsc - Trc

        m = Qc*1000/(delta_t*cp)
        return m


    def Reynold_no(Qc, Tsc, Trc, nu, d):
        '''' Return the Reynold's Number given inputs
        Qc = consumer heat demand kW
        Tsc = Supply temperature degrees C
        Trc = Return temperature degrees C
        nu = Viscosity in Pa.s
        d = Pipe diameter in metres '''

        Re = 4*mass_flow(Qc, Tsc, Trc)/(nu*d*math.pi)
        return Re



    def fric_factor(Qc, Tsc, Trc, nu, d):

        ''' Returns a Newton-Raphson Approximation to the friction factor
        f0 = starting value
        rey = Reynold's number
        er = maximum Error '''

        Re = Reynold_no(Qc, Tsc, Trc, nu, d)
        def g(f, rey):
            d1 = 50 * (10 ** -3)  # Pipe diameter in metres
            eps = 0.045*(10**-3)      #Surface roughness of steel in meters

            g_f = f**(-0.5) + 2*math.log((eps/(3.7*d1)) + 2.51/(rey*(f**0.5)))
            return g_f


        def dg(f, rey):
            d1 = 50 * (10 ** -3)  # Pipe diameter in metres
            eps = 0.045 * (10 ** -3)  #Surface roughness of steel in meters

            d_g = (-0.5*f**(-3/2))*(1 + (2*2.51)/(math.log(10)*rey*((eps/(3.7*d1)) + 2.51/(rey*(f**0.5)))))
            return d_g



        def df(g, f, rey):
            return abs(0 - g(f, rey))


        fo = 0.008     # starting value
        err = 1e-10    # maximum error

        def newtons_method(g, dg, f0, Re, er):
            delta = df(g, f0, Re)

            while delta > er:
                f0 = f0 - g(f0, Re) / dg(f0, Re)
                delta = df(g, f0, Re)

            return f0

        f_l = newtons_method(g, dg, fo, Re, err)
        return f_l



    def head_loss(Qc, Tsc, Trc, nu, d, L, Kl, g):
        ''' Returns the Pipe Head Loss in m '''

        v = (4*mass_flow(Qc, Tsc, Trc))/(math.pi*rho*d**2)
        fr = fric_factor(Qc, Tsc, Trc, nu, d)
        head_l = (fr*(L/d) + Kl)*(0.5*(v**2)/g)

        return head_l

    def U_overall(R, r, ki, hw):
        ''' Returns the Overall Heat Loss coefficient
        R = Insulation radius in m
        r = pipe radius in m
        ki = heat transfer coefficient of insulation
        hw = convective coefficient of water '''

        U = 1/((math.log(R/r))/ki + 1/(r*hw))

        return U


    def Ts_pump(Qc, Tsc, Trc, Tg, cp, L, R, r, ki, hw):
        ''' Returns the supply temp at pump to meet supply temp at consumer '''

        m = mass_flow(Qc, Tsc, Trc)
        U = U_overall(R, r, ki, hw)

        Ts = (Tsc - Tg)/(math.e**((-2*R*L*U*math.pi)/(cp*m))) + Tg

        return Ts


    def Tr_pump(Qc, Tsc, Trc, Tg, cp, L, R, r, ki, hw):
        ''' Returns the return temp to pump to based on return temp of consumer '''

        m = mass_flow(Qc, Tsc, Trc)
        U = U_overall(R, r, ki, hw)

        Tr = (Trc - Tg)*(math.e ** ((-2 * R * L * U * math.pi) / (cp * m))) + Tg

        return Tr

    def Q_loss(Qc, Tsc, Trc, Tg, cp, L, R, r, ki, hw):
        ''' Returns the Thermal losses '''

        Ts = Ts_pump(Qc, Tsc, Trc, Tg, cp, L, R, r, ki, hw)
        Tr = Tr_pump(Qc, Tsc, Trc, Tg, cp, L, R, r, ki, hw)

        Ts_av = (Ts + Tsc)*0.5
        Tr_av = (Tr + Trc)*0.5
        U = U_overall(R, r, ki, hw)

        Ql_s = 2*L*math.pi*(Ts_av - Tg)*U*R*10**-3
        Ql_r = 2*L*math.pi*(Tr_av - Tg)*U*R*10**-3

        Ql = Ql_s + Ql_r

        return Ql


    def p_mech(Qc, Tsc, Trc, nu, d, L, Kl, g):
        ''' Returns the Mechanical power needed to pump the flow at the required mass flow rate '''
        m = mass_flow(Qc, Tsc, Trc)
        hl = head_loss(Qc, Tsc, Trc, nu, d, L, Kl, g)

        P = 1.2*m*(hl+10)*g*10**-3

        return P

    Qloss = Q_loss(Qc, Tsc, Trc, Tg, cp, L, R, r, ki, hw)

    Qs = Qloss + Qc                 # HP heat demand in normal operation

    Pmech = p_mech(Qc, Tsc, Trc, nu, d, L, Kl, g) # HN pumping demand

    E_HN = Qs/COP + Pmech           # HN Combined electricity demand

    HN_Demand = (Qs/COP, Pmech, E_HN)

    return HN_Demand
