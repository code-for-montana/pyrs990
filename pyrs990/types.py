from typing import NewType

EIN = NewType("EIN", str)
"""
An EIN is a tax identification number assigned to a particular
organization. In our case, it is used to join the Annual and BMF
indices.
"""
