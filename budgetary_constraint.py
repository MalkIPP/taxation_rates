# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import division


import datetime
import os

import matplotlib.pyplot as plt
import pandas as pd

import plotly.plotly as py
from plotly.graph_objs import *
py.sign_in('Python-Demo-Account', 'gwt101uhh0')
from ggplot import *

from openfisca_core import periods
from openfisca_france.tests import base
from openfisca_core.rates import average_rate, marginal_rate

def celibataire(year,sali):
    return dict(
        parent1 = dict(birth = datetime.date(year - 40, 1, 1),sali = sali),
        menage = dict(so = 4),
        )


def parent_isole(year,sali):
    return dict(
        parent1 = dict(birth = datetime.date(year - 40, 1, 1),sali = sali),
        enfants = [
            dict(birth = datetime.date(year - 9, 1, 1)),
            ],
        menage = dict(so = 4),
        )


def couple_sans_enfant(year,sali):
    return dict(
        parent1 = dict(
            birth = datetime.date(year - 40, 1, 1),
            statmarit = 1,
            sali = sali
            ),
        parent2 = dict(birth = datetime.date(year - 40, 1, 1)),
        menage = dict(so = 4),
        )


def couple_deux_enfants(year,sali):
    return dict(
        parent1 = dict(
            birth = datetime.date(year - 40, 1, 1),
            statmarit = 1,
            sali = sali
            ),
        parent2 = dict(
            birth = datetime.date(year - 40, 1, 1),
            statmarit = 1,
            ),
        enfants = [
            dict(birth = datetime.date(year - 9, 1, 1)),
            dict(birth = datetime.date(year - 9, 1, 1)),
            ],
        menage = dict(so = 4),
        )


#def make_df(single_entity_kwargs, count, filename = None, show = None):
 
def make_result(year, count, sali, menage):
    single_entity_kwargs = menage(year,sali)
    filename = "{}_{}".format(menage.__name__, year)
    single_entity_kwargs.update(
        dict(
            axes = [
                dict(
                    count = count,
                    max = 1000,
                    min = 0,
                    name = 'loyer',
                    ),
                ],
            period = periods.period('year', year),
            )
        )
#    print filename
#    print single_entity_kwargs
    scenario = base.tax_benefit_system.new_scenario().init_single_entity(**single_entity_kwargs)
    simulation = scenario.new_simulation(debug = True)
    T= average_rate(
        target = simulation.calculate('al'),
        varying = simulation.calculate('loyer'),
    )
    t= marginal_rate(
            target = simulation.calculate('al'),
            varying = simulation.calculate('loyer'),
        )
    df1 = pd.DataFrame({"t": t,
                       })
    df2= pd.DataFrame({"T": T,
                       "loyer":simulation.calculate('loyer'),
                        "al":simulation.calculate('al')/12,
                       })
    N = count-1
    df = pd.concat([df2[0:N], df1],axis = 1)
    df['sal']="Salaire imposable = {}".format(sali)    
    return df
    
def scatter(df,sali):
    return Scatter(
        x=df["loyer"], y=df["al"],
        name = "Salaire imposable = {}".format(sali),
    )
def make_df_final(year, count, sali0,sali1,sali2, menage = menage):
    df1 = make_result(year = 2011, count = 100, sali = sali0, menage = menage)
    df2= make_result(year = 2011, count = 100, sali = sali1, menage = menage)
    df3 = make_result(year = 2011, count = 100, sali = sali2, menage = menage)
    return df1,df2,df3

def make_df_final2(year, count, sali0,sali1,sali2, menage = menage):
    df1 = make_result(year = 2011, count = 100, sali = sali0, menage = menage)
    df2= make_result(year = 2011, count = 100, sali = sali1, menage = menage)
    df3 = make_result(year = 2011, count = 100, sali = sali2, menage = menage)
    return pd.concat([df1,df2,df3])


if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(level = logging.ERROR, stream = sys.stdout)

    sali0 = 0
    sali1=5000
    sali2= 10000

    df_celib = make_df_final2(year = 2011, count = 100, sali0=sali0,sali1=sali1,sali2=sali2, menage = celibataire)

    graph_celib = ggplot(aes(x='loyer', y='al',color = 'sal'),data=df_celib) + \
        geom_line() + xlab("Loyer mensuel") + ylab("Allocation logement mensuelle") +\
        ggtitle("2010") 
    print graph_celib
    ggsave(graph_celib, file="length.pdf")

    df_celib0,df_celib0,df_celib = make_df_final(year = 2011, count = 100, sali0=sali0,sali1=sali1,sali2=sali2, menage = celibataire)
    df_parent_isole0,df_parent_isole1,df_parent_isole2 = make_df_final(year = 2011, count = 100, sali0=sali0,sali1=sali1,sali2=sali2, menage = parent_isole)
    
    celib0= scatter(df_celib0,sali0)
    celib1= scatter(df_celib1,sali1)
    celib2= scatter(df_celib2,sali2)

    parent_isole0= scatter(df_parent_isole0,sali0)
    parent_isole1= scatter(df_parent_isole1,sali1)
    parent_isole2= scatter(df_parent_isole2,sali2)
    
    data = Data([celib0,celib1,celib2,parent_isole0,parent_isole1,parent_isole2])
    layout = Layout(
        xaxis=XAxis(
            title = 'Loyer mensuel'
            ),
        yaxis=YAxis(
            title = 'Allocation logement mensuelle'
            )
        )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='line-style')

# En ggplot : 
