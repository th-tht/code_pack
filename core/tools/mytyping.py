
from math import inf, log

from typing import Dict, Tuple, List, NewType


FILE_Row = 1000

stream = NewType("stream", str)

Stream_index = NewType("Index of streams", List[stream])

match = NewType("match of streams", Tuple[stream,stream])

Proto_network = NewType("Proto-network", List[match])

Loads = NewType("Loads of heat exchangers", Dict[match, float])

strcuture_expr_SSWS = NewType("structure expression in SSWS", Tuple[int,...])

Stream_structure_SSWS = NewType("Structure of a stream in SSWS", Dict[match, strcuture_expr_SSWS])

HEN_SSWS = NewType("HEN in SSWS", Stream_structure_SSWS)

data = NewType("signal data of stream", dict)

HU = NewType("Usage of hot utilities", float)
TAC = NewType("TAC", float)

Stream_temperature = NewType("stage temperature of streams", Dict[stream, List[float]])

Stream_data = NewType("inlet, outlet, flow rate, etc of streams", Tuple[Dict,...])
Coeffcient_data = NewType("Other data", Tuple[Dict,...])


# picture front
#front = "Arial"
#front = "Times New Roman"
front_dict_large = dict(fontsize=12,  weight = 'bold')
front_dict = dict(fontsize=10, weight = 'bold')



