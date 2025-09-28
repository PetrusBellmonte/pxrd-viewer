# PXRD Viewer

PXRD Viewer is a tool designed to visualize and compare powder X-ray diffraction (PXRD) spectra. It aims to help researchers and analysts easily inspect, overlay, and interpret PXRD data from various sources, facilitating material identification and analysis.

## Features
- Load and display PXRD spectra from supported file formats
- Overlay multiple spectra for direct comparison
- Simple, user-friendly interface for spectrum analysis

## State of the repo
This repos is in currently in active development and NOT ready for production.

## Getting Started
Clone the repository and run `streamlit run App.py`


## Attempt of reading the raw files
```
u32 data[0x1770] @ 0xA00;
char char_array_at_0x00[0x10] @ 0x00;
float btheta_start @ 0x82C;
float dtheta_end @ 0x834;
float d_theta_stepsize @ 0x83C;
u16 num_points @ 0x822;
float time_per_step @ 0x844;
char char_array_at_0x600[0x1F8] @ 0x600;


u16 kilo_volt @ 0x13E;
u16 milli_Amp @ 0x140;
float radiation @ 0x142;








u16 data[0x1387] @ 0x800;
char char_array_at_0x00[0x10] @ 0x00;
float btheta_start @ 0x62C;
float dtheta_end @ 0x634;
float d_theta_stepsize @ 0x63C;
u16 num_points @ 0x622;
float time_per_step @ 0x644;


u16 kilo_volt @ 0x13E;
u16 milli_Amp @ 0x140;
float radiation @ 0x142;
```