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
struct Date {
    char date[0x10];
};

struct DataInfo{
    Date collection_start_date;
    Date collection_end_date;
    u8 nope[2][[color("000000")]];
    u16 num_points;
    u8 nope2[8][[color("000000")]];
    float theta_start;
    u8 nope3[4][[color("000000")]];
    float theta_end;
    u8 nope4[4][[color("000000")]];
    float theta_stepsize;
    u8 nope5[4][[color("000000")]];
    float time_per_step;
    u8 nope6[0x30][[color("000000")]];
    u32 min_cnt;
    u32 max_cnt;
};
DataInfo info @ 0x800;
s32 data[info.num_points] @ 0xA00;

u16 kilo_volt @ 0x13E;
u16 milli_Amp @ 0x140;
float radiation @ 0x142;
float radiation_false @ 0x146;
char comment[0x20] @ 0x70;
char format[0x08] @ 0x00;
char machine[0x08] @ 0x08;
char title[0x20] @ 0x20;
Date date @ 0x10;
```