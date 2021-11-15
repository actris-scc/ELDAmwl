import graphviz
from zope import component

from ELDAmwl.component.interface import IGraph


def register_graph():
    dot = graphviz.Digraph(comment='ELDAmwl', format='svg')

    component.provideUtility(dot, IGraph)
