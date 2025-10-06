jdxi_editor.midi.nrpn.map
=========================

.. py:module:: jdxi_editor.midi.nrpn.map

.. autoapi-nested-parse::

   Parameter Map



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.nrpn.map.ParameterMap
   jdxi_editor.midi.nrpn.map.NRPNMap
   jdxi_editor.midi.nrpn.map.RPNMap


Module Contents
---------------

.. py:class:: ParameterMap(mapping: Optional[Dict[int, Tuple[int, int]]] = None)

   .. py:attribute:: _map
      :type:  Dict[int, Tuple[int, int]]


   .. py:method:: add_mapping(key: int, msb_lsb_pair: Tuple[int, int]) -> None


   .. py:method:: get(key: int, default: Any = None) -> Any


   .. py:method:: get_lsb(key: int) -> Optional[int]


   .. py:method:: get_msb(key: int) -> Optional[int]


   .. py:method:: __getitem__(key: int) -> Tuple[int, int]


   .. py:method:: __setitem__(key: int, value: Tuple[int, int]) -> None


   .. py:method:: __contains__(key: int) -> bool


   .. py:method:: items() -> ItemsView[int, Tuple[int, int]]


   .. py:method:: __repr__() -> str


.. py:class:: NRPNMap(mapping: Optional[Dict[int, Tuple[int, int]]] = None)

   Bases: :py:obj:`ParameterMap`


.. py:class:: RPNMap(mapping: Optional[Dict[int, Tuple[int, int]]] = None)

   Bases: :py:obj:`ParameterMap`


