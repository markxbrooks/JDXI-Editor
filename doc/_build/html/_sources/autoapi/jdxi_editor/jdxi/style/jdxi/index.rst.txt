jdxi_editor.jdxi.style.jdxi
===========================

.. py:module:: jdxi_editor.jdxi.style.jdxi

.. autoapi-nested-parse::

   This module defines the `Style` class, which centralizes all style configurations
   for the JD-Xi Manager application. It includes color definitions, dimensions, fonts,
   and styles for buttons, sliders, tabs, labels, and other UI elements.

   .. attribute:: Colors

      TITLE_TEXT (str): Color for title text.
      BACKGROUND (str): Main background color.
      BACKGROUND_PRESSED (str): Background color when a button is pressed.
      BUTTON_BACKGROUND (str): Background color for buttons.
      FOREGROUND (str): Main foreground color.
      ACCENT (str): Primary red accent color.
      ACCENT_HOVER (str): Hover color for accent elements.
      ACCENT_ANALOG (str): Blue accent color for analog components.
      ACCENT_ANALOG_HOVER (str): Hover color for analog accent elements.
      BORDER (str): Border color for UI elements.
      SLIDER_HANDLE (str): Color of the slider handle.
      SLIDER_HANDLE_BORDER (str): Border color of the slider handle.
      SLIDER_GROOVE (str): Color of the slider groove.
      ACCENT_PRESSED (str): Color of the accent when pressed.
      ACCENT_ANALOG_PRESSED (str): Color of the analog accent when pressed.

   .. attribute:: Dimensions

      BUTTON_ROUND_RADIUS (int): Radius for round buttons.
      BUTTON_RECT_RADIUS (int): Radius for rectangular buttons.
      BUTTON_BORDER_WIDTH (int): Border width for buttons.
      HANDLE_SIZE (str): Size of slider handles.
      GROOVE_WIDTH (str): Width of the slider groove.
      ICON_SIZE (int): Default icon size.
      TAB_BUTTON_RECT_RADIUS (int): Radius for tab buttons.

   .. attribute:: Fonts

      FONT_FAMILY (str): Default font family.
      FONT_SIZE (str): Default font size.

   .. attribute:: Button Styles

      JDXI_BUTTON_ROUND: Standard round button style.
      JDXI_BUTTON_ROUND_SELECTED: Style for selected round buttons.
      JDXI_BUTTON_ROUND_ACTIVE: Style for active round buttons.
      JDXI_BUTTON_ROUND_SMALL: Small round button style.
      JDXI_BUTTON_RECT: Standard rectangular button style.
      JDXI_BUTTON_RECT_SELECTED: Style for selected rectangular buttons.
      JDXI_BUTTON_RECT_ACTIVE: Style for active rectangular buttons.
      JDXI_BUTTON_RECT_ANALOG: Rectangular button style for analog components.
      JDXI_BUTTON_ANALOG_ACTIVE: Active analog button style.
      JDXI_BUTTON_WAVEFORM: Button style for waveform selection.
      JDXI_BUTTON_WAVEFORM_ANALOG: Button style for analog waveform selection.

   .. attribute:: Tab Styles

      JDXI_TABS: Standard tab button styles.
      JDXI_TABS_ANALOG: Tab button styles for analog components.
      JDXI_TABS_DRUMS: Tab button styles for drum components.

   .. attribute:: Editor Styles

      JDXI_EDITOR: Style for the main editor UI.
      JDXI_EDITOR_ANALOG: Style for the analog editor UI.

   .. attribute:: Additional Styles

      JDXI: General application styling.
      JDXI_ADSR: Styling for ADSR envelope sliders.
      JDXI_LABEL_SUB: Sub-label text style.
      JDXI_LABEL: Standard label style.
      JDXI_KEYBOARD_DRUM_LABELS: Style for drum labels in the keyboard section.
      JDXI_INSTRUMENT_TITLE_LABEL: Style for instrument title labels.
      JDXI_LABEL_SYNTH_PART: Style for synthesizer part labels.
      JDXI_LABEL_ANALOG_SYNTH_PART: Style for analog synthesizer part labels.
      JDXI_DRUM_GROUP: Style for drum group UI elements.
      JDXI_PATCH_MANAGER: Styles specific to the patch manager.
      JDXI_PARTIAL_SWITCH: Style for partial switch elements.
      JDXI_PARTIALS_PANEL: Styling for the panel displaying partials.
      JDXI_DEBUGGER: Styles for the debugger window.
      JDXI_SEQUENCER: Styling for the sequencer UI.
      JDXI_PARTS_SELECT: Style for part selection elements.



Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.style.jdxi.JDXiStyle


Module Contents
---------------

