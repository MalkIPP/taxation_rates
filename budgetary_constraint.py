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

import pandas as pd


try:
    import plotly.plotly as py
    from plotly.graph_objs import *
    py.sign_in('Python-Demo-Account', 'gwt101uhh0')
except:
    pass

from ggplot import *

from openfisca_core import periods
from openfisca_france.tests import base
from openfisca_core.rates import average_rate, marginal_rate



import rpy2.robjects as robj
import rpy2.robjects.pandas2ri # for dataframe conversion
from rpy2.robjects.packages import importr
# convert the pandas df to an R dataframe
robj.pandas2ri.activate()


# you can even save the output once you like it




def celibataire(year, sali):
    return dict(
        parent1 = dict(birth = datetime.date(year - 40, 1, 1), sali = sali),
        menage = dict(so = 4),
        label = u"Célibataire",
        )


def parent_isole(year, sali):
    return dict(
        parent1 = dict(birth = datetime.date(year - 40, 1, 1), sali = sali),
        enfants = [
            dict(birth = datetime.date(year - 9, 1, 1)),
            ],
        menage = dict(so = 4),
        label = u"Parent isolé",
        )


def couple_sans_enfant(year, sali):
    return dict(
        parent1 = dict(
            birth = datetime.date(year - 40, 1, 1),
            statmarit = 1,
            sali = sali
            ),
        parent2 = dict(birth = datetime.date(year - 40, 1, 1)),
        menage = dict(so = 4),
        label = u"Couple",
        )


def couple_deux_enfants(year, sali):
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
        label = u"Couple avec deux enfants",
        )


def make_result(year, count, sali, menage):
    single_entity_kwargs = menage(year, sali)
    label = single_entity_kwargs.pop("label")
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
    T = average_rate(
        target = simulation.calculate('al'),
        varying = simulation.calculate('loyer'),
    )
    t = marginal_rate(
        target = simulation.calculate('al'),
        varying = simulation.calculate('loyer'),
        )
    df1 = pd.DataFrame({
        "t": t,
        })
    df2 = pd.DataFrame({
        "T": T,
        "loyer": simulation.calculate('loyer'),
        "al": simulation.calculate('al') / 12,
        })
    N = count - 1
    df = pd.concat([df2[0:N], df1], axis = 1)
    df["sal"] = sali
    df["typmen"] = menage.__name__
    df["typmensal"] = "{} et {} euros de salaire imposable".format(label, sali)

#    df[u"Salaire imposable"] = sali
#    df[u"Type de ménage"] = menage.__name__
    return df


#def scatter(df, sali):
#    return Scatter(
#        x = df["loyer"],
#        y = df["al"],
#        name = "Salaire imposable = {}".format(sali),
#    )
#

def make_df_final3(year, count, salis, menages):

    df_list = []
    for menage in menages:
        for sali in salis:
            df = make_result(year = 2011, count = 100, sali = sali, menage = menage)
            df_list.append(df)
    return pd.concat(df_list)


if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(level = logging.ERROR, stream = sys.stdout)

    graph_list = [
        dict(
            menages = [celibataire, parent_isole],
            salis = [0, 10000],
            ),
        dict(
            menages = [couple_sans_enfant, couple_deux_enfants],
            salis = [0, 10000],
            ),
        ]

    for graph, filename in zip(graph_list, ['celib', 'couple']):
        print filename
        print graph
        df = make_df_final3(
            year = 2011, count = 100, salis = graph["salis"], menages = graph["menages"],
            )


    #    max_xy_value = min(df_celib.loyer.max(), df_celib.al.max())
#        max_xy_value = 1000
#        graph = (
#            ggplot(
#                aes(
#                    x = 'loyer',
#                    y = 'al',
#                    color = u"Salaire imposable",
#                    linetype = u"Type de ménage",
#                    ),
#                data = df,
#                ) +
#            geom_line() +
#    #        scale_color_manual(values = ["red"] + ["green"] + ["blue"]) +
#            xlab("Loyer mensuel") +
#            ylab("Allocation logement mensuelle") +
#            xlim(low = 0, high = max_xy_value) +
#            ylim(low = 0, high = max_xy_value) +
#            ggtitle("2010") +
#            theme_matplotlib()
#            )
#        print graph

#
        df_R = robj.conversion.py2ri(df)

        # import graphics devices. This is necessary to shut the graph off
        # otherwise it just hangs and freezes python
        gr = importr('grDevices')

        plotFunc_2 = robj.r("""
        library(ggplot2)
        library(grid)
        function(df, filename){
         max_xy_value = 500
         df$sal <- as.factor(df$sal)
         df$typmen <- as.factor(df$typmen)
         df$typmensal <- as.factor(df$typmensal)
         graph = ggplot(aes(x = loyer, y = al, color = typmensal, linetype = typmensal), data = df) + geom_line() +
         scale_color_manual(values = c("red", "red", "green", "green")) +
         scale_linetype_manual(values = c("solid", "dashed", "solid", "dashed")) +
         xlab("Loyer mensuel") +
         ylab("Allocation logement mensuelle") +
         scale_x_continuous(limits=c(0, max_xy_value), expand = c(0, 0)) +
         scale_y_continuous(limits=c(0, max_xy_value), expand = c(0, 0)) +
         guides(color = guide_legend(ncol=1)) +
         theme_bw() +
         theme(legend.position = "bottom", legend.title = element_blank(),
               legend.key = element_blank()) +
         coord_fixed()
         ggsave(filename, plot = graph, width = 5)
         }
        """)
        plotFunc_2(df_R, "{}.pdf".format(filename))