.. py:class:: JDXiStyle

   Central style definitions for JD-Xi Manager


   .. py:attribute:: TRACK_LABEL_WIDTH
      :value: 70



   .. py:attribute:: TRACK_BUTTON_WIDTH
      :value: 20



   .. py:attribute:: TRACK_SPINBOX_WIDTH
      :value: 40



   .. py:attribute:: PWM_WIDGET_HEIGHT
      :value: 250



   .. py:attribute:: ADSR_PLOT_WIDTH
      :value: 300



   .. py:attribute:: ADSR_PLOT_HEIGHT
      :value: 200



   .. py:attribute:: INSTRUMENT_IMAGE_WIDTH
      :value: 350



   .. py:attribute:: TITLE_TEXT
      :value: '#FFFFFF'



   .. py:attribute:: BACKGROUND
      :value: '#000000'



   .. py:attribute:: BACKGROUND_PRESSED
      :value: '#666666'



   .. py:attribute:: BUTTON_BACKGROUND
      :value: '#222222'



   .. py:attribute:: BUTTON_BACKGROUND_PRESSED
      :value: '#333333'



   .. py:attribute:: FOREGROUND
      :value: '#FFFFFF'



   .. py:attribute:: PADDING
      :value: 1



   .. py:attribute:: SPACING
      :value: 10



   .. py:attribute:: ICON_PIXMAP_SIZE
      :value: 30



   .. py:attribute:: TRACK_ICON_PIXMAP_SIZE
      :value: 50



   .. py:attribute:: BUTTON_PADDING
      :value: 1



   .. py:attribute:: ACCENT
      :value: '#FF2200'



   .. py:attribute:: ACCENT_HOVER
      :value: '#FF2200'



   .. py:attribute:: ACCENT_ANALOG
      :value: '#00A0E9'



   .. py:attribute:: ACCENT_ANALOG_HOVER
      :value: '#00A0E9'



   .. py:attribute:: BORDER
      :value: '#333333'



   .. py:attribute:: SLIDER_HANDLE
      :value: '#000000'



   .. py:attribute:: SLIDER_HANDLE_BORDER
      :value: '#666666'



   .. py:attribute:: SLIDER_GROOVE
      :value: '#666666'



   .. py:attribute:: SLIDER_NEON
      :value: '#ff1a1a'



   .. py:attribute:: SLIDER_NEON_GRADIENT_STOP
      :value: '#660000'



   .. py:attribute:: SLIDER_NEON_ANALOG
      :value: '#1a1aff'



   .. py:attribute:: SLIDER_NEON_GRADIENT_STOP_ANALOG
      :value: '#000066'



   .. py:attribute:: ACCENT_PRESSED
      :value: '#FF6666'



   .. py:attribute:: ACCENT_ANALOG_PRESSED
      :value: '#417ffa'



   .. py:attribute:: BUTTON_ROUND_RADIUS
      :value: 15



   .. py:attribute:: BUTTON_RECT_RADIUS
      :value: 6



   .. py:attribute:: BUTTON_BORDER_WIDTH
      :value: 4



   .. py:attribute:: HANDLE_SIZE
      :value: '6px'



   .. py:attribute:: GROOVE_WIDTH
      :value: '2px'



   .. py:attribute:: ICON_SIZE
      :value: 20



   .. py:attribute:: TAB_BUTTON_RECT_RADIUS
      :value: 6



   .. py:attribute:: MAX_RULER_HEIGHT
      :value: 200



   .. py:attribute:: TRACK_HEIGHT_MINIMUM
      :value: 40



   .. py:attribute:: FONT_RED
      :value: '#d51e35'



   .. py:attribute:: FONT_FAMILY
      :value: 'Segoe UI'



   .. py:attribute:: FONT_SIZE_MAIN_TABS
      :value: '14px'



   .. py:attribute:: FONT_WEIGHT_BOLD
      :value: 'bold'



   .. py:attribute:: FONT_WEIGHT_NORMAL
      :value: 'normal'



   .. py:attribute:: GREY
      :value: '#CCCCCC'



   .. py:attribute:: BUTTON_ROUND
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #000000;
                         border: 4px solid #333333;
                         border-radius: 15px;
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                         font-size: 12px;
                         padding: 4px;
                     }
                     QPushButton:hover {
                         background-color: #FF2200;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #FF2200);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #666666;
                         border: 4px solid #FF6666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BORDER_PRESSED
      :value: '#2D2D2D'



   .. py:attribute:: BUTTON_ROUND_SELECTED
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #000000;
                         border: 4px solid #333333;
                         border-radius: 15px;
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                         font-size: 12px;
                         padding: 4px;
                     }
                     QPushButton:hover {
                         background-color: #FF2200;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #FF2200);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #666666;
                         border: 4px solid #FF6666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BUTTON_ROUND_ACTIVE
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #222222;
                         border: 4px solid #FF2200;
                         border-radius: 15px;
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                         font-size: 12px;
                         padding: 4px;
                     }
                     QPushButton:hover {
                         background-color: #FF2200;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #FF2200);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #666666;
                         border: 4px solid #FF6666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BUTTON_ROUND_SMALL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #333333;
                         border: 1px solid black;
                         border-radius: 10px;
                         color: #AAAAAA;
                         font-family: "Segoe UI";
                         font-size: 10px;
                         padding: 1px;
                     }
                     QPushButton:hover {
                         background-color: #FF2200;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #FF2200);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #666666;
                         border: 1px solid #FF6666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BUTTON_RECT
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #000000;
                         border: 4px solid #333333;
                         border-radius: 6px;
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                         font-size: 12px;
                         padding: 4px;
                     }
                     QPushButton:hover {
                         background-color: #FF2200;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #FF2200);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #666666;
                         border: 4px solid #FF6666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BUTTON_RECT_SELECTED
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #000000;
                         border: 4px solid #333333;
                         border-radius: 6px;
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                         font-size: 12px;
                         padding: 4px;
                     }
                     QPushButton:hover {
                         background-color: #FF2200;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #FF2200);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #666666;
                         border: 4px solid #FF6666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BUTTON_RECT_ACTIVE
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #222222;
                         border: 4px solid #FF2200;
                         border-radius: 6px;
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                         font-size: 12px;
                         padding: 4px;
                     }
                     QPushButton:hover {
                         background-color: #FF2200;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #FF2200);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #666666;
                         border: 4px solid #FF6666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BUTTON_RECT_ANALOG
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #000000;
                         border: 4px solid #00A0E9;
                         border-radius: 6px;
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                         font-size: 12px;
                         padding: 4px;
                     }
                     QPushButton:hover {
                         background-color: #00A0E9;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #00A0E9);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #666666;
                         border: 4px solid #FF6666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BUTTON_ANALOG_ACTIVE
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #222222;
                         border: 4px solid #00A0E9;
                         border-radius: 6px;
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                         font-size: 12px;
                         padding: 4px;
                     }
                     QPushButton:hover {
                         background-color: #00A0E9;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #00A0E9);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #666666;
                         border: 4px solid #417ffa;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BUTTON_WAVEFORM
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #222222;
                         border: 4px solid #666666;
                         border-radius: 3px;
                         color: #CCCCCC;
                         font-family: "Segoe UI";
                         font-size: 10px;
                         padding: 1px;
                     }
                     QPushButton:hover {
                         background-color: #444444;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #444444);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #333333;
                         border: 4px solid #FF6666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: BUTTON_WAVEFORM_ANALOG
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QPushButton {
                         font-family: Segoe UI;
                         background-color: #222222;
                         border: 4px solid #666666;
                         border-radius: 3px;
                         color: #CCCCCC;
                         font-family: "Segoe UI";
                         font-size: 10px;
                         padding: 1px;
                     }
                     QPushButton:hover {
                         background-color: #444444;
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                         stop:0 #660000, stop:1 #444444);
                     }
                     QPushButton:border_pressed, QPushButton:checked {
                         background-color: #333333;
                         border: 4px solid #00A0E9;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: CREDITS_LABEL_STYLE
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     /* QLabels */
                         QLabel {
                             font-family: Segoe UI;
                             color: 'black';
                             background: #FFFFFF;
                     }
                     """

      .. raw:: html

         </details>




   .. py:attribute:: EDITOR
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QWidget {
                     font-family: Segoe UI;
                     background-color: #000000;
                     color: #FFFFFF;
                     font-family: "Segoe UI";
                     font-size: 10px;
                     padding: 1px;
                 }
                        QGroupBox {
                      font-family: Segoe UI;
                      width: 200px;
                      border: none;
                      border-top: 1px solid #FF2200;
                      margin: 1px;
                      padding: 1px;
                  }
                 /* Groove (Track) */
                 QSlider::groove:vertical {
                     font-family: Segoe UI;
                     background: #111; /* Dark background */
                     width: 6px;
                     border-radius: 3px;
                 }
         
                 /* Handle (Knob) */
                 QSlider::handle:vertical {
                     background: black;
                     border: 2px solid #ff1a1a; /* Neon red border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -8px;
                     margin-bottom: 2px;
                     margin-top: 1px;
                     border-radius: 5px;
                 }
                 /* Handle (Knob) */
                 QSlider::handle:vertical:disabled {
                     background: black;
                     border: 2px solid #333333; /* grey border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -10px;
                     border-radius: 5px;
                 }
                 /* greyed out groove */
                 QSlider::sub-page:vertical:disabled {
                     background: #333333;
                     border-radius: 3px;
                 }
         
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical:disabled:hover {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
         
                 /* Unfilled portion */
                 QSlider::add-page:vertical {
                     font-family: Segoe UI;
                     background: #222;
                     border-radius: 3px;
                 }
         
                 /* Tick Marks (Small dashes on both sides) */
                 QSlider::tick-mark {
                     background: #ff1a1a;
                     width: 4px;
                     height: 2px;
                     border-radius: 1px;
                     margin-left: -8px;
                     margin-right: 8px;
                 }
                 QSlider::horizontal {
                     margin-left: 6px;
                     margin-right: 6x;
                 }
         
                 /* Handle Hover Effect */
                 QSlider::handle:vertical:hover {
                     border: 2px solid #ff3333;
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                      stop:0 #660000, stop:1 #ff1a1a);
                 }
                 /* Spin Box */
                 QSpinBox, QDoubleSpinBox {
                     background-color: #222;
                     border: 1px solid #ff1a1a;
                     border-radius: 3px;
                     padding: 1px;
                     margin: -2px;
                     color: #ff1a1a;
                 }
         
                 QGroupBox {
                     font-family: Segoe UI;
                     border: none;
                     border-top: 1px solid #FF2200;
                     border-radius: 3px;
                     margin-top: 1px;
                     width: 200px;
                     padding: 1px;
                 }
                 
                 QPushButton {
                     width: 100px;
                 }
                 
                 QGroupBox[adsr="true"] {
                     min-height: 300px;  /* Reduced height for horizontal layout */
                     width: 200px;
                 }
         
                 QSlider::handle:vertical {
                     background: #000000;
                     border: 2px solid #666666;
                     margin: 1px 0;
                     border-radius: 4px;
                 }
         
                 QSlider::handle:vertical:hover {
                     border-color: #FF2200;
                 }
         
                 QGroupBox::title {
                     subcontrol-origin: margin;
                     subcontrol-position: top center;
                     padding: 0 1px;
                     color: #FFFFFF;
                     font-weight: normal;
                 }
         
                 QPushButton {
                     font-family: Segoe UI;
                     background-color: #000000;
                     border: 1px solid #FF2200;
                     border-radius: 3px;
                     padding: 1px;
                     color: #FFFFFF;
                 }
         
                 QPushButton:hover, QPushButton:checked {
                     background-color: #FF2200;
                     color: #000000;
                 }
         
                 QComboBox, QScrollBar {
                     font-family: Segoe UI;
                     background-color: #000000;
                     border: 1px solid #FF2200;
                     border-radius: 3px;
                     padding: 1px;
                     color: #FFFFFF;
                 }
                 QComboBox {
                     width: 100px;
                 }
                 QComboBox:disabled {
                     color: #333333;
                 }
         
                 QScrollBar::handle {
                     background: #666666;
                     border-radius: 3px;
                 }
         
                 QScrollBar::handle:hover {
                     border: 2px solid #FF2200;
                 }
         
                 QSlider::groove:horizontal {
                     background: #666666;
                     height: 6px;
                     border-radius: 2px;
                 }
         
                 QSlider::handle:horizontal{
                     background: #000000;
                     border: 3px solid #ff1a1a; /* Neon red border */
                     width: 8px;  /* More rectangular */
                     height: 2px;  
                     margin: -6px;
                     padding: 1px;
                     border-radius: 4px;
                 }
                 QSlider::handle:disabled{
                     background: #000000;
                     border: 2px solid #333333; /* grey border */
                     width: 8px;  /* More rectangular */
                     height: 2px;  
                     margin: -6px;
                     padding: 1px;
                     border-radius: 4px;
                 }
                 /* Unfilled portion */
                 QSlider::add-page:horizontal {
                     background: #222;
                     border-radius: 3px;
                 }
                 QSlider::handle:vertical {
                     background: #000000;
                     border: 2px solid #666666;
                     width: 18px;
                     height: 12px;
                     margin: -9px 0;
                     border-radius: 9px;
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
                 QSlider::handle:vertical:disabled{
                     background: #000000;
                     border: 2px solid #333333; /* grey border */
                     width: 18px;  /* More rectangular */
                     height: 12px;  
                     margin: -9px;
                     border-radius: 4px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:horizontal {
                     background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:horizontal:disabled {
                     background: #333333;
                     border-radius: 3px;
                 }
         
                 /* Unfilled portion */
                 QSlider::add-page:horizontal {
                     background: #222;
                     border-radius: 3px;
                 }
                 /* QLabels */
                 QLabel {
                     color: #FFFFFF;
                     font-family: Segoe UI;
                 }
                 QSlider::horizontal {
                     margin-left: 5px;
                     margin-right: 5px;
                 }
                 QLabel { width: 100px; }
             """

      .. raw:: html

         </details>




   .. py:attribute:: EDITOR_ANALOG
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QWidget {
                     font-family: Segoe UI;
                     background-color: #000000;
                     color: #FFFFFF;
                     font-family: "Segoe UI";
                     font-size: 10px;
                     padding: 1px;
                 }
                        QGroupBox {
                      font-family: Segoe UI;
                      width: 200px;
                      border: none;
                      border-top: 1px solid #00A0E9;
                      margin: 1px;
                      padding: 1px;
                  }
                 /* Groove (Track) */
                 QSlider::groove:vertical {
                     font-family: Segoe UI;
                     background: #111; /* Dark background */
                     width: 6px;
                     border-radius: 3px;
                 }
         
                 /* Handle (Knob) */
                 QSlider::handle:vertical {
                     background: black;
                     border: 2px solid #ff1a1a; /* Neon red border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -8px;
                     margin-bottom: 2px;
                     margin-top: 1px;
                     border-radius: 5px;
                 }
                 /* Handle (Knob) */
                 QSlider::handle:vertical:disabled {
                     background: black;
                     border: 2px solid #333333; /* grey border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -10px;
                     border-radius: 5px;
                 }
                 /* greyed out groove */
                 QSlider::sub-page:vertical:disabled {
                     background: #333333;
                     border-radius: 3px;
                 }
         
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical:disabled:hover {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
         
                 /* Unfilled portion */
                 QSlider::add-page:vertical {
                     font-family: Segoe UI;
                     background: #222;
                     border-radius: 3px;
                 }
         
                 /* Tick Marks (Small dashes on both sides) */
                 QSlider::tick-mark {
                     background: #ff1a1a;
                     width: 4px;
                     height: 2px;
                     border-radius: 1px;
                     margin-left: -8px;
                     margin-right: 8px;
                 }
                 QSlider::horizontal {
                     margin-left: 6px;
                     margin-right: 6x;
                 }
         
                 /* Handle Hover Effect */
                 QSlider::handle:vertical:hover {
                     border: 2px solid #ff3333;
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                      stop:0 #660000, stop:1 #ff1a1a);
                 }
                 /* Spin Box */
                 QSpinBox, QDoubleSpinBox {
                     background-color: #222;
                     border: 1px solid #ff1a1a;
                     border-radius: 3px;
                     padding: 1px;
                     margin: -2px;
                     color: #ff1a1a;
                 }
         
                 QGroupBox {
                     font-family: Segoe UI;
                     border: none;
                     border-top: 1px solid #00A0E9;
                     border-radius: 3px;
                     margin-top: 1px;
                     width: 200px;
                     padding: 1px;
                 }
                 
                 QPushButton {
                     width: 100px;
                 }
                 
                 QGroupBox[adsr="true"] {
                     min-height: 300px;  /* Reduced height for horizontal layout */
                     width: 200px;
                 }
         
                 QSlider::handle:vertical {
                     background: #000000;
                     border: 2px solid #666666;
                     margin: 1px 0;
                     border-radius: 4px;
                 }
         
                 QSlider::handle:vertical:hover {
                     border-color: #00A0E9;
                 }
         
                 QGroupBox::title {
                     subcontrol-origin: margin;
                     subcontrol-position: top center;
                     padding: 0 1px;
                     color: #FFFFFF;
                     font-weight: normal;
                 }
         
                 QPushButton {
                     font-family: Segoe UI;
                     background-color: #000000;
                     border: 1px solid #00A0E9;
                     border-radius: 3px;
                     padding: 1px;
                     color: #FFFFFF;
                 }
         
                 QPushButton:hover, QPushButton:checked {
                     background-color: #00A0E9;
                     color: #000000;
                 }
         
                 QComboBox, QScrollBar {
                     font-family: Segoe UI;
                     background-color: #000000;
                     border: 1px solid #00A0E9;
                     border-radius: 3px;
                     padding: 1px;
                     color: #FFFFFF;
                 }
                 QComboBox {
                     width: 100px;
                 }
                 QComboBox:disabled {
                     color: #333333;
                 }
         
                 QScrollBar::handle {
                     background: #666666;
                     border-radius: 3px;
                 }
         
                 QScrollBar::handle:hover {
                     border: 2px solid #00A0E9;
                 }
         
                 QSlider::groove:horizontal {
                     background: #666666;
                     height: 6px;
                     border-radius: 2px;
                 }
         
                 QSlider::handle:horizontal{
                     background: #000000;
                     border: 3px solid #1a1aff; /* Neon red border */
                     width: 8px;  /* More rectangular */
                     height: 2px;  
                     margin: -6px;
                     padding: 1px;
                     border-radius: 4px;
                 }
                 QSlider::handle:disabled{
                     background: #000000;
                     border: 2px solid #333333; /* grey border */
                     width: 8px;  /* More rectangular */
                     height: 2px;  
                     margin: -6px;
                     padding: 1px;
                     border-radius: 4px;
                 }
                 /* Unfilled portion */
                 QSlider::add-page:horizontal {
                     background: #222;
                     border-radius: 3px;
                 }
                 QSlider::handle:vertical {
                     background: #000000;
                     border: 2px solid #666666;
                     width: 18px;
                     height: 12px;
                     margin: -9px 0;
                     border-radius: 9px;
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #000066, stop:1 #1a1aff);
                     border-radius: 3px;
                 }
                 QSlider::handle:vertical:disabled{
                     background: #000000;
                     border: 2px solid #333333; /* grey border */
                     width: 18px;  /* More rectangular */
                     height: 12px;  
                     margin: -9px;
                     border-radius: 4px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:horizontal {
                     background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                  stop:0 #000066, stop:1 #1a1aff);
                     border-radius: 3px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:horizontal:disabled {
                     background: #333333;
                     border-radius: 3px;
                 }
         
                 /* Unfilled portion */
                 QSlider::add-page:horizontal {
                     background: #222;
                     border-radius: 3px;
                 }
                 /* QLabels */
                 QLabel {
                     color: #FFFFFF;
                     font-family: Segoe UI;
                 }
                 QSlider::horizontal {
                     margin-left: 5px;
                     margin-right: 5px;
                 }
                 QLabel { width: 100px; }
             """

      .. raw:: html

         </details>




   .. py:attribute:: EDITOR_TITLE_LABEL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         font-size: 16px;
                         font-weight: bold;
                     """

      .. raw:: html

         </details>




   .. py:attribute:: INSTRUMENT
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QMainWindow {
                         background-color: black;
                     }
                     QWidget {
                         font-family: Segoe UI;
                         margin: 0px;
                         padding: 0px;
                         background-color: black;
                         color: white;
                     }
                     QMenuBar {
                         background-color: black;
                         color: white;
                     }
                     QMenuBar::item:selected {
                         background-color: #333333;
                     }
                     QMenu {
                         background-color: black;
                         color: white;
                     }
                     QMenu::item:selected {
                         background-color: #333333;
                     }
                     QGroupBox {
                         font-family: Segoe UI;
                         border: none;
                         border-top: 1px solid #333333;
                         margin: 1px;
                         padding: 1px;
                     }
                     QGroupBox::title {
                         font-family: Segoe UI;
                         subcontrol-origin: margin;
                         subcontrol-position: top center;
                         padding: 0 1px;
                         background-color: black;
                     }
                     QLabel {
                         background-color: transparent;
                         color: white;
                     }
                     QStatusBar {
                         background-color: black;
                         color: "#FF2200";
                     }
                     QSlider {
                         margin-bottom: 2px;
                         margin-top: 2px;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: INSTRUMENT_IMAGE_LABEL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QLabel {
                             height: 150px;
                             background-color: transparent;
                             border: none;
                         }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: LOG_VIEWER
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QMainWindow {
                         background-color: #2E2E2E;
                     }
                     QWidget {
                         background-color: #2E2E2E;
                         color: #FFFFFF;
                         font-family: 'Myriad Pro';
                     }
                     QTextEdit {
                         background-color: #1A1A1A;
                         color: #FFFFFF;
                         border: 1px solid #FF0000;
                         border-radius: 3px;
                         padding: 5px;
                         font-family: 'Consolas';
                     }
                     QPushButton {
                         background-color: #3D3D3D;
                         color: #FFFFFF;
                         border: 1px solid #FF0000;
                         border-radius: 3px;
                         padding: 5px 15px;
                         font-family: 'Myriad Pro';
                     }
                     QPushButton:hover {
                         background-color: #4D4D4D;
                         border: 1px solid #FF3333;
                     }
                     QPushButton:pressed {
                         background-color: #2D2D2D;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: MIDI_MESSAGE_MONITOR
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QTextEdit {
                         font-family: monospace;
                         background-color: #1E1E1E;
                         color: #FFFFFF;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: MIXER_LABEL_ANALOG
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         font-size: 16px;
                         font-weight: bold;
                         color: #00A0E9;
                     """

      .. raw:: html

         </details>




   .. py:attribute:: MIXER_LABEL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QLabel {
                         font-family: Segoe UI;
                         font-size: 16px;
                         font-weight: bold;
                         color: #FF2200;
                         }
             """

      .. raw:: html

         </details>




   .. py:attribute:: PROGRAM_PRESET_GROUPS
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """            
                  QGroupBox {
                          font-family: Segoe UI;
                          width: 300px;
                          border: none;
                          border-top: 1px solid #FF2200;
                          margin: 1px;
                          padding: 1px;
                      }"""

      .. raw:: html

         </details>




   .. py:attribute:: PROGRAM_PRESET_GROUP_WIDTH
      :value: 300



   .. py:attribute:: PROGRESS_BAR
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QProgressBar {
                     background-color: #333;
                     color: white;
                     border: 2px solid #444;
                     border-radius: 10px;
                     text-align: center;
                 }
                 QProgressBar::chunk {
                     background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                      stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 10px;
                 }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: SLIDER_VERTICAL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 /* Groove (Track) */
                 QSlider::groove:vertical {
                     font-family: Segoe UI;
                     background: #111; /* Dark background */
                     width: 6px;
                     border-radius: 3px;
                 }
         
                 /* Handle (Knob) */
                 QSlider::handle:vertical {
                     background: black;
                     border: 2px solid #ff1a1a; /* Neon red border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -8px;
                     margin-bottom: 2px;
                     margin-top: 1px;
                     border-radius: 5px;
                 }
                 /* Handle (Knob) */
                 QSlider::handle:vertical:disabled {
                     background: black;
                     border: 2px solid #333333; /* grey border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -10px;
                     border-radius: 5px;
                 }
                 /* greyed out groove */
                 QSlider::sub-page:vertical:disabled {
                     background: #333333;
                     border-radius: 3px;
                 }
         
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical:disabled:hover {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
         
                 /* Unfilled portion */
                 QSlider::add-page:vertical {
                     font-family: Segoe UI;
                     background: #222;
                     border-radius: 3px;
                 }
         
                 /* Tick Marks (Small dashes on both sides) */
                 QSlider::tick-mark {
                     background: #ff1a1a;
                     width: 4px;
                     height: 2px;
                     border-radius: 1px;
                     margin-left: -8px;
                     margin-right: 8px;
                 }
                 QSlider::horizontal {
                     margin-left: 6px;
                     margin-right: 6x;
                 }
         
                 /* Handle Hover Effect */
                 QSlider::handle:vertical:hover {
                     border: 2px solid #ff3333;
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                      stop:0 #660000, stop:1 #ff1a1a);
                 }
                 /* Spin Box */
                 QSpinBox, QDoubleSpinBox {
                     background-color: #222;
                     border: 1px solid #ff1a1a;
                     border-radius: 3px;
                     padding: 1px;
                     margin: -2px;
                     color: #ff1a1a;
                 }
                 /* QLabels */
                 QLabel {
                     color: "#d51e35";
                 }
             """

      .. raw:: html

         </details>




   .. py:attribute:: SPLASH_SCREEN
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QWidget {
                     font-family: Segoe UI;
                     background-color: #000000;
                     color: #FFFFFF;
                     font-family: "Segoe UI";
                     font-size: 14px;
                     padding: 1px;
                 }
                        QGroupBox {
                      font-family: Segoe UI;
                      width: 200px;
                      border: none;
                      border-top: 1px solid #FF2200;
                      margin: 1px;
                      padding: 1px;
                  }
                 /* Groove (Track) */
                 QSlider::groove:vertical {
                     font-family: Segoe UI;
                     background: #111; /* Dark background */
                     width: 6px;
                     border-radius: 3px;
                 }
         
                 /* Handle (Knob) */
                 QSlider::handle:vertical {
                     background: black;
                     border: 2px solid #ff1a1a; /* Neon red border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -8px;
                     margin-bottom: 2px;
                     margin-top: 1px;
                     border-radius: 5px;
                 }
                 /* Handle (Knob) */
                 QSlider::handle:vertical:disabled {
                     background: black;
                     border: 2px solid #333333; /* grey border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -10px;
                     border-radius: 5px;
                 }
                 /* greyed out groove */
                 QSlider::sub-page:vertical:disabled {
                     background: #333333;
                     border-radius: 3px;
                 }
         
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical:disabled:hover {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
         
                 /* Unfilled portion */
                 QSlider::add-page:vertical {
                     font-family: Segoe UI;
                     background: #222;
                     border-radius: 3px;
                 }
         
                 /* Tick Marks (Small dashes on both sides) */
                 QSlider::tick-mark {
                     background: #ff1a1a;
                     width: 4px;
                     height: 2px;
                     border-radius: 1px;
                     margin-left: -8px;
                     margin-right: 8px;
                 }
                 QSlider::horizontal {
                     margin-left: 6px;
                     margin-right: 6x;
                 }
         
                 /* Handle Hover Effect */
                 QSlider::handle:vertical:hover {
                     border: 2px solid #ff3333;
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                      stop:0 #660000, stop:1 #ff1a1a);
                 }
                 /* Spin Box */
                 QSpinBox, QDoubleSpinBox {
                     background-color: #222;
                     border: 1px solid #ff1a1a;
                     border-radius: 3px;
                     padding: 1px;
                     margin: -2px;
                     color: #ff1a1a;
                 }
         
                 QGroupBox {
                     font-family: Segoe UI;
                     border: none;
                     border-top: 1px solid #FF2200;
                     border-radius: 3px;
                     margin-top: 1px;
                     width: 200px;
                     padding: 1px;
                 }
                 
                 QPushButton {
                     width: 100px;
                 }
                 
                 QGroupBox[adsr="true"] {
                     min-height: 300px;  /* Reduced height for horizontal layout */
                     width: 200px;
                 }
         
                 QSlider::handle:vertical {
                     background: #000000;
                     border: 2px solid #666666;
                     margin: 1px 0;
                     border-radius: 4px;
                 }
         
                 QSlider::handle:vertical:hover {
                     border-color: #FF2200;
                 }
         
                 QGroupBox::title {
                     subcontrol-origin: margin;
                     subcontrol-position: top center;
                     padding: 0 1px;
                     color: #FFFFFF;
                     font-weight: bold;
                 }
         
                 QPushButton {
                     font-family: Segoe UI;
                     background-color: #000000;
                     border: 1px solid #FF2200;
                     border-radius: 3px;
                     padding: 1px;
                     color: #FFFFFF;
                 }
         
                 QPushButton:hover, QPushButton:checked {
                     background-color: #FF2200;
                     color: #000000;
                 }
         
                 QComboBox, QScrollBar {
                     font-family: Segoe UI;
                     background-color: #000000;
                     border: 1px solid #FF2200;
                     border-radius: 3px;
                     padding: 1px;
                     color: #FFFFFF;
                 }
                 QComboBox {
                     width: 100px;
                 }
                 QComboBox:disabled {
                     color: #333333;
                 }
         
                 QScrollBar::handle {
                     background: #666666;
                     border-radius: 3px;
                 }
         
                 QScrollBar::handle:hover {
                     border: 2px solid #FF2200;
                 }
         
                 QSlider::groove:horizontal {
                     background: #666666;
                     height: 6px;
                     border-radius: 2px;
                 }
         
                 QSlider::handle:horizontal{
                     background: #000000;
                     border: 3px solid #ff1a1a; /* Neon red border */
                     width: 8px;  /* More rectangular */
                     height: 2px;  
                     margin: -6px;
                     padding: 1px;
                     border-radius: 4px;
                 }
                 QSlider::handle:disabled{
                     background: #000000;
                     border: 2px solid #333333; /* grey border */
                     width: 8px;  /* More rectangular */
                     height: 2px;  
                     margin: -6px;
                     padding: 1px;
                     border-radius: 4px;
                 }
                 /* Unfilled portion */
                 QSlider::add-page:horizontal {
                     background: #222;
                     border-radius: 3px;
                 }
                 QSlider::handle:vertical {
                     background: #000000;
                     border: 2px solid #666666;
                     width: 18px;
                     height: 12px;
                     margin: -9px 0;
                     border-radius: 9px;
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
                 QSlider::handle:vertical:disabled{
                     background: #000000;
                     border: 2px solid #333333; /* grey border */
                     width: 18px;  /* More rectangular */
                     height: 12px;  
                     margin: -9px;
                     border-radius: 4px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:horizontal {
                     background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:horizontal:disabled {
                     background: #333333;
                     border-radius: 3px;
                 }
         
                 /* Unfilled portion */
                 QSlider::add-page:horizontal {
                     background: #222;
                     border-radius: 3px;
                 }
                 /* QLabels */
                 QLabel {
                     color: #FFFFFF;
                     font-family: Segoe UI;
                 }
                 QSlider::horizontal {
                     margin-left: 5px;
                     margin-right: 5px;
                 }
                 QLabel { width: 100px; }
             """

      .. raw:: html

         </details>




   .. py:attribute:: SPLITTER
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                          QSplitter::handle {
                              background-color: #444;
                              border: 1px solid #666;
                          }
                          QSplitter::handle:vertical {
                              height: 6px;
                          }
                          QSplitter::handle:horizontal {
                              width: 6px;
                          }
                      """

      .. raw:: html

         </details>




   .. py:attribute:: TABS
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         QTabBar::tab {
                         font-family: Segoe UI;
                         background: #000000;
                         color: white;
                         padding: 1px 1px;
                         margin: 1px;
                         border: 2px solid #666666;
                         border-radius: 6px;
                         font-family: "Segoe UI";
                         font-size: 12px;
                     }
         
                     QTabBar::tab:selected {
                         font-family: Segoe UI;
                         background: #222222;
                         color: white;
                         border: 2px solid #FF2200;
                         font-family: "Segoe UI";
                         font-size: 12px;
                     }
         
                     QTabBar::tab:hover {
                         background: #222222;
                         border: 2px solid #ff9999;
                         font-family: "Segoe UI";
                         font-size: 12px;
                     }
                     QTabWidget {
                         font-family: Segoe UI;
                         border: none
                     }
                     QTabWidget::pane {
                         border: none;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: TABS_ANALOG
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         QTabBar::tab {
                         font-family: Segoe UI;
                         background: #000000;
                         color: white;
                         padding: 1px 1px;
                         margin: 1px;
                         border: 2px solid #666666;
                         border-radius: 6px;
                         font-family: "Segoe UI";
                         font-size: 12px;
                     }
         
                     QTabBar::tab:selected {
                         font-family: Segoe UI;
                         background: #222222;
                         color: white;
                         border: 2px solid #00A0E9;
                         font-family: "Segoe UI";
                         font-size: 12px;
                     }
         
                     QTabBar::tab:hover {
                         background: #00A0C1;
                         border: 2px solid #00A0E9;
                         font-family: "Segoe UI";
                         font-size: 12px;
                     }
                     QTabWidget {
                         font-family: Segoe UI;
                         border: none
                     }
                     QTabWidget::pane {
                         border: none;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: TABS_DRUMS
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         QTabBar::tab {
                         font-family: Segoe UI;
                         background: #000000;
                         color: white;
                         padding: 1px 1px;
                         margin: 1px;
                         border: 2px solid #666666;
                         border-radius: 6px;
                         font-family: "Segoe UI";
                         font-size: 12px;
                     }
         
                     QTabBar::tab:selected {
                         font-family: Segoe UI;
                         background: #222222;
                         color: white;
                         border: 2px solid #ff6666;
                         font-family: "Segoe UI";
                         font-size: 12px;
                     }
         
                     QTabBar::tab:hover {
                         background: #222222;
                         border: 2px solid #ff9999;
                         font-family: "Segoe UI";
                         font-size: 12px;
                     }
                     QTabWidget {
                         font-family: Segoe UI;
                         border: none
                     }
                     QTabWidget::pane {
                         border: none;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: TABS_MAIN_EDITOR
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         QTabBar::tab {
                         font-family: Segoe UI;
                         background: #000000;
                         color: white;
                         padding: 1px 1px;
                         margin: 1px;
                         border: 2px solid #666666;
                         border-radius: 6px;
                         font-family: "Segoe UI";
                         font-size: 14px;
                     }
         
                     QTabBar::tab:selected {
                         font-family: Segoe UI;
                         background: #222222;
                         color: white;
                         border: 2px solid #ff6666;
                         font-family: "Segoe UI";
                         font-size: 14px;
                     }
         
                     QTabBar::tab:hover {
                         background: #222222;
                         border: 2px solid #ff9999;
                         font-family: "Segoe UI";
                         font-size: 14px;
                     }
                     QTabWidget {
                         font-family: Segoe UI;
                         border: none
                     }
                     QTabWidget::pane {
                         border: none;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: SLIDER
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QSlider::handle:horizontal{
                         background: #000000;
                         border: 3px solid #ff1a1a; /* Neon red border */
                         width: 8px;  /* More rectangular */
                         height: 2px;  
                         margin: -6px;
                         padding: 1px;
                         border-radius: 4px;
                     }
                     QSlider::handle:disabled{
                         background: #000000;
                         border: 2px solid #333333; /* grey border */
                         width: 8px;  /* More rectangular */
                         height: 2px;  
                         margin: -6px;
                         padding: 1px;
                         border-radius: 4px;
                     }
                     /* Unfilled portion */
                     QSlider::add-page:horizontal {
                         background: #222;
                         border-radius: 3px;
                     }
                     QSlider::handle:vertical {
                         background: #000000;
                         border: 2px solid #666666;
                         width: 18px;
                         height: 12px;
                         margin: -9px 0;
                         border-radius: 9px;
                     }
                     QSlider::handle:vertical:disabled{
                         background: #000000;
                         border: 2px solid #333333; /* grey border */
                         width: 18px;  /* More rectangular */
                         height: 12px;  
                         margin: -9px;
                         border-radius: 4px;
                     }
                     /* Glowing effect when moving */
                     QSlider::sub-page:horizontal {
                         background: qlineargradient(x1:1, y1:0, x2:0, y2:0, 
                                      stop:0 #660000, stop:1 #ff1a1a);
                         border-radius: 3px;
                     }
                     /* Glowing effect when moving */
                     QSlider::sub-page:horizontal:disabled {
                         background: #333333;
                         border-radius: 3px;
                     }
         
                     /* Unfilled portion */
                     QSlider::add-page:horizontal {
                         background: #222;
                         border-radius: 3px;
                     }
                     /* QLabels */
                     QLabel {
                         color: #FF2200;
                     }
                     QSlider::horizontal {
                         margin-left: 5px;
                         margin-right: 5px;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: SLIDER_DISABLED
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         QSlider::handle:horizontal{
                         background: #000000;
                         border: 3px solid #333333; /* Neon red border */
                         width: 8px;  /* More rectangular */
                         height: 2px;  
                         margin: -6px;
                         padding: 1px;
                         border-radius: 4px;
                     }
                     QSlider::handle:disabled{
                         background: #000000;
                         border: 2px solid #333333; /* grey border */
                         width: 8px;  /* More rectangular */
                         height: 2px;  
                         margin: -6px;
                         padding: 1px;
                         border-radius: 4px;
                     }
                     /* Unfilled portion */
                     QSlider::add-page:horizontal {
                         background: #222;
                         border-radius: 3px;
                     }
                     QSlider::handle:vertical {
                         background: #000000;
                         border: 2px solid #333333;
                         width: 18px;
                         height: 12px;
                         margin: -9px 0;
                         border-radius: 9px;
                     }
                     QSlider::handle:vertical:disabled{
                         background: #000000;
                         border: 2px solid #333333; /* grey border */
                         width: 18px;  /* More rectangular */
                         height: 12px;  
                         margin: -9px;
                         border-radius: 4px;
                     }
                     /* Glowing effect when moving */
                     QSlider::sub-page:horizontal {
                         background: qlineargradient(x1:1, y1:0, x2:0, y2:0, 
                                      stop:0 #660000, stop:1 #ff1a1a);
                         border-radius: 3px;
                     }
                     /* Glowing effect when moving */
                     QSlider::sub-page:horizontal:disabled {
                         background: #333333;
                         border-radius: 3px;
                     }
         
                     /* Unfilled portion */
                     QSlider::add-page:horizontal {
                         background: #222;
                         border-radius: 3px;
                     }
                     /* QLabels */
                     QLabel {
                         color: #FF2200;
                     }
                     QSlider::horizontal {
                         margin-left: 5px;
                         margin-right: 5px;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: TRANSPARENT
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QMainWindow, QWidget, QMenuBar {
                     background-color: transparent;
                     color: "#d51e35";
                 }
                 QSlider {
                     border: #333333;
                 }
                 QPushButton {
                     background-color: transparent;
                     border: 1px solid red;
                     color: "#d51e35";
                 }
                 QPushButton:hover {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                     stop:0 #660000, stop:1 #ff1a1a);
                 }
                 QStatusBar {
                     background-color: transparent;
                     color: "#d51e35";
                 }
             """

      .. raw:: html

         </details>




   .. py:attribute:: TRANSPARENT_WHITE
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QMainWindow, QWidget, QMenuBar {
                     background-color: transparent;
                     color: "#d51e35";
                 }
                 QLabel {
                     background-color: transparent;
                     color: "white";
                 }
                 QPushButton {
                     background-color: transparent;
                     border: 1px solid red;
                     color: "#d51e35";
                 }
                 QPushButton:hover {
                     background-color: rgba(255, 0, 0, 30);
                 }
                 QStatusBar {
                     background-color: transparent;
                     color: "#d51e35";
                 }
             """

      .. raw:: html

         </details>




   .. py:attribute:: ADSR_ANALOG
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QGroupBox {
                      font-family: Segoe UI;
                      width: 300px;
                      border: none;
                      border-top: 1px solid #00A0E9;
                      margin: 1px;
                      padding: 1px;
                  }
                 /* Groove (Track) */
                 QSlider::groove:vertical {
                     font-family: Segoe UI;
                     background: #111; /* Dark background */
                     width: 6px;
                     border-radius: 3px;
                     border-radius: 3px;
                     border-radius: 3px;
                 }
         
                 /* Handle (Knob) */
                 QSlider::handle:vertical {
                     background: black;
                     border: 2px solid #1a1aff; /* Neon blue border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -10px;
                     margin-bottom: 2px;
                     margin-top: 2px;
                     border-radius: 5px;
                     padding: 1px;
                 }
         
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #000066, stop:1 #1a1aff);
                     border-radius: 3px;
                 }
                 /* Handle (Knob) */
                 QSlider::handle:vertical:disabled {
                     background: black;
                     border: 2px solid #333333; /* grey border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -10px;
                     border-radius: 5px;
                 }
                 /* greyed out groove */
                 QSlider::sub-page:vertical:disabled {
                     background: #333333;
                     border-radius: 3px;
                 }
         
                 /* Unfilled portion */
                 QSlider::add-page:vertical {
                     background: #222;
                     border-radius: 3px;
                 }
         
                 /* Tick Marks (Small dashes on both sides) */
                 QSlider::tick-mark {
                     background: #1a1aff;
                     width: 4px;
                     height: 2px;
                     border-radius: 1px;
                     margin-left: 2px;
                     margin-right: 2px;
                 }
         
                 /* Handle Hover Effect */
                 QSlider::handle:vertical:hover {
                     border: 2px solid #3333ff;
                 }
                 /* Spin Box */
                 QSpinBox, QDoubleSpinBox {
                     background-color: #222;
                     border: 1px solid #00A0E9;
                     border-radius: 3px;
                     padding: 1px;
                     margin: -2px;
                     width: 40px;
                     color: #00A0E9;
                 }
                 /* QLabels */
                 QLabel {
                     color: #00A0E9;
                 }
             """

      .. raw:: html

         </details>




   .. py:attribute:: ADSR
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                  QGroupBox {
                      font-family: Segoe UI;
                      width: 200px;
                      border: none;
                      border-top: 1px solid #FF2200;
                      margin: 1px;
                      padding: 1px;
                  }
                 /* Groove (Track) */
                 QSlider::groove:vertical {
                     font-family: Segoe UI;
                     background: #111; /* Dark background */
                     width: 6px;
                     border-radius: 3px;
                 }
         
                 /* Handle (Knob) */
                 QSlider::handle:vertical {
                     background: black;
                     border: 2px solid #ff1a1a; /* Neon red border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -8px;
                     margin-bottom: 2px;
                     margin-top: 1px;
                     border-radius: 5px;
                 }
                 /* Handle (Knob) */
                 QSlider::handle:vertical:disabled {
                     background: black;
                     border: 2px solid #333333; /* grey border */
                     width: 10px;  /* More rectangular */
                     height: 10px;  
                     margin: -10px;
                     border-radius: 5px;
                 }
                 /* greyed out groove */
                 QSlider::sub-page:vertical:disabled {
                     background: #333333;
                     border-radius: 3px;
                 }
         
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
                 /* Glowing effect when moving */
                 QSlider::sub-page:vertical:disabled:hover {
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                     border-radius: 3px;
                 }
         
                 /* Unfilled portion */
                 QSlider::add-page:vertical {
                     font-family: Segoe UI;
                     background: #222;
                     border-radius: 3px;
                 }
         
                 /* Tick Marks (Small dashes on both sides) */
                 QSlider::tick-mark {
                     background: #ff1a1a;
                     width: 4px;
                     height: 2px;
                     border-radius: 1px;
                     margin-left: -8px;
                     margin-right: 8px;
                 }
                 QSlider::horizontal {
                     margin-left: 6px;
                     margin-right: 6x;
                 }
         
                 /* Handle Hover Effect */
                 QSlider::handle:vertical:hover {
                     border: 2px solid #ff3333;
                     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                      stop:0 #660000, stop:1 #ff1a1a);
                 }
                 /* Spin Box */
                 QSpinBox, QDoubleSpinBox {
                     background-color: #222;
                     border: 1px solid #ff1a1a;
                     border-radius: 3px;
                     padding: 1px;
                     margin: -2px;
                     color: #ff1a1a;
                 }
                 /* QLabels */
                 QLabel {
                     color: "#d51e35";
                 }
             """

      .. raw:: html

         </details>




   .. py:attribute:: ADSR_DISABLED
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QSlider {
                         font-family: Segoe UI;
                     }
                     QLabel {
                         font-family: Segoe UI;
                     }
                     /* Groove (Track) */
                     QSlider::groove:vertical {
                         background: #111; /* Dark background */
                         width: 6px;
                         border-radius: 3px;
                     }
         
                     /* Handle (Knob) */
                     QSlider::handle:vertical {
                         background: black;
                         border: 2px solid #333333; /* Neon red border */
                         width: 10px;  /* More rectangular */
                         height: 10px;  
                         margin: -8px;
                         margin-bottom: 2px;
                         margin-top: 2px;
                         border-radius: 5px;
                     }
                     /* Handle (Knob) */
                     QSlider::handle:vertical:disabled {
                         background: black;
                         border: 2px solid #333333; /* grey border */
                         width: 10px;  /* More rectangular */
                         height: 10px;  
                         margin: -10px;
                         border-radius: 5px;
                     }
                     /* greyed out groove */
                     QSlider::sub-page:vertical:disabled {
                         background: #333333;
                         border-radius: 3px;
                     }
         
                     /* Glowing effect when moving */
                     QSlider::sub-page:vertical {
                         font-family: Segoe UI;
                         background: #333333;
                         border-radius: 3px;
                     }
         
                     /* Unfilled portion */
                     QSlider::add-page:vertical {
                         background: #222;
                         border-radius: 3px;
                     }
         
                     /* Tick Marks (Small dashes on both sides) */
                     QSlider::tick-mark {
                         background: #333333;
                         width: 4px;
                         height: 2px;
                         border-radius: 1px;
                         margin-left: -8px;
                         margin-right: 8px;
                     }
                     QSlider::horizontal {
                         margin-left: 6px;
                         margin-right: 6x;
                     }
         
                     /* Handle Hover Effect */
                     QSlider::handle:vertical:hover {
                         border: 2px solid #ff1a1a;
                     }
                     /* Spin Box */
                     QSpinBox, QDoubleSpinBox {
                         background-color: #222;
                         border: 1px solid #ff1a1a;
                         border-radius: 3px;
                         padding: 1px;
                         margin: -2px;
                         color: #ff1a1a;
                     }
                     /* QLabels */
                     QLabel {
                         color: "#d51e35";
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: ADSR_PLOT
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QWidget {
                     background-color: #333333;
                 }
             """

      .. raw:: html

         </details>




   .. py:attribute:: COMBO_BOX
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
             QComboBox {
                 font-family: Segoe UI;
                 background-color: #000000;
                 border: 1px solid #FF2200;
                 border-radius: 3px;
                 padding: 1px;
                 color: #FFFFFF;
             }
         
             /* Style for the dropdown button */
             QComboBox::drop-down {
                 border: none;
                 width: 20px;
                 height: 20px;
             }
         
             /* Custom small down arrow */
             QComboBox::down-arrow {
                 width: 16px; /* Adjust arrow size */
                 height: 10px;
             }
         
             /* Custom small up arrow (if needed for editable combobox) */
             QComboBox::up-arrow {
                 width: 16px; /* Adjust arrow size */
                 height: 10px;
             }
         
             /* Scrollbar styling */
             QScrollBar:vertical {
                 background: black;
                 border: 2px solid #ff4500;
                 width: 20px;
                 border-radius: 5px;
             }
             """

      .. raw:: html

         </details>




   .. py:attribute:: COMBO_BOX_ANALOG
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QComboBox {
                     font-family: Segoe UI;
                     background-color: #000000;
                     border: 1px solid #00A0E9;
                     border-radius: 3px;
                     padding: 1px;
                     color: #FFFFFF;
                 }
         
                 /* Style for the dropdown button */
                 QComboBox::drop-down {
                     border: none;
                     width: 20px;
                     height: 20px;
                 }
         
                 /* Custom small down arrow */
                 QComboBox::down-arrow {
                     width: 16px; /* Adjust arrow size */
                     height: 10px;
                 }
         
                 /* Custom small up arrow (if needed for editable combobox) */
                 QComboBox::up-arrow {
                     width: 16px; /* Adjust arrow size */
                     height: 10px;
                 }
         
                 /* Scrollbar styling */
                 QScrollBar:vertical {
                     background: black;
                     border: 2px solid #ff4500;
                     width: 20px;
                     border-radius: 5px;
                 }
             """

      .. raw:: html

         </details>




   .. py:attribute:: LABEL_SUB
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     font-family: "Segoe UI";
                     font-size: 13px;
                     color: #d51e35;
                     font-weight: bold;
                 """

      .. raw:: html

         </details>




   .. py:attribute:: LABEL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     font-family: "Segoe UI";
                     font-size: 14px;
                     color: #d51e35;
                     font-weight: bold;
                     background: transparent;
                 """

      .. raw:: html

         </details>




   .. py:attribute:: QLABEL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                 QLabel {
                     font-family: "Segoe UI";
                     font-size: 14px;
                     color: #d51e35;
                     font-weight: bold;
                     background: transparent;
                 }
             """

      .. raw:: html

         </details>




   .. py:attribute:: KEYBOARD_DRUM_LABELS
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         QLabel {
                             color: #808080;
                             font-size: 7px;
                             font-family: monospace;
                             padding: 2px;
                             min-width: 30px;
                         }
                     """

      .. raw:: html

         </details>




   .. py:attribute:: INSTRUMENT_TITLE_LABEL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     font-family: Segoe UI;
                     color: #FFBB33;
                     font-size: 16px;
                     font-weight: bold;
                     font-family: "Consolas";
         
                     QGroupBox {
                         height: 60;
                         border: 2px solid black;
                         border-radius: 5px;
                         padding: 1px;
                         margin: 1px;
                         background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                             stop: 0 #321212,
                             stop: 0.3 #331111,
                             stop: 0.5 #551100,
                             stop: 0.7 #331111,
                             stop: 1 #321212
                         );
                     }
                     """

      .. raw:: html

         </details>




   .. py:attribute:: LABEL_SYNTH_PART
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         font-family: "Segoe UI";
                         font-size: 13px;
                         color: "#d51e35";  /* Base red */
                         font-weight: bold;
                     """

      .. raw:: html

         </details>




   .. py:attribute:: LABEL_ANALOG_SYNTH_PART
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         font-family: "Segoe UI";
                         font-size: 13px;
                         color: #00A0E9;  /* Blue for Analog */
                         font-weight: bold;
                     """

      .. raw:: html

         </details>




   .. py:attribute:: DRUM_GROUP
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         QGroupBox {
                         font-family: Segoe UI;
                         width: 50px;
                         height: 60;
                     }
                     """

      .. raw:: html

         </details>




   .. py:attribute:: PATCH_MANAGER
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QMainWindow {
                         background-color: #2E2E2E;
                         font-family: Segoe UI;
                     }
                     QWidget {
                         background-color: #2E2E2E;
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                     }
                     QLineEdit {
                         background-color: #1A1A1A;
                         color: #FFFFFF;
                         border: 1px solid #FF0000;
                         border-radius: 3px;
                         padding: 1px;
                         font-family: 'Consolas';
                     }
                     QPushButton {
                         background-color: #3D3D3D;
                         color: #FFFFFF;
                         border: 1px solid #FF0000;
                         border-radius: 3px;
                         padding: 1px 1px;
                         font-family: "Segoe UI";
                     }
                     QPushButton:hover {
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                         border: 1px solid #FF3333;
                     }
                     QPushButton:pressed {
                         background-color: #2D2D2D;
                     }
                     QLabel {
                         color: #FFFFFF;
                         font-family: "Segoe UI";
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: LABEL_WHEEL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """            
                 QLabel {
                         color: red;
                         font-family: "Segoe UI";
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: PARTIAL_SWITCH
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                         QCheckBox {
                             color: #CCCCCC;
                             font-size: 10px;
                         }
                         QCheckBox::indicator {
                             width: 16px;
                             height: 16px;
                             background: #333333;
                             border: 1px solid #555555;
                             border-radius: 8px;
                         }
                         QCheckBox::indicator:checked {
                             background: #666666;
                             border-color: #FF4444;
                         }
                     """

      .. raw:: html

         </details>




   .. py:attribute:: PARTIALS_PANEL
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """  
                 QGroupBox {
                     font-family: Segoe UI;
                     color: #CCCCCC;
                     height: 60;
                     font-size: 12px;
                     border: 0px;
                     border-top: 2px solid #444444;  /* Only top border */
                     border-radius: 3px;
                     margin-top: 1px;
                     padding: 1px;
                 }
                 QGroupBox::title {
                     subcontrol-origin: margin;
                     subcontrol-position: top center;
                     padding: 0 1px;
                     margin-top: 1px;
                     background-color: #2D2D2D;
                 }
             """

      .. raw:: html

         </details>




   .. py:attribute:: DEBUGGER
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     QMainWindow {
                         background-color: #2E2E2E;
                     }
                     QWidget {
                         background-color: #2E2E2E;
                         color: #FFFFFF;
                         font-family: 'Segoe UI';
                     }
                     QPlainTextEdit {
                         background-color: #1A1A1A;
                         color: #FFFFFF;
                         border: 1px solid #FF0000;
                         border-radius: 3px;
                         padding: 1px;
                         font-family: 'Consolas';
                     }
                     QTextEdit {
                         background-color: #1A1A1A;
                         color: #FFFFFF;
                         border: 1px solid #FF0000;
                         border-radius: 3px;
                         padding: 2px;
                         font-family: 'Consolas';
                     }
                     QPushButton {
                         background-color: #3D3D3D;
                         color: #FFFFFF;
                         border: 1px solid #FF0000;
                         border-radius: 3px;
                         padding: 1px 1px;
                         font-family: "Segoe UI";
                     }
                     QPushButton:hover {
                         background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #660000, stop:1 #ff1a1a);
                         border: 1px solid #FF3333;
                     }
                     QPushButton:pressed {
                         background-color: #666666;
                     }
                 """

      .. raw:: html

         </details>




   .. py:attribute:: SEQUENCER
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     font-family: "Segoe UI";
                     font-size: 14px;
                     color: #d51e35;
                     font-weight: bold;
                     background: transparent;
                 """

      .. raw:: html

         </details>




   .. py:attribute:: PARTS_SELECT
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """
                     font-family: Segoe UI;
                     font-size: 14px;
                     color: #d51e35;
                     font-weight: bold;
                     background: transparent;
                     padding-bottom: 1px;
                 """

      .. raw:: html

         </details>




